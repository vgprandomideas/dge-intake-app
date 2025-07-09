import streamlit as st
import json
import os

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

# File to store goods data
DATA_FILE = "dge_goods_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.title("📦 Damaged & Rejected Goods Intake")

# Input fields with unique keys
item_name = st.text_input("Item Name", key="item_name_input")
hs_code = st.text_input("HS Code", key="hs_code_input")
quantity = st.number_input("Quantity", min_value=1, key="quantity_input")
port = st.text_input("Port of Rejection", key="port_input")
reason = st.text_area("Reason for Rejection", key="reason_input")
image = st.file_uploader("Upload Item Image (optional)", type=["jpg", "png", "jpeg"], key="image_upload")

# Submit logic
if st.button("Submit"):
    entry = {
        "item_name": item_name,
        "hs_code": hs_code,
        "quantity": quantity,
        "port": port,
        "reason": reason
    }
    if image:
        entry["image_name"] = image.name
        with open(os.path.join("uploads", image.name), "wb") as f:
            f.write(image.read())
    data = load_data()
    data.append(entry)
    save_data(data)
    st.success("Item successfully submitted!")

# Display section
st.subheader("🔍 Uploaded Items")

data = load_data()
search_term = st.text_input("Search by Item or Port", key="search_input")

filtered_data = [
    d for d in data if search_term.lower() in d["item_name"].lower() or search_term.lower() in d["port"].lower()
]

for idx, item in enumerate(filtered_data):
    with st.expander(f"📌 {item['item_name']} (Port: {item['port']})"):
        st.markdown(f"**HS Code**: {item['hs_code']}")
        st.markdown(f"**Quantity**: {item['quantity']}")
        st.markdown(f"**Reason**: {item['reason']}")
        if "image_name" in item:
            st.image(os.path.join("uploads", item["image_name"]), width=200)
        if st.button("🗑️ Delete", key=f"delete_{idx}"):
            data.remove(item)
            save_data(data)
            st.success("Item deleted.")
            st.experimental_rerun()
