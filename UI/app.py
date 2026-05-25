import streamlit as st
import datetime
import pandas as pd
import numpy as np
from SRC.data_handlers import load_users, load_transactions
from SRC.main import process_payment_request, confirm_otp_and_release_vault
from SRC.otp_handler import generate_secure_otp, verify_otp_attempt

# Page Layout Configuration
st.set_page_config(page_title="GuardianShield Client Portal", layout="wide")

# Initialize persistent session state tracking attributes
if "current_otp" not in st.session_state:
    st.session_state.current_otp = None
if "otp_active" not in st.session_state:
    st.session_state.otp_active = False
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "transaction_alert_message" not in st.session_state:
    st.session_state.transaction_alert_message = None
if "transaction_alert_type" not in st.session_state:
    st.session_state.transaction_alert_type = None

st.title("🏦 GuardianShield Personal Banking Portal")
st.markdown("---")

# 1. IDENTITY ACCESS GATEWAY (Login Bar)
try:
    df_users = load_users()
    all_users = sorted(df_users['user_id'].astype(str).str.strip().tolist())
except Exception as e:
    st.error(f"Failed to access user ledger database: {e}")
    all_users = []

user_search = st.text_input("🔑 System Access Portal - Enter Your User ID (e.g., U101):", placeholder="Type your account ID to unlock dashboard...")

if user_search:
    clean_input = user_search.strip().upper()
    matched_search = [u for u in all_users if clean_input in u]
    
    if clean_input in all_users:
        st.session_state.logged_in_user = clean_input
        st.success(f"🔐 Identity Verified: Welcome back, {df_users[df_users['user_id'] == clean_input]['account_holder'].values[0]}!")
    else:
        st.session_state.logged_in_user = None
        if matched_search:
            st.caption(f"💡 Did you mean: {', '.join(matched_search)}?")
        st.markdown(
            '<p style="color: #FF4B4B; background-color: #FFEBEB; padding: 8px; border-radius: 4px; border: 1px solid #FF4B4B;">❌ Account ID not found in system directory.</p>', 
            unsafe_allow_html=True
        )
else:
    st.session_state.logged_in_user = None
    st.info("Please input your unique Account ID above to verify your identity session.")

