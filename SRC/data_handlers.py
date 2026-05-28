import pandas as pd
from decimal import Decimal

def load_users(filepath="DATA/users.csv"):
    df = pd.read_csv(filepath)
    df["current_balance"] = df["current_balance"].astype(str).map(Decimal)
    return df

def save_users(df, filepath="DATA/users.csv"):
    df_to_save = df.copy()
    df_to_save["current_balance"] = df_to_save["current_balance"].apply(lambda val: f"{val:.7f}")
    df_to_save.to_csv(filepath, index=False)

def load_transactions(filepath="DATA/transactions.csv"):
    df = pd.read_csv(filepath)
    df["amount"] = df["amount"].astype(str).map(Decimal)
    return df

def log_new_transaction(txn_id, from_id, to_id, amount, hour, device, location, filepath="DATA/transactions.csv"):
    df = load_transactions(filepath)
    new_row = {
        "txn_id": txn_id,
        "from_user_id": from_id,
        "to_user_id": to_id,
        "amount": Decimal(str(amount)),
        "txn_hour": int(hour),
        "device_used": str(device),
        "location": str(location)
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df["amount"] = df["amount"].apply(lambda val: f"{val:.7f}")
    df.to_csv(filepath, index=False)