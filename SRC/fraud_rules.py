import numpy as np
import pandas as pd
from decimal import Decimal
from SRC.data_handlers import load_transactions

def calculate_user_z_score(user_id, current_amount):
   
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
        
    # 5. Advanced Geo-Velocity Validation (Impossible Travel Rule)
    try:
        df_all_txns = load_transactions()
        user_history = df_all_txns[df_all_txns["from_user_id"] == user_id]
        
        if not user_history.empty:
            # Grab the last row record in the ledger file
            last_txn = user_history.iloc[-1]
            last_location = str(last_txn["location"])
            last_hour = int(last_txn["txn_hour"])
            
            # If location changed from the last sequential payment record entry
            if last_location != str(location):
                time_difference = abs(int(hour) - last_hour)
                
                # If transaction occurred too quickly across different regions
                if time_difference <= 2:
                    risk_score += 50  # Heavy weight penalty to guarantee a BLOCK status
                    reasons.append(f"IMPOSSIBLE TRAVEL VELOCITY: Instant location shift from {last_location} to {location} within {time_difference} hour(s).")
    except Exception as e:
        pass # Gracefully fall back if transactional history file parsing error occurs
        
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