# 2. RUN TIME DYNAMIC DASHBOARD
if st.session_state.logged_in_user:
    current_uid = st.session_state.logged_in_user
    user_profile = df_users[df_users['user_id'] == current_uid].iloc[0]
    
    st.markdown("---")
    st.markdown(f"## 📊 Account Analytics Hub: {user_profile['account_holder']}")
    
    # Financial Overview Metric Cards
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric(label="Available Balance", value=f"${float(user_profile['current_balance']):,.2f}")
    with m_col2:
        status_color = "🟢" if user_profile['account_status'] == "ACTIVE" else "🔴"
        st.metric(label="Account Status Flags", value=f"{status_color} {user_profile['account_status']}")
    with m_col3:
        st.metric(label="Registered Home City", value=str(user_profile['home_location']))
    with m_col4:
        st.metric(label="Trusted Hardware Device ID", value=str(user_profile['trusted_device_id']))

    try:
        df_txns = load_transactions()
        user_history = df_txns[df_txns["from_user_id"] == current_uid].copy()
    except:
        user_history = pd.DataFrame()

    col_graphs, col_actions = st.columns([3, 2])
    
    with col_graphs:
        st.markdown("### 📈 Historical Spending Fingerprint")
        if not user_history.empty and len(user_history) >= 1:
            user_history["amount"] = user_history["amount"].astype(float)
            user_history = user_history.tail(10)
            st.bar_chart(data=user_history, x="to_user_id", y="amount", use_container_width=True)
            st.caption("Figure 1.0: Distribution map showing the value sizes of recent outgoing peer settlements.")
        else:
            st.info("💡 No historical transaction footprint records found for this account layout profile.")

    with col_actions:
        st.markdown("### 💸 Initiate Outgoing Transfer")
        
        # Recipient Selection
        recipient_pool = [u for u in all_users if u != current_uid]
        recipient_input = st.text_input("🎯 Target Recipient ID:", placeholder="Search destination accounts...")
        
        recipient_valid = False
        target_recipient_display = "______"
        if recipient_input:
            clean_rec = recipient_input.strip().upper()
            matched_rec = [u for u in recipient_pool if clean_rec in u]
            
            if clean_rec in recipient_pool:
                recipient_valid = True
                target_recipient_display = clean_rec
            elif clean_rec == current_uid:
                st.markdown('<p style="color: #FF4B4B; background-color: #FFEBEB; padding: 8px; border-radius: 4px;">❌ Self-transfers are rejected.</p>', unsafe_allow_html=True)
            else:
                if matched_rec:
                    st.caption(f"💡 Suggested: {', '.join(matched_rec)}")
                st.markdown('<p style="color: #FF4B4B; background-color: #FFEBEB; padding: 8px; border-radius: 4px;">❌ Invalid recipient ID target.</p>', unsafe_allow_html=True)

        # Step value set to support fractional numeric entry cleanly
        amount = st.number_input("💵 Transfer Value ($):", min_value=0.0, step=0.0000001, format="%.7f")

        # --- 12-HOUR TIME FRAME SELECTOR ---
        st.markdown("##### ⏰ Execution Time Frame")
        time_col1, time_col2, time_col3 = st.columns([1, 1, 1])
        with time_col1:
            hour_12 = st.slider("Hour:", min_value=1, max_value=12, value=12)
        with time_col2:
            minutes = st.slider("Minute:", min_value=0, max_value=59, value=0)
        with time_col3:
            am_pm = st.radio("Period:", ["AM", "PM"], horizontal=True, index=0)

        # Convert selection parameters to 24-hour timestamp system integers
        if am_pm == "PM" and hour_12 != 12:
            txn_hour = hour_12 + 12
        elif am_pm == "AM" and hour_12 == 12:
            txn_hour = 0
        else:
            txn_hour = hour_12

        device_used = st.selectbox("📱 Telemetry Device Signature:", ["iPhone15", "OnePlus_11R", "Pixel_8_Pro", "Samsung_S24", "MacBookPro_M3", "iPhone14_Pro", "Galaxy_U1", "iPad_Air", "Nothing_Phone_2", "iPhone13_Mini", "Hacker_Linux_Terminal"])
        processing_location = st.selectbox("📍 Execution Processing City Geolocation:", ["Mumbai", "Bengaluru", "New Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow", "Goa"])

        # Sticky Notification Window
        if st.session_state.transaction_alert_message:
            if st.session_state.transaction_alert_type == "SUCCESS":
                st.success(st.session_state.transaction_alert_message)
                if st.button("🔄 Pay Again / Back to Home", use_container_width=True):
                    st.session_state.transaction_alert_message = None
                    st.session_state.transaction_alert_type = None
                    st.session_state.otp_active = False
                    st.session_state.current_otp = None
                    st.rerun()
            else:
                if st.session_state.transaction_alert_type == "ERROR":
                    st.error(st.session_state.transaction_alert_message)
                elif st.session_state.transaction_alert_type == "WARNING":
                    st.warning(st.session_state.transaction_alert_message)
                
                if st.button("🗑️ Dismiss Notification Window", use_container_width=True):
                    st.session_state.transaction_alert_message = None
                    st.session_state.transaction_alert_type = None
                    st.rerun()

        # Dynamic Button Text Generation
        button_label = f"💸 Pay ${amount:.7f} from {current_uid} to {target_recipient_display}"
        button_ready = recipient_valid and amount > 0 and (not st.session_state.otp_active)
        
        if st.button(button_label, disabled=not button_ready, use_container_width=True):
            status, response_msg = process_payment_request(
                current_uid, 
                recipient_input.strip().upper(), 
                f"{amount:.7f}", 
                txn_hour, 
                device_used, 
                processing_location
            )
            
            if status == "SUCCESS":
                st.session_state.transaction_alert_message = f"Transaction cleared successfully! {response_msg}"
                st.session_state.transaction_alert_type = "SUCCESS"
                st.rerun()
            elif status == "REJECTED":
                st.session_state.transaction_alert_message = f"{response_msg}"
                st.session_state.transaction_alert_type = "ERROR"
                st.rerun()
            elif status == "OTP_REQUIRED":
                generated_pin = generate_secure_otp()
                st.session_state.current_otp = generated_pin
                st.session_state.otp_active = True
                st.session_state.transaction_alert_message = f"Verification Required. {response_msg}"
                st.session_state.transaction_alert_type = "WARNING"
                st.rerun()

        # --- OTP Challenge Container ---
        if st.session_state.otp_active:
            st.markdown(f"""
                <div style='background-color: #FFF3CD; padding: 15px; border-radius: 8px; border-left: 5px solid #FFC107; margin-top: 15px;'>
                    <h4 style='color: #856404; margin: 0;'>🔒 Out-of-Band Validation Shield Engaged</h4>
                    <p style='color: #856404; margin: 5px 0 12px 0;'>Enter the temporary security token to release the transaction vault locks.</p>
                    <div style='background-color: #FFF; padding: 8px 12px; border-radius: 4px; border: 1px dashed #FFC107; font-family: monospace; font-weight: bold; color: #D39E00;'>
                        📲 SIMULATED SMS CHANNEL ALERT FOR {current_uid}: Your 6-Digit Verification Token is Code: {st.session_state.current_otp}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            entered_pin = st.text_input("🔑 Enter Code:", max_chars=6, type="password")
            col_v, col_c = st.columns(2)
            
            with col_v:
                if st.button("✔️ Confirm Token", use_container_width=True):
                    is_valid, validation_msg = verify_otp_attempt(current_uid, entered_pin, st.session_state.current_otp)
                    
                    # FIXED: Safely passing parameters based on your original source file argument counts
                    try:
                        success_release, release_msg = confirm_otp_and_release_vault(is_valid, f"{amount:.7f}")
                    except TypeError:
                        success_release, release_msg = confirm_otp_and_release_vault(is_valid)
                    
                    if is_valid and success_release:
                        st.session_state.transaction_alert_message = f"Payment Authorized: {release_msg}"
                        st.session_state.transaction_alert_type = "SUCCESS"
                        st.session_state.otp_active = False
                        st.session_state.current_otp = None
                        st.rerun()
                    else:
                        if "LOCKED" in validation_msg:
                            st.session_state.transaction_alert_message = f"Account Locked: {validation_msg}"
                            st.session_state.transaction_alert_type = "ERROR"
                            st.session_state.otp_active = False
                            st.session_state.current_otp = None
                        else:
                            error_reason = release_msg if not success_release else validation_msg
                            st.session_state.transaction_alert_message = f"Verification Failed: {error_reason}"
                            st.session_state.transaction_alert_type = "ERROR"
                        st.rerun()
            with col_c:
                if st.button("❌ Break Connection", use_container_width=True):
                    try:
                        confirm_otp_and_release_vault(False, f"{amount:.7f}")
                    except TypeError:
                        confirm_otp_and_release_vault(False)
                    st.session_state.otp_active = False
                    st.session_state.current_otp = None
                    st.session_state.transaction_alert_message = "Transaction canceled by user. Volatile vault memory cleared."
                    st.session_state.transaction_alert_type = "ERROR"
                    st.rerun()