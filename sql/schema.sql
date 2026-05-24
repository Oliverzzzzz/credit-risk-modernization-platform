CREATE TABLE IF NOT EXISTS credit_applications (
    application_id TEXT PRIMARY KEY,
    annual_income NUMERIC NOT NULL,
    debt_to_income NUMERIC NOT NULL,
    loan_amount NUMERIC NOT NULL,
    interest_rate NUMERIC NOT NULL,
    employment_length_years INTEGER NOT NULL,
    credit_history_years INTEGER NOT NULL,
    delinquency_count INTEGER NOT NULL,
    revolving_utilization NUMERIC NOT NULL,
    open_credit_lines INTEGER NOT NULL,
    home_ownership TEXT NOT NULL,
    loan_purpose TEXT NOT NULL,
    default_flag INTEGER
);

CREATE TABLE IF NOT EXISTS prediction_audit_log (
    prediction_id TEXT PRIMARY KEY,
    application_id TEXT,
    model_version TEXT NOT NULL,
    risk_probability NUMERIC NOT NULL,
    risk_tier TEXT NOT NULL,
    reason_codes TEXT,
    scored_at TIMESTAMP NOT NULL
);
