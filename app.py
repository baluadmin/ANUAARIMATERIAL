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
    page_title="ANUAARIMATERIALS E-Commerce Store",
    page_icon="🧵",
    layout="wide",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            font-size: 14px !important;
            color: #1e293b !important;
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
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }

        /* Full Width Edge-to-Edge Product Image Styling */
        [data-testid="stImage"] {
            width: 100% !important;
        }
        [data-testid="stImage"] img {
            width: 100% !important;
            height: 240px !important;
            object-fit: cover !important;
            border-radius: 10px !important;
            display: block !important;
        }

        /* E-Commerce Catalog Pill Button Styling */
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            background: #2b3a97 !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            border-radius: 20px !important;
            padding: 0.45rem 0.75rem !important;
            width: 100% !important;
            display: block !important;
            box-shadow: 0 2px 5px rgba(43, 58, 151, 0.15) !important;
        }
        div.stButton > button:hover {
            background: #1e2975 !important;
            color: #ffffff !important;
        }

        .login-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top: 3rem;
        }
        .login-card {
            width: 100%;
            max-width: 420px;
            padding: 30px;
            border-radius: 16px;
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.08);
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
        <div style="background: #ffffff; padding: 20px; border-radius: 14px; text-align: center; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 20px; max-width: 420px; margin-left: auto; margin-right: auto;">
            <div style="font-size: 26px; font-weight: 900; letter-spacing: 1px; color: #6b1d4f; text-transform: uppercase; margin: 0;">ANUAARI MATERIALS</div>
            <div style="font-size: 15px; font-weight: 700; color: #d97706; text-transform: lowercase; font-style: italic; letter-spacing: 0.5px;">aari work supplies</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, login_col, _ = st.columns([1, 1.8, 1])

    with login_col:
        st.markdown(
            """
            <div class="login-card">
                <div style="font-size: 20px; font-weight: 800; color: #0f172a; margin-bottom: 4px; text-align: center;">Customer Sign In</div>
                <div style="font-size: 13px; color: #64748b; font-weight: 500; margin-bottom: 16px; text-align: center;">
                    Enter your name and mobile number to browse inventory
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("customer_login_form", clear_on_submit=False):
            cust_name = st.text_input("Customer Name:", placeholder="e.g. Anusha")
            raw_phone = st.text_input("10-Digit Mobile Number:", max_chars=10, placeholder="9840450113")
            cust_phone = "".join([char for char in raw_phone if char.isdigit()])

            login_btn = st.form_submit_button("Enter Store", use_container_width=True)

            if login_btn:
                if cust_name.strip() and len(cust_phone) == 10:
                    st.session_state.logged_in_user = cust_name.strip()
                    st.session_state.user_phone = cust_phone.strip()
                    log_login_to_sheet(cust_name.strip(), cust_phone.strip())
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.warning("Please provide your name and an exact 10-digit mobile number.")
    st.stop()


# --- HEADER & NAVIGATION BAR ---
logo_col, nav_col1, nav_col2, nav_col3 = st.columns([3.5, 1, 1, 1], gap="small")

with logo_col:
    st.markdown(
        """
        <div style="background: #ffffff; padding: 10px 14px; border-radius: 10px; border: 1px solid #e2e8f0; display: inline-block;">
            <span style="font-size: 20px; font-weight: 900; color: #6b1d4f; text-transform: uppercase; letter-spacing: 0.5px;">ANUAARI MATERIALS</span>
            <span style="font-size: 13px; font-weight: 700; color: #d97706; font-style: italic; margin-left: 8px;">aari work supplies</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col1:
    if st.button("Home", use_container_width=True):
        st.session_state.current_view = "Home"
        st.rerun()

with nav_col2:
    cart_count = len(st.session_state.cart)
    if st.button(f"Cart ({cart_count})", use_container_width=True):
        st.session_state.current_view = "Cart"
        st.rerun()

with nav_col3:
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown("<hr style='margin: 14px 0 16px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)


# Load Inventory Directly from Google Sheets CSV Link
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
            cat_val = str(row.iloc[1]).strip()
            if not cat_val or cat_val.lower() == "nan":
                cat_val = "General"

            # Grab primary image from Column F (index 5)
            img_val = str(row.iloc[5]).strip() if len(row) > 5 and pd.notna(row.iloc[5]) else ""
            loc_path = f"images/{img_val}"
            if img_val and img_val.lower() != "nan":
                if os.path.exists(img_val):
                    main_img = img_val
                elif os.path.exists(loc_path):
                    main_img = loc_path
                else:
                    main_img = img_val
            else:
                main_img = ""

            product_records.append({
                "id": str(row.iloc[0]).strip(),
                "name": str(row.iloc[2]).strip(),
                "category": cat_val,
                "price": str(row.iloc[3]).strip(),
                "colors": str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else "",
                "image": main_img,
                "stock": "In Stock",
            })
    except Exception:
        product_records = []

if not product_records:
    product_records = [
        {"id": "AB0001", "name": "Sample Item", "category": "General", "price": "130.00", "colors": "red, blue", "image": "", "stock": "In Stock"}
    ]


def process_cart_checkout(address: str, secondary_phone: str, description: str) -> str:
    if not st.session_state.cart:
        return "Your cart is empty."
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
    return f"Order placed successfully for: {cart_summary}."


# --- VIEW SWITCHING ---
if st.session_state.current_view == "Home":
    categories = list(set([p["category"] for p in product_records if p["category"]]))
    if not categories:
        categories = ["General"]
        
    if st.session_state.selected_menu not in categories:
        st.session_state.selected_menu = categories[0]

    # --- CATEGORY PILLS BAR ---
    st.markdown("<span style='color: #475569; font-weight: 700; font-size: 13px; text-transform: uppercase;'>Categories</span>", unsafe_allow_html=True)
    
    for i in range(0, len(categories), 5):
        cat_cols = st.columns(5, gap="small")
        cat_batch = categories[i : i + 5]
        
        for idx, cat in enumerate(cat_batch):
            with cat_cols[idx]:
                is_selected = (st.session_state.selected_menu == cat)
                button_label = f"📁 {cat}" if is_selected else cat
                
                if st.button(button_label, key=f"cat_btn_{i}_{idx}", use_container_width=True):
                    st.session_state.selected_menu = cat
                    st.rerun()

    st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

    # --- 4-COLUMN CATALOG GRID ---
    current_cat = st.session_state.get("selected_menu", categories[0])
    filtered_items = [p for p in product_records if p["category"] == current_cat]

    if filtered_items:
        for i in range(0, len(filtered_items), 4):
            cols = st.columns(4, gap="medium")
            batch = filtered_items[i : i + 4]
            
            for col_idx, prod in enumerate(batch):
                with cols[col_idx]:
                    with st.container(border=True):
                        global_idx = i + col_idx
                        img_path = prod.get('image', '')

                        # Full Screen Edge-to-Edge Image Display
                        try:
                            if img_path:
                                st.image(img_path, use_container_width=True)
                            else:
                                st.markdown("<div style='text-align:center; padding:70px 0; color:#94a3b8;'>No Image</div>", unsafe_allow_html=True)
                        except Exception:
                            st.markdown("<div style='text-align:center; padding:70px 0; color:#94a3b8;'>Image Error</div>", unsafe_allow_html=True)
                        
                        # Product Name (Clean multi-line display matching reference)[cite: 12]
                        st.markdown(
                            f"<div style='text-align: center; font-weight: 600; font-size: 13px; color: #1e293b; height: 44px; overflow: hidden; margin-top: 8px; line-height: 1.3;'>"
                            f"{prod['name']}"
                            f"</div>", 
                            unsafe_allow_html=True
                        )

                        # Catalog Pricing Style (Red current price)[cite: 12]
                        st.markdown(
                            f"<div style='text-align: center; font-weight: 800; font-size: 15px; color: #dc2626; margin-bottom: 8px;'>"
                            f"Rs. {prod['price']}"
                            f"</div>", 
                            unsafe_allow_html=True
                        )

                        # Color Dropdown Options
                        raw_colors = prod.get('colors', '')
                        color_list = [c.strip() for c in raw_colors.replace('&', ',').split(',') if c.strip()]
                        selected_color = color_list[0] if color_list else "Standard"

                        if color_list:
                            selected_color = st.selectbox(
                                "Options", 
                                color_list, 
                                key=f"color_{global_idx}", 
                                label_visibility="collapsed"
                            )

                        # Add to Cart Button (Pill shaped navy blue matching reference)[cite: 12]
                        btn_label = "Select Options" if color_list else "Add To Cart"
                        if st.button(btn_label, key=f"cart_{global_idx}", use_container_width=True):
                            item_desc = f"{prod['id']} - {prod['name']} ({selected_color})"
                            st.session_state.cart.append({"product": item_desc, "quantity": "1 Units"})
                            st.success("Added to cart!")
                            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No items found in this category.")

else:
    # --- CART & CHECKOUT VIEW ---
    st.subheader("🛒 Shopping Cart & Checkout")
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
                    st.warning("Please provide a valid address and a 10-digit alternative phone number.")
    else:
        st.info("Your cart is empty. Click Home to browse products.")
