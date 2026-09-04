"""
RecoveryOS Standalone Server

High-performance API server with zero mandatory pip dependencies.
Implements the full RecoveryOS REST API and static asset hosting.
"""
import os
import sys
import json
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any

# Add parent directory to path so imports work reliably
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)

from app.core.config import settings
from app.core.agent import RecoveryAgent
from app.core.policy_engine import PolicyEngine
from app.core.evaluator import BenchmarkEvaluator
from app.data.synthetic_generator import generate_synthetic_transactions
from app.api.routes_razorpay import RazorpayWebhookHandler
from app.models.schemas import TransactionEvent

DATA_FILE = os.path.join(CURRENT_DIR, "app", "data", "transactions.json")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# In-memory transaction cache
CACHED_TRANSACTIONS = []
CACHED_BENCHMARK = None

def init_data():
    global CACHED_TRANSACTIONS, CACHED_BENCHMARK
    if not os.path.exists(DATA_FILE):
        print("Generating synthetic 20,000 transaction dataset...")
        CACHED_TRANSACTIONS = generate_synthetic_transactions(20000, DATA_FILE)
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            CACHED_TRANSACTIONS = json.load(f)
    print(f"Loaded {len(CACHED_TRANSACTIONS):,} transactions into memory.")
    
    # Precompute benchmark on sample or full set
    print("Computing initial benchmark metrics against Naive Baseline...")
    CACHED_BENCHMARK = BenchmarkEvaluator.run_benchmark(CACHED_TRANSACTIONS[:5000])
    print(f"Benchmark ready: {CACHED_BENCHMARK.recoveryos_recovery_rate}% Recovery Rate vs {CACHED_BENCHMARK.baseline_recovery_rate}% Baseline.")

class RecoveryOSHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Razorpay-Signature")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/health":
            self._set_headers(200)
            resp = {
                "status": "healthy",
                "project": settings.PROJECT_NAME,
                "version": settings.VERSION,
                "policies": {
                    "max_auto_recovery_amount": settings.MAX_AUTO_RECOVERY_AMOUNT,
                    "max_retry_attempts": settings.MAX_RETRY_ATTEMPTS,
                    "min_ai_confidence": settings.MIN_AI_CONFIDENCE,
                    "fraud_risk_cutoff": settings.FRAUD_RISK_CUTOFF
                },
                "transactions_loaded": len(CACHED_TRANSACTIONS)
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif path == "/api/benchmarks":
            global CACHED_BENCHMARK
            self._set_headers(200)
            if not CACHED_BENCHMARK:
                CACHED_BENCHMARK = BenchmarkEvaluator.run_benchmark(CACHED_TRANSACTIONS[:5000])
            self.wfile.write(CACHED_BENCHMARK.model_dump_json().encode("utf-8"))

        elif path == "/api/transactions":
            page = int(query.get("page", [1])[0])
            limit = int(query.get("limit", [25])[0])
            filter_code = query.get("code", [None])[0]

            filtered = CACHED_TRANSACTIONS
            if filter_code:
                filtered = [t for t in filtered if t.get("failure_code") == filter_code]

            start = (page - 1) * limit
            end = start + limit
            items = filtered[start:end]

            self._set_headers(200)
            resp = {
                "total": len(filtered),
                "page": page,
                "limit": limit,
                "items": items
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        else:
            # Serve static frontend files
            self.serve_static(path)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get("Content-Length", 0))
        body_bytes = self.rfile.read(content_length)
        
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {}

        if path == "/api/diagnose":
            try:
                txn = TransactionEvent.from_dict(body) if hasattr(TransactionEvent, "from_dict") else TransactionEvent(**body)
                trace = RecoveryAgent.process_event(txn)
                self._set_headers(200)
                self.wfile.write(trace.model_dump_json().encode("utf-8"))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif path == "/api/simulate-preset":
            scenario_key = body.get("scenario", "transient_upi")
            mock_webhook = RazorpayWebhookHandler.generate_mock_webhook(scenario_key)
            trace = RazorpayWebhookHandler.parse_and_process_event(mock_webhook)
            self._set_headers(200)
            resp = {
                "scenario": scenario_key,
                "mock_webhook_payload": mock_webhook,
                "decision_trace": trace.model_dump()
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))

        elif path == "/api/razorpay-webhook":
            sig = self.headers.get("X-Razorpay-Signature", "")
            # If real signature checking is requested
            trace = RazorpayWebhookHandler.parse_and_process_event(body)
            self._set_headers(200)
            self.wfile.write(trace.model_dump_json().encode("utf-8"))

        elif path == "/api/run-full-benchmark":
            global CACHED_BENCHMARK
            # Run benchmark on full 20,000 records
            CACHED_BENCHMARK = BenchmarkEvaluator.run_benchmark(CACHED_TRANSACTIONS)
            self._set_headers(200)
            self.wfile.write(CACHED_BENCHMARK.model_dump_json().encode("utf-8"))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode("utf-8"))

    def serve_static(self, path):
        if path in ["/", ""]:
            path = "/index.html"
        
        file_path = os.path.join(FRONTEND_DIR, path.lstrip("/"))
        if not os.path.exists(file_path):
            self._set_headers(404, "text/plain")
            self.wfile.write(b"404 Not Found")
            return

        content_type = "text/plain"
        if file_path.endswith(".html"):
            content_type = "text/html"
        elif file_path.endswith(".css"):
            content_type = "text/css"
        elif file_path.endswith(".js"):
            content_type = "application/javascript"
        elif file_path.endswith(".json"):
            content_type = "application/json"
        elif file_path.endswith(".svg"):
            content_type = "image/svg+xml"

        with open(file_path, "rb") as f:
            data = f.read()

        self._set_headers(200, content_type)
        self.wfile.write(data)

def run(port: int = 8000):
    init_data()
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, RecoveryOSHandler)
    print(f"\n=======================================================")
    print(f"  RecoveryOS Server Running at http://127.0.0.1:{port}")
    print(f"  Dashboard available at: http://127.0.0.1:{port}/index.html")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down RecoveryOS server gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    run(port)
