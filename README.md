# RecoveryOS ⚡
### Autonomous AI Revenue Recovery Decision Engine & Policy Guardrails
**Razorpay AI Buildathon 2026 — Track 3: AI Revenue Recovery**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Razorpay Buildathon](https://img.shields.io/badge/Razorpay-Buildathon%202026-blue)](https://razorpay.com/buildathon/)
[![Architecture: Hybrid AI + Deterministic](https://img.shields.io/badge/Architecture-Hybrid%20AI%20%2B%20Policy%20Gates-indigo.svg)]()
[![Production: Live on Vercel](https://img.shields.io/badge/Vercel-Deployed-success)](https://backend-two-chi-94.vercel.app)

---

> **Demo & Simulation Notice:**  
> RecoveryOS is an engineering prototype evaluated against synthetic payment telemetry and the Razorpay Test Mode Emulator. **No real customer money is moved.** All recovery metrics represent simulated recovery outcomes and estimated gateway fee savings on held-out test data.

---

## 🎯 1. One-Line Product Description
**RecoveryOS is an AI-powered revenue recovery decision engine for online merchants that maximizes recovered revenue while deterministically preventing unsafe, useless, or unauthorized recovery actions.**

---

## 🛑 2. The Problem
In modern digital commerce, **10%–25% of all payment attempts fail**.
Today's merchants and payment gateways react with **naive, indiscriminate retrying**:
1. **Fee Burning**: Retrying dead instruments (expired cards, closed accounts) burns **₹3.50+ per authorization attempt** in pointless gateway and network fees.
2. **Fraud & Chargeback Escalation**: Retrying high-risk transactions with suspicious IP or device anomalies triggers severe chargeback fines and merchant blocklisting.
3. **Customer Fatigue**: Multiple automated debits on insufficient funds damage brand trust and cause checkout abandonment.
4. **Lack of Bounded Autonomy**: Blind automation without strict transaction caps exposes merchants to uncontrolled liability.

---

## 👥 3. Target User
- **Mid-to-Enterprise Online Merchants** (D2C brands, subscription platforms, quick commerce, marketplace platforms).
- **Payment Operations & Risk Teams** needing autonomous recovery bounded by strict, auditable financial policies.

---

## 💡 4. Why Existing Retry Systems Are Insufficient
Existing retry mechanisms (e.g., standard dunning rules, basic cron retry loops) are **blind and binary**:
- They treat a ₹99 order the same as a ₹42,000 order.
- They cannot distinguish between transient network latency and permanent card expiration.
- They lack fraud risk gates and customer lifetime value (CLV) context.
- They lack stopping rules to halt execution when further attempts are futile.

---

## 🚀 5. The Solution: RecoveryOS
RecoveryOS introduces **Cognitive Revenue Recovery**:
- **Perceives** real-time payment failure events via webhooks.
- **Diagnoses** failure root cause, customer relationship health, and recoverability probability.
- **Recommends** the optimal non-intrusive recovery intervention (Smart Jitter Retry, Smart Payment Link, or Contextual WhatsApp Nudge).
- **Enforces** non-negotiable deterministic financial policies before any money movement action can execute.

```
                  ┌───────────────────────────────┐
                  │ Razorpay Webhook Event Stream │
                  │     (payment.failed / drops)  │
                  └───────────────┬───────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │      PERCEPTION LAYER         │
                  │   Error Code, Intent, Profile │
                  └───────────────┬───────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │     SEMANTIC AI DIAGNOSIS     │
                  │  Recoverability & Action Pick │
                  └───────────────┬───────────────┘
                                  ▼
                  ┌───────────────────────────────┐
                  │ DETERMINISTIC POLICY GUARDRAIL│  ◄── Hard limits (AI CANNOT bypass)
                  │  • Auto-Cap <= ₹5,000         │
                  │  • Max 2 Retries Budget       │
                  │  • Fraud Risk < 0.35          │
                  │  • Confidence >= 85%          │
                  │  • Permanent Failure Stop     │
                  └───────────────┬───────────────┘
                                  │
                   ┌──────────────┴──────────────┐
             [ APPROVED ]                  [ BLOCKED / HALTED ]
                   ▼                             ▼
        ┌─────────────────────┐        ┌─────────────────────┐
        │   ACTION EXECUTOR   │        │   DEFENSIVE ACTIONS │
        │ • Smart Jitter Retry│        │ • Escalate to Ops   │
        │ • Smart Pay Link    │        │ • Suppress Retry    │
        │ • Contextual Nudge  │        │   (Fees Saved)      │
        └──────────┬──────────┘        └─────────────────────┘
                   ▼
        ┌─────────────────────┐
        │  VERIFIED RECOVERY  │
        │  • ₹ Captured       │
        │  • Full Audit Trace │
        └─────────────────────┘
```

---

## ⚖️ 6. AI Judgment vs. Deterministic Policy Separation

Razorpay judges evaluate projects strictly on **AI Judgment**—avoiding using LLMs for arithmetic or absolute boundaries, while leveraging AI for semantic interpretation:

| Layer | Responsibilities Handled | Can It Move Money? |
| :--- | :--- | :---: |
| **AI Diagnostic Layer** | • Categorizes messy bank error strings into semantic failure archetypes<br>• Synthesizes customer CLV and prior payment behavior<br>• Recommends optimal recovery rail and timing<br>• Assigns diagnostic confidence score (0.0 – 1.0) | **NO** (Advisory Only) |
| **Deterministic Policy Layer** | • Enforces hard cap: `amount <= ₹5,000`<br>• Enforces retry budget: `attempts <= 2`<br>• Enforces fraud risk boundary: `risk < 0.35`<br>• Enforces confidence gate: `confidence >= 85%`<br>• Enforces permanent failure stopping rules (`CARD_EXPIRED`) | **GATEKEEPER** (Enforces Invariants) |
| **Action Execution** | • Issues Razorpay Smart Retry or Payment Link with exponential jitter | **ONLY IF APPROVED** |

---

## 🛡️ 7. Deterministic Safety Guardrails

| Guardrail Rule | Hard Boundary | Violation Action | Rationale |
|---|---|---|---|
| `AUTO_RECOVERY_AMOUNT_CAP` | $\le$ ₹5,000.00 | Block $\rightarrow$ Escalate to Ops | Eliminates autonomous high-ticket liability. |
| `FRAUD_RISK_BOUNDARY` | Risk Score $\le$ 0.35 | Block $\rightarrow$ Escalate to Ops | Protects merchants against chargeback fraud. |
| `MAX_RETRY_BUDGET` | Attempts $\le$ 2 | Block $\rightarrow$ Escalate to Ops | Prevents gateway rate-limiting and card network penalties. |
| `AI_CONFIDENCE_GATE` | Confidence $\ge$ 85% | Block $\rightarrow$ Escalate to Ops | Stops speculative model hallucinations from auto-triggering. |
| `PERMANENT_FAILURE_STOP` | Permanent decline codes | Halt $\rightarrow$ `DO_NOTHING` | Halts execution on dead cards, saving merchant gateway fees. |
| `WEBHOOK_IDEMPOTENCY` | In-memory SHA256 event cache | Drop duplicate | Replay attack defense; eliminates double recoveries. |
| `ALREADY_CAPTURED_SAFETY` | Status == `captured` | Suppress action | Prevents double charging when alternate payment succeeded. |

---

## 📊 8. Scientific Benchmark Methodology & Held-Out Evaluation

A corpus of **20,000 synthetic transactions** was generated using fixed PRNG seed `20260904` across 6 realistic Indian merchant verticals (Lenskart, boAt, Swiggy, Zomato, Nykaa, Urban Company).

### Exact Dataset Partition:
- **70% Training / Calibration** (14,000 records)
- **15% Validation / Rule Tuning** (3,000 records)
- **15% Held-Out Test Set** (5,000 records: `txns[-5000:]`)

### Comparative Benchmark Results (5,000 Held-Out Records):

| Metric | Naive Retry Baseline | RecoveryOS Engine | Impact / Lift |
| :--- | :---: | :---: | :---: |
| **Evaluated Records** | 5,000 | 5,000 | Held-out test set |
| **Recovery Success Rate** | 22.36% | **39.79%** | **+17.43% Absolute Lift** |
| **Net Recovered Amount** | ₹41.3 Lakh | **₹73.5 Lakh** | **+₹32.3 Lakh Additional Lift** |
| **Unnecessary Actions Burned** | 3,882 | **0** | **100% Eliminated** |
| **High-Risk Actions Taken** | 808 | **0 (Blocked)** | **100% Fraud Quarantined** |
| **Estimated Gateway Fees Saved** | ₹0 | **₹2,026.50** | **Direct Fee Savings** |
| **Net Economic Lift** | ₹0 | **+₹32.33 Lakh** | **Definitive Merchant ROI** |

*To evaluate the entire 20,000 dataset on-demand, click the "Run Full 20k Benchmark" button in the dashboard or execute `POST /api/run-full-benchmark`.*

---

## ⚡ 9. Interactive Demo Scenarios for Judges

The interactive console provides 4 repeatable presets representing common payment challenges:

1. **Scenario 1: Transient UPI Timeout (₹1,499)**
   - *Failure:* `GATEWAY_TIMEOUT` during bank switch transition.
   - *AI Diagnosis:* Transient switch delay (98% confidence). Loyal customer (CLV ₹15,400).
   - *Policy Result:* **ALL CHECKS PASSED**.
   - *Outcome:* Auto-retry dispatched with jitter $\rightarrow$ **₹1,499 Recovered**.

2. **Scenario 2: High-Value Risk Breach (₹42,000)**
   - *Failure:* `HIGH_RISK_SUSPECTED` on credit card.
   - *AI Diagnosis:* Suspicious IP velocity, risk score 0.78, zero prior order history (84% confidence).
   - *Policy Result:* **ACTION BLOCKED BY POLICY GUARDRAIL** (Exceeds ₹5k cap, exceeds 0.35 risk ceiling, below 85% confidence).
   - *Outcome:* **Halted BEFORE Execution** $\rightarrow$ Escalated for Human Review.

3. **Scenario 3: Expired Instrument (₹890)**
   - *Failure:* `CARD_EXPIRED` permanent decline.
   - *AI Diagnosis:* Permanent card expiration (99% confidence).
   - *Policy Result:* **NO AUTOMATED RECOVERY ALLOWED**.
   - *Outcome:* **HALTED — PERMANENT FAILURE** $\rightarrow$ Estimated ₹3.50 gateway authorization fee saved.

4. **Scenario 4: Checkout Cart Dropoff (₹3,250)**
   - *Failure:* `CART_DROPOFF` funnel abandonment.
   - *AI Diagnosis:* Warm purchase intent abandoned at QR stage (93% confidence).
   - *Policy Result:* **ALL CHECKS PASSED**.
   - *Outcome:* Razorpay Smart Payment Link dispatched $\rightarrow$ **₹3,250 Recovered** (amount matches exactly from start to finish).

---

## 🧪 10. Automated Chaos, Policy & Safety Tests (15 Tests)

All safety rules, idempotency defenses, and policy boundaries are backed by automated tests:

```bash
python -m unittest discover -s backend/tests -v
```

### Verified Test Suite:
```text
test_01_duplicate_webhook_idempotency           [PASS] Replay webhooks safely dropped
test_02_already_captured_payment_safety         [PASS] Captured payments suppressed from retry
test_03_ai_cannot_override_policy_engine        [PASS] Rogue AI cannot bypass deterministic engine
test_04_high_risk_transaction_blocked           [PASS] Risk > 0.35 quarantined for review
test_05_low_confidence_ai_gated                 [PASS] Confidence < 85% gated to human ops
test_06_amount_limit_exceeded                   [PASS] Amount > ₹5,000 blocked
test_07_retry_budget_exhaustion                 [PASS] Attempts > 2 halted
test_08_permanent_failure_stop_rule             [PASS] Expired instruments halted (fee saved)
test_09_scenario_4_consistent_amount            [PASS] ₹3,250 cart value recovered consistently
test_10_benchmark_determinism_and_reproducibility [PASS] Seed 20260904 produces exact identical numbers
test_01_transient_happy_path                    [PASS] Transient failures within limit approved
test_02_high_amount_escalation_guardrail        [PASS] ₹42k escalated to human
test_03_fraud_risk_boundary_guardrail           [PASS] Fraud risk cutoff enforced
test_04_permanent_failure_stop_rule             [PASS] Permanent stop rule enforced
test_05_retry_budget_exhaustion                 [PASS] Max retry budget enforced

Ran 15 tests in 0.005s — OK (15/15 Passed)
```

---

## 🛠️ 11. Quickstart & Local Setup

### Option A: Zero-Dependency Run (Instant Demo)
```powershell
# Navigate to project directory
cd C:\Users\VICTUS\.gemini\antigravity-ide\scratch\recovery-os

# Start standalone Python server
python backend/server.py
```
Open **`http://localhost:8000`** in your browser.

### Option B: FastAPI Backend + Vite Frontend
```powershell
# Terminal 1: FastAPI Backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Vite Dev Server
npm run dev
```

---

## 🌐 12. Deployment URLs
- **Live Frontend / Full App on Vercel:** [https://backend-two-chi-94.vercel.app](https://backend-two-chi-94.vercel.app)
- **Live Health API:** [https://backend-two-chi-94.vercel.app/api/health](https://backend-two-chi-94.vercel.app/api/health)
- **Live Benchmark API:** [https://backend-two-chi-94.vercel.app/api/benchmarks](https://backend-two-chi-94.vercel.app/api/benchmarks)

---

## ⚠️ 13. Known Limitations & Future Improvements
1. **Synthetic Telemetry**: Current evaluation uses realistic synthetic merchant failure distributions rather than live banking feeds. Future work includes sandbox testing with live Razorpay OAuth webhooks.
2. **Multi-Touch Escalation**: Human review currently logs an auditable quarantine ticket; future iterations can integrate direct Slack/Zendesk webhooks for merchant ops teams.
3. **Bandit Learning**: Exploration/exploitation reinforcement learning for dynamic retry jitter windows across individual issuing banks.

---

## 🛡️ License
Built for the **Razorpay AI Buildathon 2026 (Track 3: AI Revenue Recovery)**. Licensed under the MIT License.
