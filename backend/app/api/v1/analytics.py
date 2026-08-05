from datetime import date, datetime, time, timezone
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.category import Category
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.analytics import (
    CashFlowSummary,
    CategorySpending,
    SpendingByCategoryResponse,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _apply_date_range_filter(stmt, start_date: Optional[date], end_date: Optional[date]):
    if start_date:
        start_dt = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc)
        stmt = stmt.where(Transaction.transaction_date >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, time.max).replace(tzinfo=timezone.utc)
        stmt = stmt.where(Transaction.transaction_date <= end_dt)
    return stmt


@router.get("/cash-flow", response_model=CashFlowSummary)
def get_cash_flow_summary(
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculates total income, total expenses, and net cash flow for a date window."""
    stmt = select(
        Transaction.type,
        func.coalesce(func.sum(Transaction.amount), Decimal("0.00")).label("total"),
    ).where(
        Transaction.user_id == current_user.id,
        Transaction.type.in_([TransactionType.INCOME, TransactionType.EXPENSE]),
    )
    stmt = _apply_date_range_filter(stmt, start_date, end_date)
    stmt = stmt.group_by(Transaction.type)

    results = db.execute(stmt).all()
    totals = {row.type: row.total for row in results}

    income = totals.get(TransactionType.INCOME, Decimal("0.00"))
    expense = totals.get(TransactionType.EXPENSE, Decimal("0.00"))
    net = income - expense

    return CashFlowSummary(
        total_income=income,
        total_expense=expense,
        net_cash_flow=net,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/spending-by-category", response_model=SpendingByCategoryResponse)
def get_spending_by_category(
    start_date: Optional[date] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Provides a percentage and numerical breakdown of expense spending grouped by category."""
    stmt = (
        select(
            Transaction.category_id,
            Category.name.label("category_name"),
            Category.color.label("category_color"),
            Category.icon.label("category_icon"),
            func.coalesce(func.sum(Transaction.amount), Decimal("0.00")).label("total_amount"),
        )
        .outerjoin(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.EXPENSE,
        )
    )
    stmt = _apply_date_range_filter(stmt, start_date, end_date)
    stmt = stmt.group_by(
        Transaction.category_id,
        Category.name,
        Category.color,
        Category.icon,
    )

    rows = db.execute(stmt).all()
    total_spending = sum((row.total_amount for row in rows), Decimal("0.00"))

    categories_spending = []
    for row in rows:
        pct = (
            float((row.total_amount / total_spending) * 100)
            if total_spending > Decimal("0.00")
            else 0.0
        )
        categories_spending.append(
            CategorySpending(
                category_id=row.category_id,
                category_name=row.category_name or "Uncategorized",
                category_color=row.category_color,
                category_icon=row.category_icon,
                total_amount=row.total_amount,
                percentage=round(pct, 2),
            )
        )

    # Sort categories by total spending descending
    categories_spending.sort(key=lambda x: x.total_amount, reverse=True)

    return SpendingByCategoryResponse(
        total_spending=total_spending,
        categories=categories_spending,
        start_date=start_date,
        end_date=end_date,
    )