import enum
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, Enum, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimeStampMixin


class Category(str, enum.Enum):
    PHONE = "phone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    ACCESSORIES = "accessories"


class Product(Base, TimeStampMixin):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price > 0", name="price_positive"),
        CheckConstraint("stock >= 0", name="stock_non_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    brand: Mapped[str] = mapped_column(String(255), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    description: Mapped[str] = mapped_column(Text, default="", server_default="")
    specs: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default="{}"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="true"
    )
    warrenty_months: Mapped[int] = mapped_column(
        Integer, default=12, server_default="12"
    )
    category: Mapped[Category] = mapped_column(
        Enum(
            Category,
            native_enum=False,
            length=20,
            values_callable=lambda e: [m.value for m in e],
        ),
        index=True,
    )

    @property
    def in_stock(self) -> bool:
        return self.stock > 0
