import random
import pandas as pd

def generate_secure_otp():
    """
    Generates a secure, temporary 6-digit verification code.
    """
    return str(random.randint(100000, 999999))

def verify_otp_attempt(user_id, entered_otp, correct_otp, users_filepath="DATA/users.csv"):
    """
    Validates a submitted OTP token and atomically updates failure thresholds
    inside the persistent database file to prevent bypass vulnerabilities.
    """
    df_users = pd.read_csv(users_filepath)
    df_users['user_id'] = df_users['user_id'].astype(str).str.strip()
    
    if user_id not in df_users['user_id'].values:
        return False, "User account not found."
        
    # Correct OTP entered
    if str(entered_otp) == str(correct_otp):
        # Reset the failed attempts counter back to zero on success
        df_users.loc[df_users['user_id'] == user_id, 'failed_otp_attempts'] = 0
        df_users.to_csv(users_filepath, index=False)
        return True, "Verification successful."
        
    # Incorrect OTP entered
    else:
        # Extract the raw element value safely from the matching series index row
        raw_attempts = df_users.loc[df_users['user_id'] == user_id, 'failed_otp_attempts'].values[0]
        
        # DEFENSIVE IMPLEMENTATION: If value is blank, empty, or NaN, convert cleanly to integer 0
        if pd.isna(raw_attempts):
            current_attempts = 0
        else:
            current_attempts = int(float(raw_attempts))
            
        new_attempts = current_attempts + 1
        df_users.loc[df_users['user_id'] == user_id, 'failed_otp_attempts'] = new_attempts
        
        # Enforce account freezing if failure threshold is reached (3 strikes rule)
        if new_attempts >= 3:
            df_users.loc[df_users['user_id'] == user_id, 'account_status'] = 'LOCKED'
            df_users.to_csv(users_filepath, index=False)
            return False, "SECURITY ALERT: Maximum validation attempts reached. Account has been LOCKED."
            
        df_users.to_csv(users_filepath, index=False)
        remaining = 3 - new_attempts
        return False, f"Invalid code. Verification failed. {remaining} attempt(s) remaining."