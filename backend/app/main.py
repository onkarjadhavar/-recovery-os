"""
FastAPI Application Entrypoint for RecoveryOS
Provides OpenAPI documentation, swagger UI, and high-performance async handlers.
"""
import os
import json
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any

from .core.config import settings
from .core.agent import RecoveryAgent
from .core.evaluator import BenchmarkEvaluator
from .models.schemas import (
    TransactionEvent,
    DecisionTrace,
    BatchBenchmarkResult
)
from .api.routes_razorpay import RazorpayWebhookHandler
from .data.synthetic_generator import generate_synthetic_transactions

app = FastAPI(
    title="RecoveryOS API",
    description="Autonomous AI Revenue Recovery & Policy Guardrail Decision Engine for Razorpay",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "transactions.json")
CACHED_TRANSACTIONS: List[Dict[str, Any]] = []

@app.on_event("startup")
def startup_event():
    global CACHED_TRANSACTIONS
    if not os.path.exists(DATA_PATH):
        CACHED_TRANSACTIONS = generate_synthetic_transactions(20000, DATA_PATH)
    else:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            CACHED_TRANSACTIONS = json.load(f)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "guardrails": {
            "max_auto_recovery_amount": settings.MAX_AUTO_RECOVERY_AMOUNT,
            "max_retry_attempts": settings.MAX_RETRY_ATTEMPTS,
            "min_ai_confidence": settings.MIN_AI_CONFIDENCE,
            "fraud_risk_cutoff": settings.FRAUD_RISK_CUTOFF
        },
        "dataset_size": len(CACHED_TRANSACTIONS)
    }

@app.post("/api/diagnose", response_model=DecisionTrace)
def diagnose_transaction(txn: TransactionEvent):
    return RecoveryAgent.process_event(txn)

@app.post("/api/simulate-preset")
def simulate_preset_scenario(payload: Dict[str, str]):
    scenario_key = payload.get("scenario", "transient_upi")
    mock_webhook = RazorpayWebhookHandler.generate_mock_webhook(scenario_key)
    trace = RazorpayWebhookHandler.parse_and_process_event(mock_webhook)
    return {
        "scenario": scenario_key,
        "mock_webhook_payload": mock_webhook,
        "decision_trace": trace
    }

@app.get("/api/benchmarks", response_model=BatchBenchmarkResult)
def get_benchmarks(sample_size: int = 5000):
    sample = CACHED_TRANSACTIONS[:sample_size] if CACHED_TRANSACTIONS else []
    return BenchmarkEvaluator.run_benchmark(sample)

@app.post("/api/razorpay-webhook", response_model=DecisionTrace)
def handle_razorpay_webhook(
    payload: Dict[str, Any],
    x_razorpay_signature: Optional[str] = Header(None)
):
    return RazorpayWebhookHandler.parse_and_process_event(payload)

@app.get("/api/transactions")
def list_transactions(page: int = 1, limit: int = 25, code: Optional[str] = None):
    filtered = CACHED_TRANSACTIONS
    if code:
        filtered = [t for t in filtered if t.get("failure_code") == code]
    start = (page - 1) * limit
    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "items": filtered[start:start + limit]
    }
