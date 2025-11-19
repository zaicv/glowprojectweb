"""
💰 Finance routes - Money Copilot backend
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body

from config import supabase

router = APIRouter(prefix="/api/finance", tags=["finance"])

CATEGORY_SPLIT = {
    "Entertainment": Decimal("0.14285714"),
    "Groceries & Shopping": Decimal("0.57142857"),
    "Eating Out": Decimal("0.28571429"),
}

EXPENSE_CATEGORIES = list(CATEGORY_SPLIT.keys())
INCOME_CATEGORY = "Income"


def _category_column(category: str) -> str:
    return f"{category.lower().replace(' & ', '_').replace(' ', '_')}_amount"


def _decimal(value: float) -> Decimal:
    return Decimal(str(value))


def _round_currency(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _split_budget(amount: float) -> Dict[str, float]:
    total = _decimal(amount)
    return {name: _round_currency(total * ratio) for name, ratio in CATEGORY_SPLIT.items()}


def _month_bounds(month: Optional[int], year: Optional[int]) -> Dict[str, datetime]:
    now = datetime.utcnow()
    target_month = month or now.month
    target_year = year or now.year
    start = datetime(target_year, target_month, 1)
    if target_month == 12:
        end = datetime(target_year + 1, 1, 1)
    else:
        end = datetime(target_year, target_month + 1, 1)
    return {"start": start, "end": end}


def _summarize_transactions(rows: List[dict]) -> Dict[str, float]:
    summary = {category: 0.0 for category in EXPENSE_CATEGORIES}
    totals = {"spent": 0.0, "income": 0.0}

    for row in rows:
        amount = float(row.get("amount") or 0.0)
        kind = (row.get("kind") or "expense").lower()
        category = row.get("category")

        if kind == "income":
            totals["income"] += amount
        else:
            totals["spent"] += amount
            if category in summary:
                summary[category] += amount

    return {"categories": summary, **totals}


def _build_ai_insights(
    budget: Optional[dict],
    transaction_summary: Dict[str, float],
    bills: List[dict],
) -> List[dict]:
    insights: List[dict] = []
    base_amount = float(budget.get("base_amount", 0)) if budget else 0.0
    spent = transaction_summary.get("spent", 0.0)

    if base_amount > 0:
        percent_used = spent / base_amount
        if percent_used >= 0.9:
            insights.append(
                {
                    "type": "warning",
                    "message": "You've used 90% of this month's budget. Consider pausing non-essential spend.",
                    "action": "Create a guardrail",
                }
            )
        elif percent_used >= 0.75:
            insights.append(
                {
                    "type": "tip",
                    "message": "Spending is trending high. We can trim recurring charges automatically.",
                    "action": "Review subscriptions",
                }
            )

    if budget:
        for category, allocated in CATEGORY_SPLIT.items():
            allocated_amount = float(budget.get(_category_column(category), 0))
            actual = transaction_summary["categories"].get(category, 0.0)
            if allocated_amount > 0 and actual > allocated_amount * 1.15:
                insights.append(
                    {
                        "type": "warning",
                        "message": f"{category} is {((actual / allocated_amount) - 1):.0%} over the plan.",
                        "action": "Adjust allocation",
                    }
                )

    due_soon = [bill for bill in bills if bill.get("days_until_due", 0) <= 3]
    if due_soon:
        insights.append(
            {
                "type": "goal",
                "message": f"{len(due_soon)} bill(s) due within 3 days. Glow can auto-schedule them.",
                "action": "Enable autopay",
            }
        )

    if not insights:
        insights.append(
            {
                "type": "goal",
                "message": "All systems nominal. You're pacing on budget and bills.",
                "action": "Optimize cash cushion",
            }
        )

    return insights


@router.get("/overview")
def get_finance_overview(
    user_id: str = Query(..., description="Supabase user ID"),
    month: Optional[int] = None,
    year: Optional[int] = None,
):
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    bounds = _month_bounds(month, year)
    period_start = bounds["start"].isoformat()
    period_end = bounds["end"].isoformat()
    target_month = bounds["start"].month
    target_year = bounds["start"].year

    budget_resp = (
        supabase.table("finance_budgets")
        .select("*")
        .eq("user_id", user_id)
        .eq("month", target_month)
        .eq("year", target_year)
        .limit(1)
        .execute()
    )
    budget_rows = getattr(budget_resp, "data", []) or []
    budget = budget_rows[0] if budget_rows else None

    tx_resp = (
        supabase.table("finance_transactions")
        .select("*")
        .eq("user_id", user_id)
        .gte("transaction_date", period_start)
        .lt("transaction_date", period_end)
        .order("transaction_date", desc=True)
        .execute()
    )
    transactions = getattr(tx_resp, "data", []) or []

    bills_resp = (
        supabase.table("finance_bills")
        .select("*")
        .eq("user_id", user_id)
        .gte("due_date", datetime.utcnow().date().isoformat())
        .order("due_date", ascending=True)
        .execute()
    )
    bills = getattr(bills_resp, "data", []) or []

    goals_resp = (
        supabase.table("finance_goals")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", ascending=True)
        .execute()
    )
    goals = getattr(goals_resp, "data", []) or []

    tx_summary = _summarize_transactions(transactions)

    for bill in bills:
        due_date = datetime.fromisoformat(bill.get("due_date"))
        bill["days_until_due"] = (due_date.date() - datetime.utcnow().date()).days

    insights = _build_ai_insights(budget, tx_summary, bills)

    return {
        "budget": budget
        or {
            "user_id": user_id,
            "base_amount": 0,
            "month": target_month,
            "year": target_year,
            "entertainment_amount": 0,
            "groceries_shopping_amount": 0,
            "eating_out_amount": 0,
        },
        "transactions": transactions,
        "bills": bills,
        "goals": goals,
        "totals": {
            "income": tx_summary["income"],
            "spent": tx_summary["spent"],
            "category_spend": tx_summary["categories"],
        },
        "insights": insights,
    }


@router.post("/overview")
def get_finance_overview_post(payload: dict = Body(...)):
    user_id = payload.get("user_id")
    month = payload.get("month")
    year = payload.get("year")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    return get_finance_overview(user_id=user_id, month=month, year=year)




@router.post("/budget")
def upsert_budget(payload: dict):
    user_id = payload.get("user_id")
    amount = float(payload.get("amount", 0))
    month = payload.get("month")
    year = payload.get("year")

    if not user_id or amount <= 0:
        raise HTTPException(status_code=400, detail="user_id and amount are required")

    bounds = _month_bounds(month, year)
    target_month = bounds["start"].month
    target_year = bounds["start"].year

    splits = _split_budget(amount)

    row = {
        "user_id": user_id,
        "month": target_month,
        "year": target_year,
        "base_amount": float(amount),
    }
    for name, value in splits.items():
        key = _category_column(name)
        row[key] = value

    result = (
        supabase.table("finance_budgets")
        .upsert(row, on_conflict="user_id,month,year")
        .execute()
    )
    return {"status": "success", "data": row, "supabase": getattr(result, "data", [])}


def _validate_category(category: str, kind: str) -> None:
    if kind == "expense" and category not in EXPENSE_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Category must be one of: {', '.join(EXPENSE_CATEGORIES)}",
        )
    if kind == "income" and category != INCOME_CATEGORY:
        raise HTTPException(
            status_code=400,
            detail="Income transactions must use the 'Income' category",
        )


@router.post("/transactions")
def create_transaction(payload: dict):
    user_id = payload.get("user_id")
    amount = float(payload.get("amount", 0))
    category = payload.get("category")
    payee = payload.get("payee")
    kind = (payload.get("kind") or "expense").lower()
    transaction_date = payload.get("transaction_date") or datetime.utcnow().isoformat()
    notes = payload.get("notes")

    if not user_id or amount <= 0 or not category or not payee:
        raise HTTPException(status_code=400, detail="user_id, payee, amount, category are required")

    _validate_category(category, kind)

    row = {
        "user_id": user_id,
        "payee": payee,
        "amount": amount,
        "category": category,
        "kind": kind,
        "transaction_date": transaction_date,
        "notes": notes,
    }
    result = supabase.table("finance_transactions").insert(row).execute()
    return {"status": "success", "data": getattr(result, "data", row)}


@router.get("/transactions")
def list_transactions(user_id: str = Query(...), limit: int = 50):
    resp = (
        supabase.table("finance_transactions")
        .select("*")
        .eq("user_id", user_id)
        .order("transaction_date", desc=True)
        .limit(limit)
        .execute()
    )
    return getattr(resp, "data", [])


@router.post("/bills")
def create_bill(payload: dict):
    user_id = payload.get("user_id")
    name = payload.get("name")
    amount = float(payload.get("amount", 0))
    due_date = payload.get("due_date")
    category = payload.get("category") or "General"
    autopay_source = payload.get("autopay_source")
    status = payload.get("status") or "upcoming"

    if not user_id or not name or amount <= 0 or not due_date:
        raise HTTPException(status_code=400, detail="user_id, name, amount, due_date required")

    row = {
        "user_id": user_id,
        "name": name,
        "amount": amount,
        "due_date": due_date,
        "category": category,
        "autopay_source": autopay_source,
        "status": status,
    }
    result = supabase.table("finance_bills").insert(row).execute()
    return {"status": "success", "data": getattr(result, "data", row)}


@router.get("/bills")
def list_bills(user_id: str = Query(...)):
    resp = (
        supabase.table("finance_bills")
        .select("*")
        .eq("user_id", user_id)
        .order("due_date", ascending=True)
        .execute()
    )
    return getattr(resp, "data", [])


@router.post("/goals")
def create_goal(payload: dict):
    user_id = payload.get("user_id")
    name = payload.get("name")
    target = payload.get("target_amount")
    current = payload.get("current_amount", 0)
    color = payload.get("color")

    if not user_id or not name or target is None:
        raise HTTPException(status_code=400, detail="user_id, name, target_amount required")

    row = {
        "user_id": user_id,
        "name": name,
        "target_amount": float(target),
        "current_amount": float(current),
        "color": color or "#22c55e",
    }
    result = supabase.table("finance_goals").insert(row).execute()
    return {"status": "success", "data": getattr(result, "data", row)}


@router.patch("/goals/{goal_id}")
def update_goal(goal_id: str, payload: dict):
    current_amount = payload.get("current_amount")
    name = payload.get("name")
    target = payload.get("target_amount")
    color = payload.get("color")

    update_fields = {}
    if current_amount is not None:
        update_fields["current_amount"] = float(current_amount)
    if name is not None:
        update_fields["name"] = name
    if target is not None:
        update_fields["target_amount"] = float(target)
    if color is not None:
        update_fields["color"] = color

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    resp = (
        supabase.table("finance_goals")
        .update(update_fields)
        .eq("id", goal_id)
        .execute()
    )
    return {"status": "success", "data": getattr(resp, "data", [])}


@router.get("/goals")
def list_goals(user_id: str = Query(...)):
    resp = (
        supabase.table("finance_goals")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", ascending=True)
        .execute()
    )
    return getattr(resp, "data", [])
