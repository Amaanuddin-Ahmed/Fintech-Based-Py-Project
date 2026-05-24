# COMPLETE SET OF RULES THAT ARE TO BE FOLLOWED TO DEFINE A PAYMENT AS FRAUD OR SAFE
def is_fraudulent(transaction):
    # Rule 1: If the transaction amount is greater than $10,000, it is considered fraudulent
    if transaction['amount'] > 10000:
        return True
    
    # Rule 2: If the transaction is made from a high-risk country, it is considered fraudulent
    high_risk_countries = ['CountryA', 'CountryB', 'CountryC']
    if transaction['country'] in high_risk_countries:
        return True
    
    # Rule 3: If the transaction is made at an unusual time (e.g., between 12 AM and 5 AM), it is considered fraudulent
    if transaction['time'].hour >= 0 and transaction['time'].hour < 5:
        return True
    
    # Rule 4: If the transaction is made using a new device that has not been used before, it is considered fraudulent
    if transaction['device'] not in transaction['user_devices']:
        return True
    
    # If none of the rules are triggered, the transaction is considered safe
    return False