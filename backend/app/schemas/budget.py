from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.category import CategoryResponse


class BudgetBase(BaseModel):
    category_id: Optional[UUID] = None
    amount: Decimal = Field(..., json_schema_extra={"example": 500.00})
    start_date: date
    end_date: date


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    category: Optional[CategoryResponse] = None

class BudgetUpdate(BaseModel):
    category_id: Optional[UUID] = None
    amount: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None