# RecoveryOS Security Architecture & Defensive Policy Invariants

## 1. Threat Model & Design Principles
RecoveryOS acts as an autonomous revenue recovery decision engine. In financial automation, the primary failure mode is **uncontrolled or unsafe automated execution** (e.g., infinite retry storms, double-charging customers, retrying fraudulent cards, or attempting high-value money movement without oversight).

RecoveryOS adheres to the principle of **Separation of Concerns**:
- **The AI Diagnostic Layer proposes actions based on telemetry.**
- **The Deterministic Policy Layer validates proposals against hard financial safety invariants.**
- **The AI CANNOT override or bypass the Policy Engine under any circumstance.**

---

## 2. Secrets Isolation & Client-Side Safety
1. **Zero Secret Exposure to Client**:
   - Razorpay API Secrets, Webhook Secrets, and LLM API Keys are strictly confined to backend server environments (`os.getenv`).
   - The browser interface communicates solely via authenticated/rate-limited REST endpoints (`/api/diagnose`, `/api/benchmarks`, `/api/simulate-preset`).
2. **Environment Variable Configuration**:
   - `.env.example` is committed to the repository with placeholder values.
   - Real credentials and live API secrets are strictly ignored via `.gitignore`.

---

## 3. Webhook Integrity, Idempotency & Replay Defense
1. **HMAC-SHA256 Signature Verification**:
   - Every inbound webhook payload received at `/api/razorpay/webhook` is verified against the `X-Razorpay-Signature` header using HMAC-SHA256.
2. **Event Idempotency Cache**:
   - RecoveryOS maintains an event idempotency table (`PROCESSED_WEBHOOK_EVENTS`).
   - If an event ID or transaction ID is re-transmitted (e.g., network retry or replay attack), the system acknowledges the event but suppresses redundant execution:
   ```json
   {
     "status": "ignored_duplicate",
     "message": "Event event_001 already processed. Deduplication guardrail triggered."
   }
   ```
3. **Already-Captured Interception**:
   - If a payment event has already settled or captured (`payment.captured`), the recovery engine immediately halts to eliminate double debiting.

---

## 4. Deterministic Financial Guardrails (Hard Invariants)

| Guardrail Rule | Hard Boundary | Failure Action | Security Rationale |
|---|---|---|---|
| **AUTO_RECOVERY_AMOUNT_CAP** | $\le$ ₹5,000.00 | Block $\rightarrow$ Escalate to Human | Prevents autonomous money movement on high-value orders without human eyes. |
| **FRAUD_RISK_BOUNDARY** | Risk Score $\le$ 0.35 | Block $\rightarrow$ Escalate to Human | Stops automated retries on stolen cards, synthetic identities, or velocity spikes. |
| **MAX_RETRY_BUDGET** | Attempts $\le$ 2 | Block $\rightarrow$ Escalate to Human | Protects merchants from gateway authorization dispute penalties and card network fines. |
| **AI_CONFIDENCE_GATE** | Confidence $\ge$ 85% | Block $\rightarrow$ Escalate to Human | Rejects uncertain or hallucinations in LLM reasoning from executing autonomous actions. |
| **PERMANENT_FAILURE_STOP** | Permanent decline codes | Halt $\rightarrow$ `DO_NOTHING` | Avoids wasting gateway transaction fees (₹3.50/call) on dead or expired instruments. |

---

## 5. Input Validation & Safe Sanitization
- All request payloads are strictly parsed and sanitized using **Pydantic v2 schemas** (`TransactionEvent`, `PresetScenarioRequest`).
- Malformed payloads, SQL injection tokens, or schema deviations are rejected with standard HTTP 422 Unprocessable Entity responses before reaching business logic.
- Exception handlers suppress internal tracebacks in production mode.
