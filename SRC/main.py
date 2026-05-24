from decimal import Decimal
from SRC.data_handlers import load_users
from SRC.fraud_rules import evaluate_transaction_risk
from SRC.transactions_engine import execute_transaction

# This temporary dictionary acts as our secure memory vault for pending payments
pending_transaction_vault = {}

def process_payment_request(from_user, to_user, amount_str, hour, device, location):
    """
    Coordinates the initial verification gate for an incoming payment attempt.
    """
    global pending_transaction_vault
    
    # Load user registry matrix to check status profiles
    df_users = load_users()
    
    if from_user not in df_users['user_id'].values:
        return "REJECTED", "Sender account does not exist."
        
    user_profile = df_users[df_users['user_id'] == from_user].iloc[0]
    
    # Safety Check: Instantly reject if the account is already frozen
    if user_profile['account_status'] == 'LOCKED':
        return "REJECTED", "Transaction denied. This account is currently LOCKED due to security flags."
        
    # Run our quantitative scoring metrics engine
    risk_score, action, reasons = evaluate_transaction_risk(
        from_user, amount_str, hour, device, location, user_profile
    )
    
    # Store the parameters in our temporary dictionary vault (Your design step!)
    pending_transaction_vault = {
        "from_user_id": from_user,
        "to_user_id": to_user,
        "amount": amount_str,
        "risk_score": risk_score,
        "reasons": reasons
    }
    
    if action == "BLOCK":
        pending_transaction_vault.clear() # Clear memory instantly on high fraud
        return "REJECTED", f"Blocked by automated fraud rules. Reasons: {', '.join(reasons)}"
        
    elif action == "OTP_CHALLENGE":
        return "OTP_REQUIRED", f"Security Verification Required. Risk Score: {risk_score}"
        
    else:  # APPROVE
        # Safe to pass straight to our atomic execution ledger
        success, message = execute_transaction(from_user, to_user, amount_str)
        pending_transaction_vault.clear() # Clear vault after completion
        return "SUCCESS", message

def confirm_otp_and_release_vault(is_otp_correct):
    """
    Processes the held temporary vault transaction based on OTP validation results.
    """
    global pending_transaction_vault
    
    if not pending_transaction_vault:
        return False, "No active pending transaction found in memory vault."
        
    if is_otp_correct:
        # Extract held transaction data fields safely
        success, message = execute_transaction(
            pending_transaction_vault["from_user_id"],
            pending_transaction_vault["to_user_id"],
            pending_transaction_vault["amount"]
        )
        pending_transaction_vault.clear() # Free up the vault memory allocation
        return True, message
    else:
        pending_transaction_vault.clear() # Trash the data if validation fails
        return False, "Payment failed: Invalid One-Time Password verification code entered."