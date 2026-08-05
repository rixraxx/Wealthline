from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import TransactionType
from app.schemas.category import CategoryResponse


class TransactionBase(BaseModel):
    account_id: UUID
    category_id: Optional[UUID] = None
    amount: Decimal = Field(..., json_schema_extra={"example": 45.99})
    type: TransactionType
    description: Optional[str] = Field(default=None, json_schema_extra={"example": "Trader Joe's groceries"})
    transaction_date: datetime
    transfer_account_id: Optional[UUID] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None