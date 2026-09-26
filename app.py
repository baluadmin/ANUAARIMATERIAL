from datetime import datetime
import csv
import os
import re
import chromadb
import pandas as pd
import requests
import streamlit as st

# 1. Streamlit Page Configuration & Enterprise Styling
st.set_page_config(
    page_title="ANUAARIMATERIAL E-Commerce Store",
    page_icon="🧵",
    layout="wide",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            font-size: 15px !important;
            color: #0f172a !important;
        }

        .stApp {
            background-color: #f8fafc !important; 
        }

        #MainMenu, header, footer {visibility: hidden; display: none !important;}
        div[data-testid="stToolbar"], section[data-testid="stStatusWidget"] {display: none !important;}
        .stAppDeployButton {display: none !important; visibility: hidden !important;}
        header[data-testid="stHeader"] {display: none !important; visibility: hidden !important;}
        div[data-testid="stDecoration"] {display: none !important;}

        .block-container {
            padding-top: 0.8rem !important;
            padding-bottom: 1.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }

        .brand-banner {
            background: linear-gradient(135deg, #1d4ed8 0%, #0284c7 100%) !important;
            padding: 14px 18px !important;
            border-radius: 12px !important;
            text-align: center !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25) !important;
            margin-bottom: 12px !important;
            border: 1px solid #38bdf8 !important;
        }
        .brand-banner .brand-title {
            font-size: 22px !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            margin: 0 0 4px 0 !important;
            text-transform: uppercase !important;
        }
        .brand-banner .brand-phone {
            font-size: 15px !important;
            font-weight: 700 !important;
            color: #e0f2fe !important;
            margin: 0 !important;
        }

        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            background: #ffffff !important;
            color: #0f172a !important;
            border: 1.5px solid #cbd5e1 !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            border-radius: 8px !important;
            padding: 0.45rem 0.75rem !important;
            width: 100% !important;
            display: block !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        }
        div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
            background: #2563eb !important;
            color: #ffffff !important;
            border-color: #1d4ed8 !important;
        }

        .login-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            width: 100%;
        }
        .login-card {
            width: 100%;
            max-width: 450px;
            margin: 0 auto;
            padding: 30px 32px;
            border-radius: 20px;
            background: #ffffff !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            box-shadow: 0 20px 40px -15px rgba(30, 58, 138, 0.12);
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize Session States
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_phone" not in st.session_state:
    st.session_state.user_phone = None
if "cart" not in st.session_state:
    st.session_state.cart = []
if "current_view" not in st.session_state:
    st.session_state.current_view = "Home"
if "selected_menu" not in st.session_state:
    st.session_state.selected_menu = None
if "product_page" not in st.session_state:
    st.session_state.product_page = 0
if "quantities" not in st.session_state:
    st.session_state.quantities = {}

# Google Apps Script Web App Endpoint URL
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyftApEC3eQJvJPF0tCSX7eFwAG52IinpEhQtlxhmVaOtpbc1J83zJZIhs9XRDRCezCZA/exec"

# Database Setup
db_path = "./chroma_db_anuaari"
try:
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name="anuaari_inventory_library")
except Exception as e:
    st.error(f"Error connecting to Database: {e}")
    st.stop()


# Function to log customer login into the "LOGIN" tab via Apps Script
def log_login_to_sheet(name, phone):
    try:
        payload = {
            "Type": "Login",
            "Customer_Name": name,
            "Primary_Phone": phone,
        }
        requests.post(GOOGLE_SCRIPT_URL, json=payload)
    except Exception as e:
        print(f"Login sheet error: {e}")


