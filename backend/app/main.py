"""
FastAPI Application Entrypoint for RecoveryOS
Provides OpenAPI documentation, swagger UI, and high-performance async handlers.
"""
import os
import json
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
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

def get_cached_transactions() -> List[Dict[str, Any]]:
    global CACHED_TRANSACTIONS
    if not CACHED_TRANSACTIONS:
        if os.path.exists(DATA_PATH):
            try:
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    CACHED_TRANSACTIONS = json.load(f)
            except Exception:
                pass
        if not CACHED_TRANSACTIONS:
            CACHED_TRANSACTIONS = generate_synthetic_transactions(2000, DATA_PATH)
    return CACHED_TRANSACTIONS

@app.on_event("startup")
def startup_event():
    get_cached_transactions()

@app.get("/api/health")
def health_check():
    txns = get_cached_transactions()
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
        "dataset_size": len(txns)
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
    txns = get_cached_transactions()
    sample = txns[:sample_size] if txns else []
    return BenchmarkEvaluator.run_benchmark(sample)

@app.post("/api/razorpay-webhook", response_model=DecisionTrace)
def handle_razorpay_webhook(
    payload: Dict[str, Any],
    x_razorpay_signature: Optional[str] = Header(None)
):
    return RazorpayWebhookHandler.parse_and_process_event(payload)

@app.get("/api/transactions")
def list_transactions(page: int = 1, limit: int = 25, code: Optional[str] = None):
    filtered = get_cached_transactions()
    if code:
        filtered = [t for t in filtered if t.get("failure_code") == code]
    start = (page - 1) * limit
    return {
        "total": len(filtered),
        "page": page,
        "limit": limit,
        "items": filtered[start:start + limit]
    }

# Fallback routes to serve static frontend dashboard directly
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _find_static_file(name: str) -> Optional[str]:
    search_dirs = [
        STATIC_DIR,
        os.path.join(os.getcwd(), "public"),
        os.path.join(os.getcwd(), "dist"),
        os.path.join(ROOT_DIR, "public"),
        os.path.join(ROOT_DIR, "dist"),
        os.path.join(ROOT_DIR, "frontend"),
        os.getcwd(),
        ROOT_DIR
    ]
    for d in search_dirs:
        target = os.path.join(d, name)
        if os.path.exists(target):
            return target
    return None

try:
    from .static_content import INDEX_HTML, STYLE_CSS, APP_JS
except ImportError:
    INDEX_HTML = "<h1>RecoveryOS Dashboard</h1>"
    STYLE_CSS = "/* RecoveryOS Styles */"
    APP_JS = "// RecoveryOS Client"

@app.get("/")
def serve_root():
    p = _find_static_file("index.html")
    if p:
        return FileResponse(p, media_type="text/html")
    return HTMLResponse(INDEX_HTML, media_type="text/html")

@app.get("/index.html")
def serve_index_html():
    return serve_root()

@app.get("/style.css")
def serve_style_css():
    p = _find_static_file("style.css")
    if p:
        return FileResponse(p, media_type="text/css")
    return HTMLResponse(STYLE_CSS, media_type="text/css")

@app.get("/app.js")
def serve_app_js():
    p = _find_static_file("app.js")
    if p:
        return FileResponse(p, media_type="application/javascript")
    return HTMLResponse(APP_JS, media_type="application/javascript")


