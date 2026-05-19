from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean

from app.core.db import Base


class AIProvider(Base):
    __tablename__ = "ai_providers"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # "gemini", "openai", etc.
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
