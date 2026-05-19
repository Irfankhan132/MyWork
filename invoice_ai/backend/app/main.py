from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.tenants import router as tenants_router
from app.routers.users import router as users_router
from app.routers.me import router as me_router
from app.routers.invoices import router as invoices_router
from app.routers.reports import router as reports_router
from app.routers.chat import router as chat_router
from app.routers.usage import router as usage_router
from app.routers.billing import router as billing_router

from app.core.config import settings
from fastapi.responses import RedirectResponse

unit_price = settings.OVERAGE_UNIT_PRICE_MICROS["gemini"]



app = FastAPI(title="Invoice AI API", version="0.1.0")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


app.include_router(health_router)
app.include_router(tenants_router)
app.include_router(users_router)
app.include_router(me_router)
app.include_router(invoices_router)
app.include_router(reports_router)
app.include_router(chat_router)
app.include_router(usage_router)
app.include_router(billing_router)

print(settings.OVERAGE_UNIT_PRICE_MICROS)
print(settings.OVERAGE_CURRENCY)

