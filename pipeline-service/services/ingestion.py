import requests
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from models.customer import Customer


FLASK_BASE_URL = "http://mock-server:5000"


def fetch_all_customers() -> list[dict]:
    """Fetch all customers from Flask with auto-pagination."""
    all_customers = []
    page = 1
    limit = 10

    while True:
        resp = requests.get(
            f"{FLASK_BASE_URL}/api/customers",
            params={"page": page, "limit": limit},
            timeout=10
        )
        resp.raise_for_status()
        payload = resp.json()

        data = payload.get("data", [])
        all_customers.extend(data)

        total = payload.get("total", 0)
        if len(all_customers) >= total or not data:
            break

        page += 1

    return all_customers


def parse_customer(raw: dict) -> dict:
    """Parse and coerce raw dict fields to Python types."""
    dob = raw.get("date_of_birth")
    if isinstance(dob, str) and dob:
        dob = date.fromisoformat(dob)

    created_at = raw.get("created_at")
    if isinstance(created_at, str) and created_at:
        created_at = datetime.fromisoformat(created_at)

    balance = raw.get("account_balance")
    if balance is not None:
        balance = Decimal(str(balance))

    return {
        "customer_id": raw.get("customer_id"),
        "first_name": raw.get("first_name"),
        "last_name": raw.get("last_name"),
        "email": raw.get("email"),
        "phone": raw.get("phone"),
        "address": raw.get("address"),
        "date_of_birth": dob,
        "account_balance": balance,
        "created_at": created_at,
    }


def upsert_customers(db: Session, customers_data: list[dict]) -> int:
    """Upsert customers into PostgreSQL. Returns count of records processed."""
    count = 0
    for raw in customers_data:
        parsed = parse_customer(raw)
        existing = db.query(Customer).filter(
            Customer.customer_id == parsed["customer_id"]
        ).first()

        if existing:
            for key, value in parsed.items():
                setattr(existing, key, value)
        else:
            db.add(Customer(**parsed))

        count += 1

    db.commit()
    return count
