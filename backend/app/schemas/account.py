from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import AccountType


class AccountBase(BaseModel):
    name: str = Field(..., max_length=100, json_schema_extra={"example": "Chase Checking"})
    type: AccountType
    balance: Decimal = Field(default=Decimal("0.00"), json_schema_extra={"example": 1500.50})
    currency: str = Field(default="USD", max_length=3)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    balance: Optional[Decimal] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime