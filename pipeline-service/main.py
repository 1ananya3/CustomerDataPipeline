from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, init_db
from models.customer import Customer
from services.ingestion import fetch_all_customers, upsert_customers

app = FastAPI(title="Pipeline Service", version="1.0.0")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "pipeline-service"}


@app.post("/api/ingest")
def ingest(db: Session = Depends(get_db)):
    try:
        customers_data = fetch_all_customers()
        records_processed = upsert_customers(db, customers_data)
        return {"status": "success", "records_processed": records_processed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(Customer).count()
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()

    def serialize(c: Customer) -> dict:
        return {
            "customer_id": c.customer_id,
            "first_name": c.first_name,
            "last_name": c.last_name,
            "email": c.email,
            "phone": c.phone,
            "address": c.address,
            "date_of_birth": str(c.date_of_birth) if c.date_of_birth else None,
            "account_balance": float(c.account_balance) if c.account_balance else None,
            "created_at": str(c.created_at) if c.created_at else None,
        }

    return {
        "data": [serialize(c) for c in customers],
        "total": total,
        "page": page,
        "limit": limit
    }


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "data": {
            "customer_id": customer.customer_id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "date_of_birth": str(customer.date_of_birth) if customer.date_of_birth else None,
            "account_balance": float(customer.account_balance) if customer.account_balance else None,
            "created_at": str(customer.created_at) if customer.created_at else None,
        }
    }
