"""
Configuration & Deterministic Guardrail Boundaries for RecoveryOS
"""
import os

class Settings:
    PROJECT_NAME: str = "RecoveryOS"
    VERSION: str = "1.0.0"
    
    # Razorpay API Credentials (defaults to test simulator mode if not provided)
    RAZORPAY_KEY_ID: str = os.getenv("RAZORPAY_KEY_ID", "rzp_test_sim_demo12345")
    RAZORPAY_KEY_SECRET: str = os.getenv("RAZORPAY_KEY_SECRET", "sim_secret_demo67890")
    RAZORPAY_WEBHOOK_SECRET: str = os.getenv("RAZORPAY_WEBHOOK_SECRET", "whsec_sim_recoveryos")
    
    # AI Engine Settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # ─── DETERMINISTIC POLICY GUARDRAILS (THE HARD LIMITS) ───────────
    # 1. Maximum transaction value permitted for automated unassisted recovery.
    #    Transactions above this amount require human escalation/ops approval.
    MAX_AUTO_RECOVERY_AMOUNT: float = float(os.getenv("MAX_AUTO_RECOVERY_AMOUNT", "5000.0"))
    
    # 2. Hard budget on automated retries per transaction to prevent customer fatigue
    #    and recurring gateway authorization penalties.
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "2"))
    
    # 3. Minimum AI diagnostic confidence score (0.0 - 1.0) required to trigger action.
    MIN_AI_CONFIDENCE: float = float(os.getenv("MIN_AI_CONFIDENCE", "0.85"))
    
    # 4. Strict risk boundary: Transactions with risk score >= this are strictly blocked.
    FRAUD_RISK_CUTOFF: float = float(os.getenv("FRAUD_RISK_CUTOFF", "0.35"))
    
    # 5. Estimated gateway fee cost burned per pointless retry (INR)
    ESTIMATED_RETRY_FEE_BURN: float = 3.50

settings = Settings()
