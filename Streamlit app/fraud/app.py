import streamlit as st
import requests
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Quantum Fraud Detector",
    page_icon="🧠",
    layout="centered"
)

# --- Custom CSS Styling ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem;
        color: #1E3A8A;
        margin-bottom: 0.3rem;
        font-weight: 800;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .input-section {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #E5E7EB;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .stButton > button {
        background-color: #1D4ED8;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        padding: 0.6rem 1.2rem;
    }
    .stButton > button:hover {
        background-color: #2563EB;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 class='main-header'>Quantum Fraud Detection</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Analyze transactions using quantum machine learning algorithms</p>", unsafe_allow_html=True)

# --- Session State ---
if 'last_transaction' not in st.session_state:
    st.session_state.last_transaction = None

# --- Input Section ---
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.subheader("🔢 Enter Transaction Details")

# First row of inputs
col1, col2 = st.columns(2)
with col1:
    amount = st.number_input("Transaction Amount ($)", min_value=0.01, step=100.0)
    oldbalanceOrg = st.number_input("Sender's Previous Balance ($)", min_value=0.0, step=100.0)
    newbalanceOrig = st.number_input("Sender's New Balance ($)", min_value=0.0, step=100.0)
with col2:
    oldbalanceDest = st.number_input("Receiver's Previous Balance ($)", min_value=0.0, step=100.0)
    newbalanceDest = st.number_input("Receiver's New Balance ($)", min_value=0.0, step=100.0)

# Additional features section
with st.expander("Additional Transaction Features"):
    col3, col4 = st.columns(2)
    with col3:
        step = st.number_input("Step (Time)", min_value=1, value=1)
        type_transfer = st.checkbox("Is Transfer", value=True)
        type_cash_out = st.checkbox("Is Cash Out")
    with col4:
        type_payment = st.checkbox("Is Payment")
        type_cash_in = st.checkbox("Is Cash In")
        isFraud = st.checkbox("Is Known Fraud (for testing)", value=False)

st.markdown("</div>", unsafe_allow_html=True)

# --- Buttons ---
col5, col6 = st.columns(2)
with col5:
    analyze = st.button("🔍 Analyze Transaction")
with col6:
    clear = st.button("🧹 Clear Fields")

if clear:
    st.experimental_rerun()

# --- Prediction Logic ---
if analyze:
    errors = []
    if amount <= 0:
        errors.append("Amount must be greater than zero.")
    if oldbalanceOrg < newbalanceOrig:
        errors.append("Sender's previous balance cannot be less than new balance.")
    
    if errors:
        for err in errors:
            st.error(err)
    else:
        with st.spinner("🔬 Analyzing with quantum model..."):
            try:
                # Convert checkbox values to numeric
                transfer = 1 if type_transfer else 0
                cash_out = 1 if type_cash_out else 0
                payment = 1 if type_payment else 0
                cash_in = 1 if type_cash_in else 0
                fraud = 1 if isFraud else 0
                
                # Format the features as expected by the API - all 10 features
                features = [
                    step,
                    amount,
                    oldbalanceOrg,
                    newbalanceOrig,
                    oldbalanceDest,
                    newbalanceDest,
                    transfer,
                    cash_out,
                    payment,
                    cash_in
                ]
                
                # Create the payload with the features array
                payload = {
                    "features": features
                }
                
                # Store the original data for display
                original_data = {
                    "step": step,
                    "amount": amount,
                    "oldbalanceOrg": oldbalanceOrg,
                    "newbalanceOrig": newbalanceOrig,
                    "oldbalanceDest": oldbalanceDest,
                    "newbalanceDest": newbalanceDest,
                    "type_transfer": transfer,
                    "type_cash_out": cash_out,
                    "type_payment": payment,
                    "type_cash_in": cash_in
                }
                
                # 🚀 API URL
                api_url = "https://fraud-detector-4bc89302-d5df-459d-a988.ahumain.cranecloud.io/predict"
                
                # Make the API request
                response = requests.post(api_url, json=payload, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                # 🧠 Prediction Display
                st.session_state.last_transaction = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "payload": original_data,
                    "result": result
                }
                
                if "prediction" in result:
                    if result["prediction"] == 1:
                        st.markdown("<div class='result-box' style='background-color:#FEE2E2; border:1px solid #FCA5A5'>", unsafe_allow_html=True)
                        st.error("🚨 FRAUDULENT TRANSACTION DETECTED!")
                        st.markdown("**🛑 Action Suggested:** Block the transaction and flag the account.", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='result-box' style='background-color:#DCFCE7; border:1px solid #6EE7B7'>", unsafe_allow_html=True)
                        st.success("✅ LEGITIMATE TRANSACTION")
                        st.markdown("**Transaction appears safe and can proceed normally.**", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    if "confidence" in result:
                        conf = result["confidence"] * 100 if result["confidence"] <= 1 else result["confidence"]
                        st.progress(int(conf))
                        st.info(f"📊 Model Confidence: {conf:.2f}%")
                else:
                    st.warning("⚠️ No prediction key found in response!")
                    st.json(result)  # Display the actual response for debugging
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Connection Error: Could not connect to the API server. Please check your internet connection.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout Error: The API request took too long to complete. Please try again later.")
            except requests.exceptions.HTTPError as e:
                st.error(f"🌐 HTTP Error: {e}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ API Request Failed: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected Error: {e}")
                st.error(f"Details: {str(e)}")

# --- Last Transaction Summary ---
if st.session_state.last_transaction:
    with st.expander("🧾 Last Transaction Summary"):
        st.write(f"**Time:** {st.session_state.last_transaction['timestamp']}")
        st.write(f"**Details:**")
        st.json(st.session_state.last_transaction["payload"])
        
        # Check if prediction exists in the result
        if "prediction" in st.session_state.last_transaction["result"]:
            prediction_value = st.session_state.last_transaction["result"]["prediction"]
            prediction_text = "Fraudulent" if prediction_value == 1 else "Legitimate"
            st.write(f"**Prediction:** {prediction_text}")
        else:
            st.write("**Prediction:** Not available")
            st.write("**API Response:**")
            st.json(st.session_state.last_transaction["result"])

# --- Footer ---
st.markdown("---")
st.markdown("""
<center style="color: #6B7280; font-size: 1rem;">
    Developed with ❤️ using Quantum Machine Learning <br>
    &copy; 2025 Group_18 | Powered by   College of computing and information sciences, makerere University,PennyLane and Streamlit 
</center>
""", unsafe_allow_html=True)
