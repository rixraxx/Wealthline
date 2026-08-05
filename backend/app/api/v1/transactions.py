import uuid
from datetime import date, datetime, time, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.account import Account
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
    search: Optional[str] = Query(default=None, description="Search in transaction description"),
    start_date: Optional[date] = Query(default=None, description="Filter from start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(default=None, description="Filter up to end date (YYYY-MM-DD)"),
    account_id: Optional[uuid.UUID] = Query(default=None, description="Filter by account ID"),
    category_id: Optional[uuid.UUID] = Query(default=None, description="Filter by category ID"),
    transaction_type: Optional[TransactionType] = Query(
        default=None, alias="type", description="Filter by type (INCOME, EXPENSE, TRANSFER)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List transactions with support for pagination, search, date range, and field filtering."""
    stmt = (
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.user_id == current_user.id)
    )

    # 1. Search filter (case-insensitive substring match)
    if search:
        stmt = stmt.where(Transaction.description.ilike(f"%{search.strip()}%"))

    # 2. Date range filters
    if start_date:
        start_dt = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc)
        stmt = stmt.where(Transaction.transaction_date >= start_dt)
    if end_date:
        end_dt = datetime.combine(end_date, time.max).replace(tzinfo=timezone.utc)
        stmt = stmt.where(Transaction.transaction_date <= end_dt)

    # 3. Specific ID and Enum filters
    if account_id:
        stmt = stmt.where(Transaction.account_id == account_id)
    if category_id:
        stmt = stmt.where(Transaction.category_id == category_id)
    if transaction_type:
        stmt = stmt.where(Transaction.type == transaction_type)

    # 4. Ordering and Pagination
    stmt = (
        stmt.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return db.scalars(stmt).all()


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    tx_in: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch primary account
    stmt = select(Account).where(
        Account.id == tx_in.account_id,
        Account.user_id == current_user.id,
        Account.is_active == True,
    )
    account = db.scalar(stmt)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Primary account not found")

    # Handle balance logic based on type
    if tx_in.type == TransactionType.INCOME:
        account.balance += tx_in.amount
    elif tx_in.type == TransactionType.EXPENSE:
        account.balance -= tx_in.amount
    elif tx_in.type == TransactionType.TRANSFER:
        if not tx_in.transfer_account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="transfer_account_id is required for TRANSFER type transactions",
            )
        target_stmt = select(Account).where(
            Account.id == tx_in.transfer_account_id,
            Account.user_id == current_user.id,
            Account.is_active == True,
        )
        target_account = db.scalar(target_stmt)
        if not target_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target transfer account not found",
            )
        account.balance -= tx_in.amount
        target_account.balance += tx_in.amount

    transaction = Transaction(
        **tx_in.model_dump(),
        user_id=current_user.id,
    )
    db.add(transaction)
    db.commit()

    # Re-fetch with category relationship populated
    res_stmt = (
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(Transaction.id == transaction.id)
    )
    return db.scalar(res_stmt)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Transaction).where(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id,
    )
    tx = db.scalar(stmt)
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    # Revert account balance adjustment
    account_stmt = select(Account).where(Account.id == tx.account_id)
    account = db.scalar(account_stmt)
    if account:
        if tx.type == TransactionType.INCOME:
            account.balance -= tx.amount
        elif tx.type == TransactionType.EXPENSE:
            account.balance += tx.amount
        elif tx.type == TransactionType.TRANSFER and tx.transfer_account_id:
            target_stmt = select(Account).where(Account.id == tx.transfer_account_id)
            target_account = db.scalar(target_stmt)
            account.balance += tx.amount
            if target_account:
                target_account.balance -= tx.amount

    db.delete(tx)
    db.commit()
    return None