
# 🏦 GuardianShield: Precision-Safe Fintech Simulator with Fraud Detection

GuardianShield is a robust peer-to-peer payment gateway architecture designed to eliminate transactional math drift while actively blocking financial fraud telemetry outliers. Built around high-precision banking logic, the engine guarantees data-state alignment by coupling real-time telemetry risk evaluation with memory-isolated transaction processing.

---

### 🚀 Core Architecture at a Glance

```
  [ User Pay Input ] 
          │
          ▼
┌────────────────────────────────────────────────────────┐
│  SRC/fraud_rules.py: Telemetry Risk Matrix Evaluation  │
└─────────────────────────┬──────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
     [ Risk Score > 60 ]      [ 30 <= Risk Score <= 60 ]
            │                           │
            ▼                           ▼
       ⚡ ACTION: BLOCK          🔑 ACTION: OTP CHALLENGE
    (Memory Clear Void)                 │
                                        ▼
                         [ Streamlit Session Isolation ]
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
                 [ Correct Token ]             [ App State Crash ]
                         │                             │
                         ▼                             ▼
         ┌──────────────────────────────┐       ⚠️ CRITICAL RISK:
         │ SRC/transactions_engine.py   │       Stale data held in global 
         │  Atomic Ledger Verification  │       memory vault buffer.
         └──────────────┬───────────────┘
                        │
                        ▼
         [ Balance Deduction & Write ]

```

---

### ⚙️ Operational System Mechanics

* **⚡ Zero-Drift Asset Protection:** Financial arithmetic discards floating-point tracking variables entirely. Account states utilize Python `Decimal` modules mapping to uniform database structures to prevent rounding exploitation.
* **📡 Layered Telemetry Extraction:** Incoming transaction contexts are measured across explicit environmental variables—including device hardware signatures, geolocation offsets, clock-hour schedules, and custom historical standard deviation footprints ($Z\text{-Scores}$).
* **🔐 Session State Isolation Rules:** Suspicious transfers undergo conditional runtime locks. Temporary global transactional data variables are suspended within an isolated state pending valid token challenge release signals.

---

### 🛠️ Low-Level Engine Component Breakdown

#### 1. Identity & State Gatekeeping (`UI/app.py`)

Provides dynamic session mapping and serves as the presentation gateway layer. It manages asynchronous data ingestion using the configuration loop below:

* Initializes local browser context structures safely.
* Maps standard clock positions (12-Hour representations) dynamically into 24-Hour integers prior to passing payloads downward to security verification tasks.
* Displays structural user metric cards and visual asset distributions on matching session state logins.

#### 2. Quantitative Fraud Analytics Core (`SRC/fraud_rules.py`)

Computes telemetry risk indexes securely scaled between values of $0$ and $100$. The decision matrix handles incoming transfer validations using categorical threat criteria:

| Threat Category | Underlying Processing Rule | Weight Modifier |
| --- | --- | --- |
| **Statistical Outlier** | Triggers if transactional value creates a volume outlier ($Z\text{-Score} \ge 3.5$). | `+45 Risk Points` |
| **Hardware Shift** | Evaluates current client hardware ID against user profile trusted device signatures. | `+25 Risk Points` |
| **Location Anomaly** | Detects processing city location departures relative to home geolocation profiles. | `+20 Risk Points` |
| **Window Security** | Catches midnight ledger entry submissions executed between 23:00 and 04:00 HRS. | `+15 Risk Points` |
| **Impossible Travel** | Computes sequence space-time speed from last recorded transaction row context. | `+50 Risk Block` |

#### 3. High-Precision Ledger Processor (`SRC/transactions_engine.py`)

Handles disk serialization and enforces atomic accounting state integrity.

* Validates participant records via string-cleaned system directory match passes.
* Confirms total available sender balances exceed intent amounts prior to execution.
* Updates persistence files safely using uniform data structures to ensure total system assets remain completely balanced.

```python
# System Core Math Invariance Rule
new_sender_bal = sender_balance - amount
new_recipient_bal = recipient_balance + amount

```

---

### 📋 File System Map

```filepath
├── DATA/
│   ├── users.csv             # Primary account ledgers (Balances, Hardware Signatures)
│   └── transactions.csv      # Chronological audit tracks for Z-Score computing
├── LOGS/
│   └── fraud_logs.csv        # Flagged system risk markers and telemetry descriptions
├── SRC/
│   ├── data_handlers.py      # Abstracted CSV database reading/writing interfaces
│   ├── fraud_rules.py        # Z-Score math algorithms and categorical evaluation rules
│   ├── main.py               # Memory buffer routing coordinator
│   └── transactions_engine.py# High-precision financial arithmetic module
└── UI/
    └── app.py                # Streamlit responsive frontend control dashboards

```
