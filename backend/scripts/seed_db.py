import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.account import Account
from app.models.budget import Budget
from app.models.category import Category
from app.models.enums import AccountType, TransactionType
from app.models.transaction import Transaction
from app.models.user import User

# Default Category Specifications
DEFAULT_CATEGORIES = [
    # Expense Categories
    {"name": "Groceries", "type": TransactionType.EXPENSE, "icon": "shopping_cart", "color": "#10B981"},
    {"name": "Dining & Restaurants", "type": TransactionType.EXPENSE, "icon": "restaurant", "color": "#F59E0B"},
    {"name": "Rent & Housing", "type": TransactionType.EXPENSE, "icon": "home", "color": "#EF4444"},
    {"name": "Utilities & Bills", "type": TransactionType.EXPENSE, "icon": "bolt", "color": "#6366F1"},
    {"name": "Transportation & Fuel", "type": TransactionType.EXPENSE, "icon": "directions_car", "color": "#3B82F6"},
    {"name": "Entertainment & Leisure", "type": TransactionType.EXPENSE, "icon": "movie", "color": "#8B5CF6"},
    {"name": "Subscriptions & SaaS", "type": TransactionType.EXPENSE, "icon": "subscriptions", "color": "#EC4899"},
    {"name": "Health & Fitness", "type": TransactionType.EXPENSE, "icon": "favorite", "color": "#14B8A6"},
    # Income Categories
    {"name": "Salary & Wages", "type": TransactionType.INCOME, "icon": "payments", "color": "#10B981"},
    {"name": "Freelance & Consulting", "type": TransactionType.INCOME, "icon": "work", "color": "#06B6D4"},
    {"name": "Investments & Dividends", "type": TransactionType.INCOME, "icon": "trending_up", "color": "#8B5CF6"},
]


def seed_database():
    db = SessionLocal()
    try:
        print("🌱 Seeding database...")

        # 1. Create Demo User
        demo_email = "demo@wealthline.io"
        stmt = select(User).where(User.email == demo_email)
        demo_user = db.scalar(stmt)

        if not demo_user:
            demo_user = User(
                email=demo_email,
                hashed_password=get_password_hash("Wealthline123!"),
                full_name="Demo User",
                is_active=True,
            )
            db.add(demo_user)
            db.flush()
            print(f"  └─ Created Demo User: {demo_email} (Password: Wealthline123!)")
        else:
            print(f"  └─ Demo User ({demo_email}) already exists.")

        # 2. Create Default System Categories (associated with Demo User)
        category_map = {}
        for cat_data in DEFAULT_CATEGORIES:
            stmt = select(Category).where(
                Category.name == cat_data["name"],
                Category.user_id == demo_user.id,
            )
            cat = db.scalar(stmt)
            if not cat:
                cat = Category(
                    name=cat_data["name"],
                    type=cat_data["type"],
                    icon=cat_data["icon"],
                    color=cat_data["color"],
                    user_id=demo_user.id,
                )
                db.add(cat)
                db.flush()
            category_map[cat.name] = cat

        print(f"  └─ Ensured {len(category_map)} categories exist.")

        # 3. Create Sample Accounts
        stmt = select(Account).where(Account.user_id == demo_user.id)
        existing_accounts = db.scalars(stmt).all()

        if not existing_accounts:
            checking = Account(
                name="Main Checking",
                type=AccountType.CHECKING,
                balance=Decimal("4250.00"),
                currency="USD",
                user_id=demo_user.id,
            )
            savings = Account(
                name="High-Yield Savings",
                type=AccountType.SAVINGS,
                balance=Decimal("15000.00"),
                currency="USD",
                user_id=demo_user.id,
            )
            credit_card = Account(
                name="Rewards Credit Card",
                type=AccountType.CREDIT_CARD,
                balance=Decimal("320.50"),
                currency="USD",
                user_id=demo_user.id,
            )
            db.add_all([checking, savings, credit_card])
            db.flush()

            print("  └─ Created sample accounts (Checking, Savings, Credit Card).")

            # 4. Create Sample Transactions
            now = datetime.now(timezone.utc)
            sample_txs = [
                Transaction(
                    user_id=demo_user.id,
                    account_id=checking.id,
                    category_id=category_map["Salary & Wages"].id,
                    amount=Decimal("3500.00"),
                    type=TransactionType.INCOME,
                    description="Bi-weekly Salary Deposit",
                    transaction_date=now - timedelta(days=5),
                ),
                Transaction(
                    user_id=demo_user.id,
                    account_id=checking.id,
                    category_id=category_map["Rent & Housing"].id,
                    amount=Decimal("1400.00"),
                    type=TransactionType.EXPENSE,
                    description="Monthly Apartment Rent",
                    transaction_date=now - timedelta(days=4),
                ),
                Transaction(
                    user_id=demo_user.id,
                    account_id=credit_card.id,
                    category_id=category_map["Groceries"].id,
                    amount=Decimal("142.80"),
                    type=TransactionType.EXPENSE,
                    description="Weekly Groceries - Whole Foods",
                    transaction_date=now - timedelta(days=2),
                ),
                Transaction(
                    user_id=demo_user.id,
                    account_id=credit_card.id,
                    category_id=category_map["Dining & Restaurants"].id,
                    amount=Decimal("56.40"),
                    type=TransactionType.EXPENSE,
                    description="Dinner with friends",
                    transaction_date=now - timedelta(days=1),
                ),
            ]
            db.add_all(sample_txs)

            # 5. Create Sample Budget
            sample_budget = Budget(
                user_id=demo_user.id,
                category_id=category_map["Groceries"].id,
                amount=Decimal("600.00"),
                start_date=now.replace(day=1).date(),
                end_date=(now.replace(day=28) + timedelta(days=10)).replace(day=1) - timedelta(days=1),
            )
            db.add(sample_budget)
            print("  └─ Added initial sample transactions and monthly grocery budget.")

        db.commit()
        print("✅ Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()