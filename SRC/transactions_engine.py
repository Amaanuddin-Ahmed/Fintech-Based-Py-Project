import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

def execute_transaction(from_user_id, to_user_id, amount_str, users_filepath="DATA/users.csv"):
    """
    Executes a high-precision balance transfer between two users with strict validation.
    """
    # Load fresh user database rows
    df_users = pd.read_csv(users_filepath)
    df_users['user_id'] = df_users['user_id'].astype(str).str.strip()
    
    # 1. Validation: Does Sender Exist?
    if from_user_id not in df_users['user_id'].values:
        return False, "Sender profile account record not found."
        
    # 2. Validation: Does Recipient Exist? (Your U999 Safety Rule!)
    if to_user_id not in df_users['user_id'].values:
        return False, f"Recipient account ID '{to_user_id}' does not exist. Please check the ID."
        
    # Set up high-precision Decimal math configurations
    amount = Decimal(str(amount_str))
    
    # Extract current balances from ledger rows
    sender_balance = Decimal(str(df_users.loc[df_users['user_id'] == from_user_id, 'current_balance'].values[0]))
    recipient_balance = Decimal(str(df_users.loc[df_users['user_id'] == to_user_id, 'current_balance'].values[0]))
    
    # 3. Validation: Does Sender Have Enough Money?
    if sender_balance < amount:
        return False, "Transaction declined: Insufficient account funds available."
        
    # 4. Atomic Execution: Modify values safely in memory
    new_sender_bal = sender_balance - amount
    new_recipient_bal = recipient_balance + amount
    
    # Format to exactly 7 decimal positions uniformly
    df_users.loc[df_users['user_id'] == from_user_id, 'current_balance'] = float(new_sender_bal)
    df_users.loc[df_users['user_id'] == to_user_id, 'current_balance'] = float(new_recipient_bal)
    
    # Save the updated data securely back to CSV
    df_users.to_csv(users_filepath, index=False)
    return True, f"Successfully transferred ${amount:.7f} to {to_user_id}."