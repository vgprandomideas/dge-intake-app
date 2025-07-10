import streamlit as st
import os
import json

# Ensure 'uploads' folder exists
os.makedirs("uploads", exist_ok=True)

DATA_FILE = "dge_goods_data.json"

CATEGORY_VALUATION = {
    "Electronics": 50,
    "Automobile": 55,
    "Textiles": 40,
    "Furniture": 60,
    "Machinery": 45,
    "Plastic Goods": 35,
    "Chemicals": 30,
    "Food & Beverage": 25,
    "Metals": 50,
    "Paper": 30,
    "Pharmaceuticals": 40,
    "Toys": 35,
    "Glassware": 45,
    "Footwear": 38,
    "Leather Products": 42
}

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.title("📦 Damaged & Rejected Goods Intake")

# Input fields
item_name = st.text_input("Item Name", key="item_name_input")
hs_code = st.text_input("HS Code", key="hs_code_input")
quantity = st.number_input("Quantity", min_value=1, key="quantity_input")
port = st.text_input("Port of Rejection", key="port_input")
reason = st.text_area("Reason for Rejection", key="reason_input")
image = st.file_uploader("Upload Item Image (optional)", type=["jpg", "jpeg", "png"], key="image_input")

# Valuation section
st.subheader("💰 Goods Valuation")
category = st.selectbox("Select Category", list(CATEGORY_VALUATION.keys()), key="category_input")
original_price = st.number_input("Original Price (USD)", min_value=0.0, step=1.0, key="original_price_input")
default_percent = float(CATEGORY_VALUATION[category])
override_percent = st.number_input("Override Valuation % (optional)", value=default_percent, min_value=0.0, max_value=100.0, step=1.0)

valuation_percent = override_percent
valued_price = (valuation_percent / 100.0) * original_price
st.markdown(f"📉 **Valued Price**: ${valued_price:,.2f} based on {valuation_percent:.1f}% valuation")

# SCF Option
require_scf = st.checkbox("📌 Do you need SCF (Supply Chain Finance) on this item?")

# SCF Inputs
scf_amount = None
scf_interest = None
scf_days = None
scf_interest_amount = 0
scf_total_repay = 0

if require_scf:
    st.subheader("🏦 SCF Details")
    max_scf = round(0.6 * valued_price, 2)
    scf_amount = st.number_input("SCF Amount Requested (USD)", min_value=0.0, max_value=max_scf, value=0.0, step=100.0)
    scf_interest = st.number_input("Proposed Interest Rate (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.1)
    scf_days = st.number_input("Number of Days for SCF", min_value=1, max_value=365, value=30)

    scf_interest_amount = (scf_amount * scf_interest * scf_days) / (365 * 100)
    scf_total_repay = scf_amount + scf_interest_amount

    st.markdown(f"🧾 **Interest Payable**: ${scf_interest_amount:,.2f}")
    st.markdown(f"💰 **Total Repayment (Principal + Interest)**: ${scf_total_repay:,.2f}")

# Submission
if st.button("Submit"):
    entry = {
        "item_name": item_name,
        "hs_code": hs_code,
        "quantity": quantity,
        "port": port,
        "reason": reason,
        "category": category,
        "original_price": original_price,
        "valuation_percent": valuation_percent,
        "valued_price": valued_price,
        "scf_required": require_scf
    }

    if image:
        image_path = os.path.join("uploads", image.name)
        with open(image_path, "wb") as f:
            f.write(image.read())
        entry["image_name"] = image.name
    else:
        entry["image_name"] = ""

    if require_scf:
        entry.update({
            "scf_amount": scf_amount,
            "scf_interest_rate": scf_interest,
            "scf_days": scf_days,
            "scf_interest_payable": scf_interest_amount,
            "scf_total_repayment": scf_total_repay
        })

    data = load_data()
    data.append(entry)
    save_data(data)
    st.success("✅ Item successfully submitted!")

# Search and Display
st.subheader("🔍 Uploaded Items")
search_term = st.text_input("Search by Item or Port", key="search_input")

data = load_data()
filtered = [d for d in data if search_term.lower() in d["item_name"].lower() or search_term.lower() in d["port"].lower()]

for idx, item in enumerate(filtered):
    with st.expander(f"📌 {item['item_name']} (Port: {item['port']})"):
        st.markdown(f"**HS Code**: {item['hs_code']}")
        st.markdown(f"**Quantity**: {item['quantity']}")
        st.markdown(f"**Category**: {item['category']}")
        st.markdown(f"**Original Price**: ${item['original_price']}")
        st.markdown(f"**Valuation %**: {item['valuation_percent']}%")
        st.markdown(f"**Valued Price**: ${item['valued_price']}")
        st.markdown(f"**Reason**: {item['reason']}")
        if item.get("scf_required"):
            st.markdown("**📌 SCF Details:**")
            st.markdown(f"- SCF Amount: ${item.get('scf_amount', 0)}")
            st.markdown(f"- Interest Rate: {item.get('scf_interest_rate', 0)}%")
            st.markdown(f"- Days: {item.get('scf_days', 0)}")
            st.markdown(f"- Interest Payable: ${item.get('scf_interest_payable', 0):,.2f}")
            st.markdown(f"- Total Repayment: ${item.get('scf_total_repayment', 0):,.2f}")

        if item.get("image_name"):
            st.image(os.path.join("uploads", item["image_name"]), width=200)

        if st.button("🗑️ Delete", key=f"delete_{idx}"):
            data.remove(item)
            save_data(data)
            st.success("Item deleted.")
            st.experimental_rerun()
