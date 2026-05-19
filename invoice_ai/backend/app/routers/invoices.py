from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from pathlib import Path
import shutil

from app.core.db import get_db
from app.core.auth import get_context, RequestContext
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceResponse
from uuid import UUID
from app.agents.ocr_agent import extract_from_file

from app.schemas.invoice import InvoiceResponse, InvoiceDetail, InvoiceUpdate

from app.agents.classification_agent import classify
from app.agents.fraud_agent import fraud_check
from app.agents.compliance_agent import check_compliance
from datetime import datetime, timedelta, timezone
from app.services.token_service import consume_tokens, estimate_tokens_for_text
from fastapi import APIRouter, Depends, HTTPException
from app.services.provider_router import select_provider


router = APIRouter(prefix="/invoices", tags=["invoices"])

STORAGE_DIR = Path("storage")


router = APIRouter()

@router.post("/{invoice_id}/process", response_model=InvoiceResponse)
def process_invoice(
    invoice_id: UUID,
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    inv = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == ctx.tenant_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if inv.status not in ("uploaded", "failed"):
        raise HTTPException(
            status_code=400,
            detail=f"Invoice status is '{inv.status}', cannot process"
        )

    # provider_id = "gemini"
    endpoint = "invoice.process"
    provider_id = select_provider(
        db,
        user_id=str(ctx.user.id),
        endpoint=endpoint,
        preferred_provider="gemini",
    )

    try:
        inv.status = "processing"
        db.commit()
        db.refresh(inv)

        # ------------------------------------------------------------
        # 1) OCR / Extraction
        # ------------------------------------------------------------
        extracted = extract_from_file(inv.storage_path)
        inv.vendor = extracted.vendor
        inv.invoice_number = extracted.invoice_number
        inv.invoice_date = extracted.invoice_date
        inv.currency = extracted.currency
        inv.subtotal = extracted.subtotal
        inv.tax = extracted.tax
        inv.total = extracted.total
        inv.extracted_data = extracted.raw

        # Build text_hint for AI agents + token estimation
        text_hint = ""
        if extracted.raw and isinstance(extracted.raw, dict):
            text_hint = extracted.raw.get("text_preview") or ""

        # ------------------------------------------------------------
        # BILLING (Extra): charge based on OCR text size
        # ------------------------------------------------------------
        extra_tokens = estimate_tokens_for_text(text_hint or inv.filename or "")
        extra_charge = consume_tokens(
            db,
            user_id=str(ctx.user.id),
            tenant_id=str(ctx.tenant_id),
            endpoint=endpoint,
            tokens=extra_tokens,
            provider_id=provider_id,
        )
        if not inv.agent_results:
            inv.agent_results = {}
            
        inv.agent_results["provider_selected"] = provider_id
        inv.agent_results["billing"] = extra_charge

        db.commit()
        db.refresh(inv)

        # ------------------------------------------------------------
        # 2) Agent 1: Classification
        # ------------------------------------------------------------
        class_res = classify(text_hint=text_hint or None, filename=inv.filename)
        inv.invoice_type = class_res.invoice_type
        inv.language = class_res.language

        # ------------------------------------------------------------
        # 3) Agent 2: Fraud detection
        # ------------------------------------------------------------
        duplicate_invoice_number = False
        if inv.invoice_number:
            dup = (
                db.query(Invoice)
                .filter(
                    Invoice.tenant_id == ctx.tenant_id,
                    Invoice.invoice_number == inv.invoice_number,
                    Invoice.id != inv.id,
                )
                .first()
            )
            duplicate_invoice_number = dup is not None

        suspicious_similarity = False
        if inv.vendor and inv.total is not None:
            recent_similar = (
                db.query(Invoice)
                .filter(
                    Invoice.tenant_id == ctx.tenant_id,
                    Invoice.vendor == inv.vendor,
                    Invoice.total == inv.total,
                    Invoice.id != inv.id,
                    Invoice.created_at >= (datetime.now(timezone.utc) - timedelta(days=7)),
                )
                .first()
            )
            suspicious_similarity = recent_similar is not None

        fraud_res = fraud_check(
            duplicate_invoice_number=duplicate_invoice_number,
            suspicious_similarity=suspicious_similarity,
            total=float(inv.total) if inv.total else None,
            vendor=inv.vendor,
            invoice_number=inv.invoice_number,
        )
        inv.risk_score = fraud_res.risk_score
        inv.risk_flags = {"flags": fraud_res.flags}

        # ------------------------------------------------------------
        # 4) Agent 3: Compliance
        # ------------------------------------------------------------
        comp_res = check_compliance(
            currency=inv.currency,
            tax=float(inv.tax) if inv.tax else None
        )
        inv.compliance_status = comp_res.status

        # ------------------------------------------------------------
        # Store all agent results (MERGE, don’t overwrite billing)
        # ------------------------------------------------------------
        inv.agent_results = {
            **(inv.agent_results or {}),
            "classification": class_res.details,
            "fraud": fraud_res.details | {"flags": fraud_res.flags, "risk_score": fraud_res.risk_score},
            "compliance": comp_res.details,
        }

        inv.status = "processed"
        db.commit()
        db.refresh(inv)

    except HTTPException as e:
        # if quota exhausted, reset so user can retry after upgrade
        if e.status_code == 402:
            inv.status = "uploaded"
            inv.extracted_data = {
                "error": str(e.detail),
                "source": "process_invoice",
                "code": 402
            }
            db.commit()
            db.refresh(inv)
        raise

    except Exception as e:
        inv.status = "failed"
        inv.extracted_data = {"error": str(e), "source": "process_invoice"}
        db.commit()
        db.refresh(inv)

    return InvoiceResponse(
        id=inv.id,
        tenant_id=inv.tenant_id,
        filename=inv.filename,
        content_type=inv.content_type,
        status=inv.status,
        created_at=inv.created_at,
    )
  
    
@router.post("/{invoice_id}/reprocess", response_model=InvoiceResponse)
def reprocess_invoice(
    invoice_id: UUID,
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    inv = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == ctx.tenant_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # allow reprocessing even if processed
    inv.status = "failed"  # a safe way to reuse the same pipeline rules
    db.commit()
    db.refresh(inv)

    # call the same logic as process by simply continuing:
    # easiest: just duplicate the process logic OR extract it into a function later
    # For now, simplest is to tell user to call /process again after setting failed:
    return InvoiceResponse(
        id=inv.id,
        tenant_id=inv.tenant_id,
        filename=inv.filename,
        content_type=inv.content_type,
        status=inv.status,
        created_at=inv.created_at,
    )

    
@router.get("/{invoice_id}", response_model=InvoiceDetail)
def get_invoice(
    invoice_id: UUID,
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    inv = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == ctx.tenant_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return InvoiceDetail(
        id=inv.id,
        tenant_id=inv.tenant_id,
        filename=inv.filename,
        content_type=inv.content_type,
        storage_path=inv.storage_path,
        vendor=inv.vendor,
        invoice_number=inv.invoice_number,
        invoice_date=inv.invoice_date,
        currency=inv.currency,
        subtotal=float(inv.subtotal) if inv.subtotal is not None else None,
        tax=float(inv.tax) if inv.tax is not None else None,
        total=float(inv.total) if inv.total is not None else None,
        status=inv.status,
        extracted_data=inv.extracted_data,
        notes=inv.notes,
        created_at=inv.created_at,
    )

@router.patch("/{invoice_id}", response_model=InvoiceDetail)
def update_invoice(
    invoice_id: UUID,
    payload: InvoiceUpdate,
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    inv = (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id, Invoice.tenant_id == ctx.tenant_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    data = payload.model_dump(exclude_unset=True)

    # Apply only provided fields
    for key, value in data.items():
        setattr(inv, key, value)

    db.commit()
    db.refresh(inv)

    return InvoiceDetail(
        id=inv.id,
        tenant_id=inv.tenant_id,
        filename=inv.filename,
        content_type=inv.content_type,
        storage_path=inv.storage_path,
        vendor=inv.vendor,
        invoice_number=inv.invoice_number,
        invoice_date=inv.invoice_date,
        currency=inv.currency,
        subtotal=float(inv.subtotal) if inv.subtotal is not None else None,
        tax=float(inv.tax) if inv.tax is not None else None,
        total=float(inv.total) if inv.total is not None else None,
        status=inv.status,
        extracted_data=inv.extracted_data,
        notes=inv.notes,
        created_at=inv.created_at,
    )
    


@router.post("/upload", response_model=InvoiceResponse, status_code=201)
def upload_invoice(
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    # Create tenant folder
    tenant_folder = STORAGE_DIR / str(ctx.tenant_id)
    tenant_folder.mkdir(parents=True, exist_ok=True)

    # Generate unique stored filename
    safe_name = Path(file.filename).name  # strips any path tricks
    stored_name = f"{uuid4()}__{safe_name}"
    stored_path = tenant_folder / stored_name

    # Save file to disk
    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create invoice DB row
    inv = Invoice(
        tenant_id=ctx.tenant_id,
        filename=safe_name,
        content_type=file.content_type,
        storage_path=str(stored_path),
        status="uploaded",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)

    return InvoiceResponse(
        id=inv.id,
        tenant_id=inv.tenant_id,
        filename=inv.filename,
        content_type=inv.content_type,
        status=inv.status,
        created_at=inv.created_at,
    )


@router.get("/", response_model=list[InvoiceResponse])
def list_invoices(
    ctx: RequestContext = Depends(get_context),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Invoice)
        .filter(Invoice.tenant_id == ctx.tenant_id)
        .order_by(Invoice.created_at.desc())
        .all()
    )

    return [
        InvoiceResponse(
            id=r.id,
            tenant_id=r.tenant_id,
            filename=r.filename,
            content_type=r.content_type,
            status=r.status,
            created_at=r.created_at,
        )
        for r in rows
    ]
