from datetime import datetime
import os
import pandas as pd
import requests
import streamlit as st

# 1. Page Configuration & Professional Styling
st.set_page_config(
    page_title="ANUAARI MATERIALS | Aari & Craft Supplies",
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
            color: #2d1524 !important;
        }

        .stApp {
            background-color: #faf7f9 !important; 
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

        .custom-scrollbar::-webkit-scrollbar {
            height: 6px;
            width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 3px;
        }

        /* Product Card Styling */
        div[data-testid="stVerticalBlock"] div[data-testid="stContainer"] {
            background-color: #ffffff !important;
            border: 1px solid #f3e8f1 !important;
            border-radius: 16px !important;
            padding: 12px !important;
            box-shadow: 0 4px 15px rgba(107, 29, 79, 0.04) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        div[data-testid="stVerticalBlock"] div[data-testid="stContainer"]:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 25px rgba(107, 29, 79, 0.1) !important;
            border-color: #e8d0e4 !important;
        }

        /* Image Frame */
        div[data-testid="stVerticalBlock"] div[data-testid="stContainer"] div[data-testid="stImage"] {
            margin: 0 !important;
            padding: 4px !important;
            width: 100% !important;
            background-color: #fcf9fb !important;
            border-radius: 12px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        [data-testid="stImage"] img {
            width: 100% !important;
            height: 150px !important;
            object-fit: contain !important;
            object-position: center center !important;
            border-radius: 8px !important;
            display: block !important;
        }

        /* Buttons Styling */
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #6b1d4f 0%, #53143c 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            border-radius: 12px !important;
            padding: 0.4rem 0.8rem !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(107, 29, 79, 0.2) !important;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #53143c 0%, #3a0d29 100%) !important;
            opacity: 0.95;
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
            border-radius: 20px;
            background: #ffffff !important;
            border: 1px solid #f3e8f1 !important;
            box-shadow: 0 10px 30px -5px rgba(107, 29, 79, 0.08);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Session States safely
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "user_phone" not in st.session_state:
    st.session_state.user_phone = None
if "cart" not in st.session_state or not isinstance(st.session_state.cart, dict):
    st.session_state.cart = {}
if "current_view" not in st.session_state:
    st.session_state.current_view = "Home"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyftApEC3eQJvJPF0tCSX7eFwAG52IinpEhQtlxhmVaOtpbc1J83zJZIhs9XRDRCezCZA/exec"


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
        <div style="background: #ffffff; padding: 24px; border-radius: 16px; text-align: center; border: 1px solid #f3e8f1; box-shadow: 0 6px 20px rgba(107,29,79,0.04); margin-bottom: 20px; max-width: 420px; margin-left: auto; margin-right: auto;">
            <div style="display: inline-block; background: rgba(107,29,79,0.1); color: #6b1d4f; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Exclusive Store</div>
            <div style="font-size: 24px; font-weight: 900; letter-spacing: 0.5px; color: #6b1d4f; text-transform: uppercase; margin: 0;">ANUAARI MATERIALS</div>
            <div style="font-size: 13px; font-weight: 700; color: #d97706; text-transform: lowercase; font-style: italic; letter-spacing: 0.5px; margin-top: 4px;">aari work supplies</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, login_col, _ = st.columns([1, 1.8, 1])

    with login_col:
        st.markdown(
            """
            <div class="login-card">
                <div style="font-size: 16px; font-weight: 800; color: #0f172a; margin-bottom: 2px; text-align: center;">Customer Sign In</div>
                <div style="font-size: 12px; color: #64748b; font-weight: 500; margin-bottom: 16px; text-align: center;">
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
logo_col, nav_col1, nav_col2, nav_col3 = st.columns([3.2, 1, 1, 1], gap="small")

with logo_col:
    st.markdown(
        f"""
        <div style="background: #ffffff; padding: 10px 16px; border-radius: 12px; border: 1px solid #f3e8f1; display: inline-block; box-shadow: 0 2px 8px rgba(107,29,79,0.03);">
            <span style="font-size: 18px; font-weight: 900; color: #6b1d4f; text-transform: uppercase; letter-spacing: 0.5px;">ANUAARI MATERIALS</span>
            <span style="font-size: 12px; font-weight: 700; color: #d97706; font-style: italic; margin-left: 6px;">aari supplies</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = "Home"
        st.rerun()

with nav_col2:
    total_cart_items = sum(st.session_state.cart.values()) if isinstance(st.session_state.cart, dict) else 0
    if st.button(f"🛒 Cart ({total_cart_items})", use_container_width=True):
        st.session_state.current_view = "Cart"
        st.rerun()

with nav_col3:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown("<hr style='margin: 14px 0 16px 0; border: none; border-top: 1px solid #f0e1ec;'>", unsafe_allow_html=True)


# Load Inventory Directly from Google Sheets
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

            img_val = str(row.iloc[5]).strip() if len(row) > 5 and pd.notna(row.iloc[5]) else ""
            desc_val = str(row.iloc[6]).strip() if len(row) > 6 and pd.notna(row.iloc[6]) else ""
            if desc_val.lower() == "nan":
                desc_val = ""

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
                "description": desc_val,
                "stock": "In Stock",
            })
    except Exception:
        product_records = []

if not product_records:
    product_records = [
        {"id": "AB0001", "name": "Hanging Beads Oval Shape Readymade Hook Glassy Color", "category": "Beads", "price": "90.00", "colors": "Red, Blue, Green", "image": "", "description": "High quality glassy finish beads for grand aari embroidery work.", "stock": "In Stock"}
    ]


def process_cart_checkout(address: str, payment_method: str, secondary_phone: str, description: str) -> str:
    if not st.session_state.cart:
        return "Your cart is empty."
    customer_name = st.session_state.logged_in_user
    primary_phone = st.session_state.user_phone
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cart_summary = ", ".join([f"{qty} Units of {item}" for item, qty in st.session_state.cart.items()])

    try:
        order_data = {
            "Type": "Order",
            "Timestamp": timestamp,
            "Customer_Name": customer_name,
            "Primary_Phone": primary_phone,
            "Items": cart_summary,
            "Address": address,
            "Payment_Method": payment_method,
            "Secondary_Phone": secondary_phone,
            "Description": description,
        }
        requests.post(GOOGLE_SCRIPT_URL, json=order_data)
    except Exception as e:
        print(f"Order sheet error: {e}")

    st.session_state.cart = {}
    return f"Order placed successfully ({payment_method}) for: {cart_summary}."


# --- STOREFRONT CATALOG VIEW ---
if st.session_state.current_view == "Home":
    categories = list(set([p["category"] for p in product_records if p["category"]]))
    if not categories:
        categories = ["General"]
        
    if st.session_state.selected_category not in categories:
        st.session_state.selected_category = categories[0]

    # Category Selection Header & Tabs
    cat_top_col1, cat_top_col2 = st.columns([3, 1])
    with cat_top_col1:
        st.markdown("<span style='color: #6b1d4f; font-weight: 800; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;'>📁 Master Categories</span>", unsafe_allow_html=True)
    with cat_top_col2:
        st.markdown(f"<div style='text-align: right; font-size: 12px; font-weight: 600; color: #64748b;'>Welcome, {st.session_state.logged_in_user}</div>", unsafe_allow_html=True)

    for i in range(0, len(categories), 5):
        cat_cols = st.columns(5, gap="small")
        cat_batch = categories[i : i + 5]
        
        for idx, cat in enumerate(cat_batch):
            with cat_cols[idx]:
                is_selected = (st.session_state.selected_category == cat)
                button_label = f"📂 {cat}" if is_selected else cat
                
                if st.button(button_label, key=f"cat_btn_{i}_{idx}", use_container_width=True):
                    st.session_state.selected_category = cat
                    st.rerun()

    st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #f0e1ec;'>", unsafe_allow_html=True)

    # Product Section Header
    current_cat = st.session_state.get("selected_category", categories[0])
    filtered_items = [p for p in product_records if p["category"] == current_cat]

    grid_head_col1, grid_head_col2 = st.columns([3, 1])
    with grid_head_col1:
        st.markdown(f"<h3 style='margin: 0; font-size: 18px; font-weight: 900; color: #0f172a;'>{current_cat}</h3>", unsafe_allow_html=True)
    with grid_head_col2:
        st.markdown(f"<div style='text-align: right;'><span style='background: rgba(107,29,79,0.1); color: #6b1d4f; font-weight: 700; font-size: 12px; padding: 4px 12px; border-radius: 20px;'>{len(filtered_items)} items</span></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # 4-Column Product Grid
    if filtered_items:
        for i in range(0, len(filtered_items), 4):
            cols = st.columns(4, gap="medium")
            batch = filtered_items[i : i + 4]
            
            for col_idx, prod in enumerate(batch):
                with cols[col_idx]:
                    with st.container(border=True):
                        global_idx = i + col_idx
                        img_path = prod.get('image', '')
                        desc_text = prod.get('description', '')

                        # Split card inner content into Image (left) and Description (right)
                        card_col_img, card_col_desc = st.columns([1, 1], gap="small")

                        with card_col_img:
                            try:
                                if img_path:
                                    st.image(img_path, use_container_width=True)
                                else:
                                    st.markdown("<div style='text-align:center; padding:50px 0; background:#fcf9fb; color:#94a3b8; font-size:11px; font-weight:700; border-radius:8px;'>No Image</div>", unsafe_allow_html=True)
                            except Exception:
                                st.markdown("<div style='text-align:center; padding:50px 0; background:#fcf9fb; color:#94a3b8; font-size:11px; font-weight:700; border-radius:8px;'>Error</div>", unsafe_allow_html=True)

                        with card_col_desc:
                            st.markdown(
                                f"<div style='font-size: 11px; font-weight: 600; color: #475569; background: #f8fafc; padding: 6px; border-radius: 8px; height: 150px; overflow-y: auto; border: 1px solid #e2e8f0;'>"
                                f"<strong>Details:</strong><br>{desc_text if desc_text else 'No additional details available.'}"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        
                        # Product Name
                        st.markdown(
                            f"<div style='font-weight: 700; font-size: 12px; color: #0f172a; height: 38px; overflow: hidden; margin-top: 8px; line-height: 1.3;'>"
                            f"{prod['name']}"
                            f"</div>", 
                            unsafe_allow_html=True
                        )

                        # Pricing Section
                        st.markdown(
                            f"<div style='font-weight: 800; font-size: 14px; color: #dc2626; margin-bottom: 8px;'>"
                            f"Rs. {prod['price']} <span style='font-size: 11px; color: #94a3b8; text-decoration: line-through; font-weight: 600; margin-left: 4px;'>Rs. 160.00</span>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )

                        # Color Dropdown Options Parser (Supports comma, backslash, ampersand)
                        raw_colors = prod.get('colors', '')
                        for sep in ['\\', ',', '&']:
                            raw_colors = raw_colors.replace(sep, '|')
                        color_list = [c.strip() for c in raw_colors.split('|') if c.strip()]
                        selected_color = color_list[0] if color_list else "Standard"

                        if color_list:
                            selected_color = st.selectbox(
                                "Options", 
                                color_list, 
                                key=f"color_{global_idx}", 
                                label_visibility="collapsed"
                            )

                        # Item Key for Cart Storage
                        item_key = f"{prod['name']} ({selected_color})"
                        current_qty = st.session_state.cart.get(item_key, 0)

                        # Quantity Stepper Layout ([ - ] [ Qty ] [ + ])
                        q_col1, q_col2, q_col3 = st.columns([1, 1.2, 1], gap="small")
                        
                        with q_col1:
                            if st.button("➖", key=f"minus_{global_idx}", use_container_width=True):
                                if current_qty > 0:
                                    st.session_state.cart[item_key] = current_qty - 1
                                    if st.session_state.cart[item_key] == 0:
                                        del st.session_state.cart[item_key]
                                    st.rerun()

                        with q_col2:
                            st.markdown(
                                f"<div style='text-align: center; font-weight: 800; font-size: 13px; padding-top: 6px; color: #6b1d4f;'>{current_qty}</div>",
                                unsafe_allow_html=True
                            )

                        with q_col3:
                            if st.button("➕", key=f"plus_{global_idx}", use_container_width=True):
                                st.session_state.cart[item_key] = current_qty + 1
                                st.rerun()

                        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No items found in this category.")

else:
    # --- CART & CHECKOUT VIEW ---
    st.subheader("🛒 Shopping Cart & Secure Checkout")
    if st.session_state.cart:
        for item_desc, qty in list(st.session_state.cart.items()):
            col_item, col_rem = st.columns([4, 1])
            with col_item:
                st.markdown(f"• **{item_desc}** — Quantity: **{qty} Units**")
            with col_rem:
                if st.button("Remove", key=f"rem_{item_desc}"):
                    del st.session_state.cart[item_desc]
                    st.rerun()

        st.markdown("---")
        with st.form("checkout_form"):
            address = st.text_area("Delivery Address (with Pincode):")
            sec_phone = st.text_input("Alternative Contact Number:", max_chars=10)
            payment_option = st.radio("Select Payment Method:", ["Cash on Delivery (COD)", "Prepaid (UPI / Cards)"], horizontal=True)
            notes = st.text_area("Custom Instructions / Notes:")

            if st.form_submit_button("Complete Order Now"):
                if address and len(sec_phone) == 10:
                    res_msg = process_cart_checkout(address, payment_option, sec_phone, notes)
                    st.success(res_msg)
                    st.session_state.current_view = "Home"
                    st.rerun()
                else:
                    st.warning("Please provide a valid address and a 10-digit alternative phone number.")
    else:
        st.info("Your cart is empty. Click Home to browse products.")