# --- LOGIN SCREEN ---
if not st.session_state.logged_in_user:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 22px;">
            <div style="font-size: 30px; font-weight: 800; text-transform: uppercase; color: #0f172a;">
                ANUAARIMATERIAL
            </div>
            <p style="font-size: 14px; color: #64748b; font-weight: 600; margin: 0;">
                Aari Work & Embroidery Materials &nbsp;|&nbsp; <span style="color: #0284c7; font-weight: 700;">📞 9840450113</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, login_col, _ = st.columns([1, 2.2, 1])

    with login_col:
        st.markdown(
            """
            <div class="login-card">
                <div style="font-size: 26px; text-align: center; margin-bottom: 10px;">🧵</div>
                <div style="font-size: 21px; font-weight: 800; color: #0f172a; margin-bottom: 4px; text-align: center;">Welcome Customer</div>
                <div style="font-size: 13px; color: #64748b; font-weight: 500; margin-bottom: 18px; text-align: center;">
                    Enter your details to explore collections & order supplies
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("customer_login_form", clear_on_submit=False):
            cust_name = st.text_input("Customer Name:", placeholder="e.g. Anusha")
            raw_phone = st.text_input("10-Digit Mobile Number:", max_chars=10, placeholder="9840450113")
            cust_phone = "".join([char for char in raw_phone if char.isdigit()])

            login_btn = st.form_submit_button("🚀 Enter Store", use_container_width=True)

            if login_btn:
                if cust_name.strip() and len(cust_phone) == 10:
                    st.session_state.logged_in_user = cust_name.strip()
                    st.session_state.user_phone = cust_phone.strip()
                    
                    log_login_to_sheet(cust_name.strip(), cust_phone.strip())

                    st.success("✅ Login Successful!")
                    st.rerun()
                else:
                    st.warning("⚠️ Please provide your name and an exact 10-digit mobile number.")
    st.stop()


# --- AFTER LOGIN HEADER & NAVIGATION ---
st.markdown(
    """
    <div class="brand-banner">
        <div class="brand-title">ANUAARIMATERIAL E-Commerce</div>
        <div class="brand-phone">📞 Contact: 9840450113</div>
    </div>
""",
    unsafe_allow_html=True,
)

top_comm, top_space, top_c1, top_c2, top_c3 = st.columns([2.2, 0.4, 1.3, 1.3, 1.3], gap="small")
with top_comm:
    st.markdown(
        f"<span style='color: #64748b; font-weight:600;'>Welcome,</span> <span style='color: #2563eb; font-weight:800;'>{st.session_state.logged_in_user}</span> 👋",
        unsafe_allow_html=True,
    )
with top_space:
    st.empty()
with top_c1:
    if st.button("Home", use_container_width=True):
        st.session_state.current_view = "Home"
        st.rerun()
with top_c2:
    cart_count = len(st.session_state.cart)
    if st.button(f"Cart ({cart_count})", use_container_width=True):
        st.session_state.current_view = "Cart"
        st.rerun()
with top_c3:
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown("---")


# Load Inventory Directly from Google Sheets CSV Link (`need inventory model for this ANUAARI` tab)
@st.cache_data(ttl=2)
def load_inventory_from_sheet():
    sheet_csv_url = "https://docs.google.com/spreadsheets/d/1SK6S8tw4KWvwm_sQS6FHMGsSla7RkQ7XFkE7uuf9GRM/gviz/tq?tqx=out:csv&sheet=need+inventory+model+for+this+ANUAARI"
    try:
        df = pd.read_csv(sheet_csv_url)
        df.to_csv("inventory.csv", index=False)
        return df
    except Exception as e:
        if os.path.exists("inventory.csv"):
            return pd.read_csv("inventory.csv")
        return pd.DataFrame()


inv_df = load_inventory_from_sheet()

product_records = []
if not inv_df.empty:
    try:
        inv_df.columns = inv_df.columns.astype(str).str.strip()
        for _, row in inv_df.iterrows():
            product_records.append({
                "id": str(row.iloc[0]).strip(),             # Column A: Item_ID[cite: 3]
                "name": str(row.iloc[2]).strip(),           # Column C: Subcategory / Item Name[cite: 3]
                "category": str(row.iloc[1]).strip(),       # Column B: Category[cite: 3]
                "subcategory": str(row.iloc[2]).strip(),    # Column C: Subcategory[cite: 3]
                "price": str(row.iloc[3]).strip(),          # Column D: Price (INR)[cite: 3]
                "colors": str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else "", # Column E: Color Options[cite: 3]
                "stock": "In Stock",
            })
    except Exception:
        product_records = []

if not product_records:
    product_records = [
        {"id": "AB0001", "name": "AAI", "category": "AAI", "subcategory": "AAI", "price": "10", "colors": "red", "stock": "In Stock"}
    ]


def process_cart_checkout(address: str, secondary_phone: str, description: str) -> str:
    """Checkout all items in the cart and send order data to Google Sheet 'ANUAAARI Orders' tab via Apps Script."""
    if not st.session_state.cart:
        return "Your cart is empty. Please add items first."

    customer_name = st.session_state.logged_in_user
    primary_phone = st.session_state.user_phone
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cart_summary = ", ".join([f"{item['quantity']} of {item['product']}" for item in st.session_state.cart])

    try:
        order_data = {
            "Type": "Order",
            "Timestamp": timestamp,
            "Customer_Name": customer_name,
            "Primary_Phone": primary_phone,
            "Items": cart_summary,
            "Address": address,
            "Secondary_Phone": secondary_phone,
            "Description": description,
        }
        requests.post(GOOGLE_SCRIPT_URL, json=order_data)
    except Exception as e:
        print(f"Order sheet error: {e}")

    st.session_state.cart = []
    return f"Checkout complete! Order placed successfully for: {cart_summary}."


# --- VIEW SWITCHING: HOME VS CART ---
if st.session_state.current_view == "Home":
    col_menu, col_items = st.columns([1, 3], gap="medium")

    # 1. Master Categories Menu Sidebar
    with col_menu:
        st.markdown("<span style='color: #0f172a; font-weight: 800; font-size: 16px;'>Master Categories</span>", unsafe_allow_html=True)
        with st.container(height=650, border=True):
            categories = list(set([p["category"] for p in product_records if p["category"]]))
            if not categories:
                categories = ["AAI"]
                
            if st.session_state.selected_menu not in categories:
                st.session_state.selected_menu = categories[0]

            for cat in categories:
                if st.button(cat, key=f"menu_btn_{cat}", use_container_width=True):
                    st.session_state.selected_menu = cat
                    st.session_state.product_page = 0
                    st.rerun()

    # 2. Product Items & All Subcategories View
    with col_items:
        current_cat = st.session_state.get("selected_menu", categories[0])
        st.markdown(f"<span style='color: #64748b; font-weight: 700;'>Selected Category:</span> <span style='color: #0f172a; font-weight: 800; font-size: 16px;'>{current_cat}</span>", unsafe_allow_html=True)
        
        with st.container(height=650, border=True):
            filtered_items = [p for p in product_records if p["category"] == current_cat]

            if filtered_items:
                st.markdown("---")

                for idx, prod in enumerate(filtered_items):
                    subcat_display = f" | Subcategory: {prod['subcategory']}" if prod.get('subcategory') else ""
                    color_display = f" | Colors: {prod['colors']}" if prod.get('colors') else ""
                    
                    st.markdown(f"<div style='font-weight: 800; font-size: 15px;'>{prod['id']} - {prod['name']}{subcat_display}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color: #2563eb; font-weight: 800; font-size: 15px;'>₹{prod['price']}{color_display} | Stock: {prod['stock']}</div>", unsafe_allow_html=True)

                    if st.button("Add to Cart", key=f"add_cart_{current_cat}_{idx}", use_container_width=True):
                        st.session_state.cart.append({"product": f"{prod['id']} - {prod['name']} ({prod['colors']})", "quantity": "1 Units"})
                        st.success("Added to cart!")
                        st.rerun()
                    st.markdown("<hr style='margin: 6px 0;'>", unsafe_allow_html=True)
            else:
                st.info("No items found in this master category.")

else:
    # --- CART & CHECKOUT VIEW ---
    st.subheader("🛒 Your Shopping Cart & Secure Checkout")
    if st.session_state.cart:
        for c_idx, item in enumerate(st.session_state.cart):
            col_item, col_rem = st.columns([4, 1])
            with col_item:
                st.markdown(f"• **{item['product']}** ({item['quantity']})")
            with col_rem:
                if st.button("Remove", key=f"rem_{c_idx}"):
                    st.session_state.cart.pop(c_idx)
                    st.rerun()

        st.markdown("---")
        with st.form("checkout_form"):
            address = st.text_area("Delivery Address:")
            sec_phone = st.text_input("Alternative Contact Number:", max_chars=10)
            notes = st.text_area("Custom Description / Instructions:")

            if st.form_submit_button("Complete Order"):
                if address and len(sec_phone) == 10:
                    res_msg = process_cart_checkout(address, sec_phone, notes)
                    st.success(res_msg)
                    st.session_state.current_view = "Home"
                    st.rerun()
                else:
                    st.warning("⚠️ Please provide a valid address and a 10-digit alternative phone number.")
    else:
        st.info("Your cart is empty. Click **Home** to browse products.")
