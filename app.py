from datetime import datetime
import base64
import os
import random
import pandas as pd
import requests
import streamlit as st

# 1. Page Configuration & Styling
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
            padding-top: 0.8rem !important;
            padding-bottom: 2rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
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
            padding: 10px !important;
            box-shadow: 0 4px 15px rgba(107, 29, 79, 0.04) !important;
            margin-bottom: 10px;
        }

        /* Direct Clickable Zoom Image */
        .zoom-thumb {
            width: 100%;
            height: 140px;
            object-fit: contain;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s ease, opacity 0.2s ease;
            display: block;
        }
        .zoom-thumb:hover {
            opacity: 0.85;
            transform: scale(1.03);
        }

        /* Lightbox Overlay */
        .lightbox-overlay {
            display: none;
            position: fixed;
            z-index: 999999;
            left: 0;
            top: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(20, 5, 15, 0.85);
            backdrop-filter: blur(4px);
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .lightbox-overlay:target {
            display: flex;
        }
        .lightbox-img {
            max-width: 90vw;
            max-height: 85vh;
            object-fit: contain;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            animation: zoomIn 0.25s ease-out;
            cursor: default;
        }
        .close-hint {
            position: absolute;
            top: 20px;
            right: 25px;
            color: #ffffff;
            font-size: 28px;
            font-weight: bold;
            text-decoration: none;
            background: rgba(0,0,0,0.4);
            border-radius: 50%;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        @keyframes zoomIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        /* Buttons Styling - Touch Friendly for Mobile */
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #6b1d4f 0%, #53143c 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            border-radius: 12px !important;
            padding: 0.5rem 0.8rem !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(107, 29, 79, 0.2) !important;
            min-height: 40px !important;
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
            padding-top: 2rem;
        }
        .login-card {
            width: 100%;
            max-width: 420px;
            padding: 20px;
            border-radius: 20px;
            background: #ffffff !important;
            border: 1px solid #f3e8f1 !important;
            box-shadow: 0 10px 30px -5px rgba(107, 29, 79, 0.08);
        }

        /* Mobile Adjustments */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
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
if "shuffled_seed" not in st.session_state:
    st.session_state.shuffled_seed = random.randint(1, 10000)

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


def get_image_src(image_path):
    if not image_path:
        return ""
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode("utf-8")
                ext = image_path.split(".")[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                return f"data:{mime};base64,{b64}"
        except Exception:
            return ""
    return image_path


# --- LOGIN SCREEN ---
if not st.session_state.logged_in_user:
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: #ffffff; padding: 20px; border-radius: 16px; text-align: center; border: 1px solid #f3e8f1; box-shadow: 0 6px 20px rgba(107,29,79,0.04); margin-bottom: 20px; width: 100%; max-width: 420px; margin-left: auto; margin-right: auto;">
            <div style="display: inline-block; background: rgba(107,29,79,0.1); color: #6b1d4f; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">Exclusive Store</div>
            <div style="font-size: 22px; font-weight: 900; letter-spacing: 0.5px; color: #6b1d4f; text-transform: uppercase; margin: 0;">ANUAARI MATERIALS</div>
            <div style="font-size: 13px; font-weight: 700; color: #d97706; text-transform: lowercase; font-style: italic; letter-spacing: 0.5px; margin-top: 4px;">aari work supplies</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, login_col, _ = st.columns([0.1, 2.8, 0.1])

    with login_col:
        with st.form("customer_login_form", clear_on_submit=False):
            cust_name = st.text_input("Customer Name:", placeholder="")
            raw_phone = st.text_input("10-Digit Mobile Number:", max_chars=10, placeholder="")
            cust_phone = "".join([char for char in raw_phone if char.isdigit()])

            login_btn = st.form_submit_button("Enter Store", use_container_width=True)

            if login_btn:
                if cust_name.strip() and len(cust_phone) == 10:
                    st.session_state.logged_in_user = cust_name.strip()
                    st.session_state.user_phone = cust_phone.strip()
                    st.session_state.shuffled_seed = random.randint(1, 10000)  # Shuffle on login
                    log_login_to_sheet(cust_name.strip(), cust_phone.strip())
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.warning("Please provide your name and an exact 10-digit mobile number.")
    st.stop()


# --- HEADER & NAVIGATION BAR ---
logo_col, nav_col1, nav_col2, nav_col3 = st.columns([2.5, 1, 1, 0.8], gap="small")

with logo_col:
    st.markdown(
        f"""
        <div style="background: #ffffff; padding: 8px 12px; border-radius: 12px; border: 1px solid #f3e8f1; display: inline-block; box-shadow: 0 2px 8px rgba(107,29,79,0.03);">
            <span style="font-size: 15px; font-weight: 900; color: #6b1d4f; text-transform: uppercase; letter-spacing: 0.5px;">ANUAARI MATERIALS</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with nav_col1:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = "Home"
        st.session_state.selected_category = None  # Reset category view on Home click
        st.session_state.shuffled_seed = random.randint(1, 10000)  # Re-shuffle products on home click
        st.rerun()

with nav_col2:
    total_cart_items = sum(st.session_state.cart.values()) if isinstance(st.session_state.cart, dict) else 0
    if st.button(f"🛒 Cart ({total_cart_items})", use_container_width=True):
        st.session_state.current_view = "Cart"
        st.rerun()

with nav_col3:
    if st.button("🚪", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown("<hr style='margin: 12px 0 14px 0; border: none; border-top: 1px solid #f0e1ec;'>", unsafe_allow_html=True)


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

    # Category Selection Header & Tabs
    st.markdown("<span style='color: #6b1d4f; font-weight: 800; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;'>Category</span>", unsafe_allow_html=True)

    for i in range(0, len(categories), 3):
        cat_cols = st.columns(3, gap="small")
        cat_batch = categories[i : i + 3]
        
        for idx, cat in enumerate(cat_batch):
            with cat_cols[idx]:
                is_selected = (st.session_state.selected_category == cat)
                button_label = f"📂 {cat}" if is_selected else cat
                
                if st.button(button_label, key=f"cat_btn_{i}_{idx}", use_container_width=True):
                    st.session_state.selected_category = cat
                    st.rerun()

    st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #f0e1ec;'>", unsafe_allow_html=True)

    # Filter or Shuffle Products
    if st.session_state.selected_category:
        filtered_items = [p for p in product_records if p["category"] == st.session_state.selected_category]
        header_title = st.session_state.selected_category
    else:
        # Shuffle products randomly when no specific category is selected
        filtered_items = list(product_records)
        random.seed(st.session_state.shuffled_seed)
        random.shuffle(filtered_items)
        header_title = "Featured Products"

    grid_head_col1, grid_head_col2 = st.columns([2, 1])
    with grid_head_col1:
        st.markdown(f"<h3 style='margin: 0; font-size: 16px; font-weight: 900; color: #0f172a;'>{header_title}</h3>", unsafe_allow_html=True)
    with grid_head_col2:
        st.markdown(f"<div style='text-align: right;'><span style='background: rgba(107,29,79,0.1); color: #6b1d4f; font-weight: 700; font-size: 11px; padding: 3px 10px; border-radius: 20px;'>{len(filtered_items)} items</span></div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    # Responsive 2-Column Grid
    if filtered_items:
        for i in range(0, len(filtered_items), 2):
            cols = st.columns(2, gap="small")
            batch = filtered_items[i : i + 2]
            
            for col_idx, prod in enumerate(batch):
                with cols[col_idx]:
                    with st.container(border=True):
                        global_idx = i + col_idx
                        img_path = prod.get('image', '')
                        desc_text = prod.get('description', '')
                        img_src = get_image_src(img_path)

                        # Compact Image Display
                        if img_src:
                            st.markdown(
                                f"""
                                <a href="#modal_{global_idx}">
                                    <img src="{img_src}" class="zoom-thumb" alt="{prod['name']}" title="Click to Zoom" />
                                </a>
                                <div id="modal_{global_idx}" class="lightbox-overlay" onclick="location.href='#';">
                                    <a href="#" class="close-hint">&times;</a>
                                    <img src="{img_src}" class="lightbox-img" alt="{prod['name']}" onclick="event.stopPropagation();" />
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown("<div style='text-align:center; padding:40px 0; color:#94a3b8; font-size:11px; font-weight:700;'>No Image</div>", unsafe_allow_html=True)

                        # Description Text Below Image
                        st.markdown(
                            f"<div style='font-size: 10px; font-weight: 600; color: #475569; padding: 4px 0px; max-height: 80px; overflow-y: auto; line-height: 1.3;'>"
                            f"<strong>Details:</strong> {desc_text if desc_text else 'No additional details.'}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                        
                        # Product Name
                        st.markdown(
                            f"<div style='font-weight: 700; font-size: 11px; color: #0f172a; height: 32px; overflow: hidden; margin-top: 4px; line-height: 1.2;'>"
                            f"{prod['name']}"
                            f"</div>", 
                            unsafe_allow_html=True,
                        )

                        # Pricing Section
                        st.markdown(
                            f"<div style='font-weight: 800; font-size: 13px; color: #dc2626; margin-bottom: 6px;'>"
                            f"Rs. {prod['price']} <span style='font-size: 10px; color: #94a3b8; text-decoration: line-through; font-weight: 600; margin-left: 2px;'>Rs. 160</span>"
                            f"</div>", 
                            unsafe_allow_html=True,
                        )

                        # Color Dropdown Options Parser
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
                                label_visibility="collapsed",
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
                                f"<div style='text-align: center; font-weight: 800; font-size: 12px; padding-top: 6px; color: #6b1d4f;'>{current_qty}</div>",
                                unsafe_allow_html=True,
                            )

                        with q_col3:
                            if st.button("➕", key=f"plus_{global_idx}", use_container_width=True):
                                st.session_state.cart[item_key] = current_qty + 1
                                st.rerun()

                        st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No items found in this category.")

else:
    # --- CART & CHECKOUT VIEW ---
    st.subheader("🛒 Shopping Cart & Secure Checkout")
    if st.session_state.cart:
        for item_desc, qty in list(st.session_state.cart.items()):
            col_item, col_rem = st.columns([3, 1])
            with col_item:
                st.markdown(f"• **{item_desc}** — Qty: **{qty}**")
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
