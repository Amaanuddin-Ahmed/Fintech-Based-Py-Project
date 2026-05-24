import numpy as np
import pandas as pd
from decimal import Decimal
from SRC.data_handlers import load_transactions

def calculate_user_z_score(user_id, current_amount):
    """
    Computes standard statistical Z-Score deviation for a transaction amount
    based on a user's unique profile history ledger.
    """
    df_txns = load_transactions()
    user_txns = df_txns[df_txns["from_user_id"] == user_id]
    
    # Handle users with little to no spending history footprint safely
    if len(user_txns) < 2:
        return 0.0
        
    amounts = user_txns["amount"].astype(float).values
    mean = np.mean(amounts)
    std_dev = np.std(amounts)
    
    # Handle zero-variance scenarios (e.g., user always sends exactly the same amount)
    if std_dev == 0:
        return 0.0 if float(current_amount) == mean else 3.0
        
    z_score = (float(current_amount) - mean) / std_dev
    return max(0.0, z_score)

def evaluate_transaction_risk(user_id, amount, hour, device, location, user_profile):
    """
    Evaluates transaction telemetry data points to generate an integrated
    fraud risk probability matrix score from 0 to 100.
    """
    risk_score = 0
    reasons = []
    
    # 1. Quantitative Financial Volume Outliers (Z-Score)
    z_score = calculate_user_z_score(user_id, amount)
    if z_score >= 3.5:
        risk_score += 45
        reasons.append(f"Extreme transaction value variance (Z-Score: {z_score:.2f})")
    elif z_score >= 2.0:
        risk_score += 25
        reasons.append(f"Moderate transaction value variance (Z-Score: {z_score:.2f})")
        
    # 2. Hardware Profile Anomalies (Your Device Logic)
    if str(device) != str(user_profile["trusted_device_id"]):
        risk_score += 25
        reasons.append(f"Unfamiliar device signature detected: {device}")
        
    # 3. Geolocation Telemetry Changes (Your Location Logic)
    if str(location) != str(user_profile["home_location"]):
        risk_score += 20
        reasons.append(f"Unfamiliar processing city location: {location}")
        
    # 4. Midnight Processing Window Risks (Your Time Logic)
    if int(hour) >= 23 or int(hour) <= 4:
        risk_score += 15
        reasons.append(f"Suspicious transaction execution processing hour: {hour}:00 HRS")
        
    # Bound the metric output firmly between 0 and 100 points
    final_risk = min(100, risk_score)
    
    # Establish execution control classifications
    if final_risk >= 65:
        action = "BLOCK"
    elif final_risk >= 30:
        action = "OTP_CHALLENGE"
    else:
        action = "APPROVE"
        
    return final_risk, action, reasons