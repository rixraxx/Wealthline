from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import TransactionType

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=50, json_schema_extra={"example": "Groceries"})
    type: TransactionType
    icon: Optional[str] = Field(default="shopping_cart", json_schema_extra={"example": "fastfood"})
    color: Optional[str] = Field(default="#000000", json_schema_extra={"example": "#FF5733"})

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: Optional[UUID] = None
    created_at: datetime

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[TransactionType] = None
    icon: Optional[str] = None
    color: Optional[str] = None