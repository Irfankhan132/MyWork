from fastapi import APIRouter, Depends
from app.core.auth import get_context, RequestContext

router = APIRouter(tags=["auth-test"])

@router.get("/me")
def me(ctx: RequestContext = Depends(get_context)):
    return {
        "user_id": str(ctx.user.id),
        "email": ctx.user.email,
        "tenant_id": str(ctx.tenant_id),
        "role": ctx.role,
    }
