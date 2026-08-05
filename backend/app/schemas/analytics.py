from datetime import date
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class CashFlowSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    net_cash_flow: Decimal
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CategorySpending(BaseModel):
    category_id: Optional[UUID] = None
    category_name: str
    category_color: Optional[str] = None
    category_icon: Optional[str] = None
    total_amount: Decimal
    percentage: float


class SpendingByCategoryResponse(BaseModel):
    total_spending: Decimal
    categories: List[CategorySpending]
    start_date: Optional[date] = None
    end_date: Optional[date] = None