import random
from typing import List, Dict, Any
from app.models import Customer, Supplier, EntityArchetype, SupplierArchetype

def generate_historical_transactions() -> List[Dict[str, Any]]:
    """
    Generates 3-6 months of backdated historical payment events for archetypes.
    """
    transactions = []
    customers = [
        ("cust_1", "Customer A Enterprise", EntityArchetype.RELIABLE, 0.92, 2),
        ("cust_2", "Customer B Logistics", EntityArchetype.AVERAGE, 0.75, 6),
        ("cust_3", "Customer C Retail", EntityArchetype.RISKY, 0.45, 14),
    ]

    for cust_id, name, archetype, on_time_rate, base_delay in customers:
        for i in range(12):  # 12 historical invoices
            is_on_time = random.random() < on_time_rate
            delay = 0 if is_on_time else base_delay + random.randint(1, 5)
            transactions.append({
                "customer_id": cust_id,
                "customer_name": name,
                "archetype": archetype,
                "amount": round(random.uniform(5.0, 15.0), 2),
                "is_on_time": is_on_time,
                "delay_days": delay
            })

    return transactions

def preprocess_customer_history(customer_id: str, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Startup preprocessing step deriving fields for decision engine.
    Derives alpha, beta, on_time_probability, average_delay_days.
    """
    cust_txs = [t for t in transactions if t["customer_id"] == customer_id]
    if not cust_txs:
        return {"alpha": 5, "beta": 2, "on_time_probability": 0.71, "average_delay_days": 4.0}

    on_time = sum(1 for t in cust_txs if t["is_on_time"])
    late = len(cust_txs) - on_time
    delays = [t["delay_days"] for t in cust_txs if not t["is_on_time"]]

    alpha = on_time + 1
    beta = late + 1
    prob = round(alpha / (len(cust_txs) + 2), 3)
    avg_delay = round(sum(delays) / max(1, len(delays)), 1) if delays else 0.0

    return {
        "alpha": alpha,
        "beta": beta,
        "on_time_probability": prob,
        "average_delay_days": avg_delay
    }
