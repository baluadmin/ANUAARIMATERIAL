from datetime import datetime
import base64
import os
import random
import pandas as pd
import requests
import streamlit as st

# 1. Page Configuration & Custom CSS Layout Styling
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
            overflow: hidden !important;
        }

        #MainMenu, header, footer {visibility: hidden; display: none !important;}
        div[data-testid="stToolbar"], section[data-testid="stStatusWidget"] {display: none !important;}
        .stAppDeployButton {display: none !important; visibility: hidden !important;}
        header[data-testid="stHeader"] {display: none !important; visibility: hidden !important;}
        div[data-testid="stDecoration"] {display: none !important;}

        /* App Main Block Container Config with internal scrolling */
        .block-container {
            padding: 1rem !important;
            max-width: 100% !important;
            height: calc(100vh - 75px) !important;
            overflow-y: auto !important;
            margin-bottom: 75px !important;
        }

        /* Absolutely Fixed Bottom Navigation Bar */
        .fixed-bottom-nav {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            width: 100% !important;
            background: #ffffff !important;
            border-top: 1px solid #f3e8f1 !important;
            padding: 8px 16px !important;
            z-index: 9999999 !important;
            box-shadow: 0 -4px 20px rgba(107, 29, 79, 0.1) !important;
        }

        /* Product Card Styling for 3 Columns */
        div[data-testid="stVerticalBlock"] div[data-testid="stContainer"] {
            background-color: #ffffff !important;
            border: 1px solid #f3e8f1 !important;
            border-radius: 14px !important;
            padding: 10px !important;
            box-shadow: 0 4px 12px rgba(107, 29, 79, 0.04) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 8px;
        }
        
        div[data-testid="stVerticalBlock"] div[data-testid="stContainer"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(107, 29, 79, 0.08) !important;
            border-color: #e8d0e4 !important;
        }

        /* Direct Clickable Zoom Image */
        .zoom-thumb {
            width: 100% !important;
            height: 105px !important;
            object-fit: cover !important;
            border-radius: 6px !important;
            cursor: pointer;
            transition: transform 0.2s ease, opacity 0.2s ease;
            display: block !important;
            margin: 0 !important;
        }
        .zoom-thumb:hover {
            opacity: 0.85;
            transform: scale(1.02);
        }

        /* Lightbox Overlay */
        .lightbox-overlay {
            display: none;
            position: fixed;
            z-index: 99999999;
            left: 0;
            top: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(20, 5, 15, 0.9);
            backdrop-filter: blur(4px);
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .lightbox-overlay:target {
            display: flex;
        }
        .lightbox-content {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: default;
        }
        .lightbox-img {
            max-width: 85vw;
            max-height: 80vh;
            object-fit: contain;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            animation: zoomIn 0.25s ease-out;
        }
        .close-hint {
            position: absolute;
            top: -50px;
            right: 0px;
            color: #ffffff;
            font-size: 28px;
            font-weight: bold;
            text-decoration: none;
            background: rgba(0,0,0,0.5);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .nav-btn {
            position: absolute;
            top: 50%;
            transform: translateY(-50%);
            color: #ffffff;
            font-size: 32px;
            font-weight: bold;
            text-decoration: none;
            background: rgba(107, 29, 79, 0.7);
            border-radius: 50%;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
            transition: background 0.2s;
        }
        .nav-btn:hover {
            background: rgba(107, 29, 79, 1);
        }
        .prev-btn {
            left: -70px;
        }
        .next-btn {
            right: -70px;
        }

        @keyframes zoomIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        /* Compact Buttons Styling */
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #6b1d4f 0%, #53143c 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            font-size: 12px !important;
            border-radius: 6px !important;
            padding: 0.2rem 0.4rem !important;
            width: 100% !important;
            min-height: 30px !important;
            box-shadow: 0 2px 5px rgba(107, 29, 79, 0.15) !important;
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
    st.session_state.current_view = "Categories"
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "selected_subcategory" not in st.session_state:
    st.session_state.selected_subcategory = None
if "shuffled_seed" not in st.session_state:
    st.session_state.shuffled_seed = random.randint(1, 10000)

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyftApEC3eQJvJPF0tCSX7eFwAG52IinpEhQtlxhmVaOtpbc1J83zJZIhs9XRDRCezCZA/exec"


def log_login_to_sheet(name, phone):
    try:
        payload = {"Type": "Login", "Customer_Name": name, "Primary_Phone": phone}
        requests.post(GOOGLE_SCRIPT_URL, json=payload)
    except Exception as e:
        print(f"Login sheet error: {e}")


def get_image_src(image_path):
    if not image_path:
        return ""
    image_path = image_path.strip()
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path
    
    loc_path = f"images/{image_path}"
    target_path = image_path if os.path.exists(image_path) else (loc_path if os.path.exists(loc_path) else "")
    
    if target_path:
        try:
            with open(target_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode("utf-8")
                ext = target_path.split(".")[-1].lower()
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
        with st.form("customer_login_form", clear_on_submit=False):
            cust_name = st.text_input("Customer Name:", placeholder="")
            raw_phone = st.text_input("10-Digit Mobile Number:", max_chars=10, placeholder="")
            cust_phone = "".join([char for char in raw_phone if char.isdigit()])

            login_btn = st.form_submit_button("Enter Store", use_container_width=True)

            if login_btn:
                if cust_name.strip() and len(cust_phone) == 10:
                    st.session_state.logged_in_user = cust_name.strip()
                    st.session_state.user_phone = cust_phone.strip()
                    st.session_state.shuffled_seed = random.randint(1, 10000)
                    log_login_to_sheet(cust_name.strip(), cust_phone.strip())
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.warning("Please provide your name and an exact 10-digit mobile number.")
    st.stop()


# Load Inventory Directly from Google Sheets
@st.cache_data(ttl=2)
def load_inventory_from_sheet():
    sheet_csv_url = "https://docs.google.com/spreadsheets/d/1SK6S8tw4KWvwm_sQS6FHMGsSla7RkQ7XFkE7uuf9GRM/gviz/tq?tqx=out:csv&sheet=need+inventory+model+for+this+ANUAARI"
    try:
        df = pd.read_csv(sheet_csv_url)
        df.to_csv("inventory.csv", index=False)
        return df
    except Exception:
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
            
            subcat_val = str(row.iloc[2]).strip() if len(row) > 2 and pd.notna(row.iloc[2]) else ""
            if subcat_val.lower() == "nan":
                subcat_val = ""

            img_val = str(row.iloc[5]).strip() if len(row) > 5 and pd.notna(row.iloc[5]) else ""
            desc_val = str(row.iloc[6]).strip() if len(row) > 6 and pd.notna(row.iloc[6]) else ""
            if desc_val.lower() == "nan":
                desc_val = ""

            product_records.append({
                "id": str(row.iloc[0]).strip(),
                "name": subcat_val if subcat_val else "Craft Item",
                "category": cat_val,
                "subcategory": subcat_val,
                "price": str(row.iloc[3]).strip() if len(row) > 3 else "0.0",
                "colors": str(row.iloc[4]).strip() if len(row) > 4 and pd.notna(row.iloc[4]) else "",
                "images": img_val,
                "description": desc_val,
            })
    except Exception:
        product_records = []

if not product_records:
    product_records = [
        {"id": "AB0001", "name": "Glassy Beads", "category": "Beads", "subcategory": "Glassy Beads", "price": "90.00", "colors": "Red, Blue", "images": "bunch beads 1.JPG \\ bunch beads 2.JPG \\ bunch beads 3.JPG", "description": "High quality beads."}
    ]


def process_cart_checkout(address: str, payment_method: str, secondary_phone: str, notes: str) -> str:
    if not st.session_state.cart:
        return "Your cart is empty."
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cart_summary = ", ".join([f"{qty} Units of {item}" for item, qty in st.session_state.cart.items()])
    try:
        order_data = {
            "Type": "Order",
            "Timestamp": timestamp,
            "Customer_Name": st.session_state.logged_in_user,
            "Primary_Phone": st.session_state.user_phone,
            "Items": cart_summary,
            "Address": address,
            "Payment_Method": payment_method,
            "Secondary_Phone": secondary_phone,
            "Description": notes,
        }
        requests.post(GOOGLE_SCRIPT_URL, json=order_data)
    except Exception:
        pass
    st.session_state.cart = {}
    return f"Order placed successfully ({payment_method})!"


def render_product_grid(items):
    if not items:
        st.info("No items found.")
        return

    for i in range(0, len(items), 3):
        cols = st.columns(3, gap="small")
        batch = items[i : i + 3]
        
        for col_idx, prod in enumerate(batch):
            with cols[col_idx]:
                with st.container(border=True):
                    u_key = prod['id']
                    raw_imgs = prod.get('images', '')
                    
                    for sep in ['\\', ',']:
                        raw_imgs = raw_imgs.replace(sep, '|')
                    img_list = [get_image_src(img.strip()) for img in raw_imgs.split('|') if img.strip() and img.strip().lower() != 'nan']

                    desc_text = prod.get('description', '')
                    total_imgs = len(img_list)

                    if total_imgs > 0:
                        img_cols = st.columns(total_imgs, gap="small")
                        for img_i, img_url in enumerate(img_list):
                            prev_i = (img_i - 1) % total_imgs
                            next_i = (img_i + 1) % total_imgs
                            
                            with img_cols[img_i]:
                                st.markdown(
                                    f"""
                                    <a href="#modal_{u_key}_{img_i}">
                                        <img src="{img_url}" class="zoom-thumb" alt="{prod['name']}" title="Click to Zoom" />
                                    </a>
                                    <div id="modal_{u_key}_{img_i}" class="lightbox-overlay" onclick="location.href='#';">
                                        <div class="lightbox-content" onclick="event.stopPropagation();">
                                            <a href="#" class="close-hint">&times;</a>
                                            <a href="#modal_{u_key}_{prev_i}" class="nav-btn prev-btn">‹</a>
                                            <img src="{img_url}" class="lightbox-img" alt="{prod['name']}" />
                                            <a href="#modal_{u_key}_{next_i}" class="nav-btn next-btn">›</a>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True
                                )
                    else:
                        st.markdown("<div style='text-align:center; padding:35px 0; color:#94a3b8; font-size:11px; font-weight:700;'>No Image</div>", unsafe_allow_html=True)

                    st.markdown(
                        f"<div style='font-size: 12px; font-weight: 600; color: #475569; padding: 4px 0px; height: 38px; overflow-y: auto; line-height: 1.3;'>"
                        f"<strong>Details:</strong> {desc_text if desc_text else 'No details available.'}"
                        f"</div>", unsafe_allow_html=True
                    )
                    
                    st.markdown(
                        f"<div style='font-weight: 700; font-size: 13px; color: #0f172a; height: 32px; overflow: hidden; margin-top: 4px; line-height: 1.2;'>"
                        f"{prod['name']}"
                        f"</div>", unsafe_allow_html=True
                    )

                    st.markdown(
                        f"<div style='font-weight: 800; font-size: 13px; color: #dc2626; margin-bottom: 4px;'>"
                        f"Rs. {prod['price']} <span style='font-size: 10px; color: #94a3b8; text-decoration: line-through; font-weight: 600; margin-left: 2px;'>Rs. 160</span>"
                        f"</div>", unsafe_allow_html=True
                    )

                    raw_colors = prod.get('colors', '')
                    for sep in ['\\', ',', '&']: raw_colors = raw_colors.replace(sep, '|')
                    color_list = [c.strip() for c in raw_colors.split('|') if c.strip()]
                    selected_color = color_list[0] if color_list else "Standard"

                    if color_list:
                        selected_color = st.selectbox("Options", color_list, key=f"color_{u_key}", label_visibility="collapsed")

                    item_key = f"{prod['name']} ({selected_color})"
                    current_qty = st.session_state.cart.get(item_key, 0)

                    q_col1, q_col2, q_col3 = st.columns([1, 1.2, 1], gap="small")
                    with q_col1:
                        if st.button("➖", key=f"minus_{u_key}", use_container_width=True):
                            if current_qty > 0:
                                st.session_state.cart[item_key] = current_qty - 1
                                if st.session_state.cart[item_key] == 0: del st.session_state.cart[item_key]
                                st.rerun()
                    with q_col2:
                        st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 13px; padding-top: 4px; color: #6b1d4f;'>{current_qty}</div>", unsafe_allow_html=True)
                    with q_col3:
                        if st.button("➕", key=f"plus_{u_key}", use_container_width=True):
                            st.session_state.cart[item_key] = current_qty + 1
                            st.rerun()

                    st.markdown("<div style='height: 2px;'></div>", unsafe_allow_html=True)


# --- SCROLLABLE CENTER CONTENT AREA ---
if st.session_state.current_view == "Home":
    filtered_items = list(product_records)
    random.seed(st.session_state.shuffled_seed)
    random.shuffle(filtered_items)

    grid_head_col1, grid_head_col2 = st.columns([3, 1])
    with grid_head_col1:
        st.markdown(f"<h3 style='margin: 0; font-size: 16px; font-weight: 900; color: #0f172a;'>🔥 Featured Products</h3>", unsafe_allow_html=True)
    with grid_head_col2:
        st.markdown(f"<div style='text-align: right;'><span style='background: rgba(107,29,79,0.1); color: #6b1d4f; font-weight: 700; font-size: 11px; padding: 3px 10px; border-radius: 20px;'>{len(filtered_items)} items</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

    render_product_grid(filtered_items)


elif st.session_state.current_view == "Categories":
    categories = sorted(list(set([p["category"] for p in product_records if p["category"]])))
    
    st.markdown("<span style='color: #6b1d4f; font-weight: 800; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;'>🗂️ Master Categories</span>", unsafe_allow_html=True)
    
    for i in range(0, len(categories), 3):
        cat_cols = st.columns(3, gap="small")
        for idx, cat in enumerate(categories[i : i + 3]):
            with cat_cols[idx]:
                is_selected = (st.session_state.selected_category == cat)
                btn_label = f"📂 {cat}" if is_selected else cat
                if st.button(btn_label, key=f"cat_btn_{i}_{idx}", use_container_width=True):
                    st.session_state.selected_category = cat
                    st.session_state.selected_subcategory = None
                    st.rerun()

    st.markdown("<hr style='margin: 12px 0; border: none; border-top: 1px solid #f0e1ec;'>", unsafe_allow_html=True)

    if st.session_state.selected_category:
        subcats = sorted(list(set([p["subcategory"] for p in product_records if p["category"] == st.session_state.selected_category and p["subcategory"]])))
        
        if subcats:
            st.markdown("<span style='color: #d97706; font-weight: 800; font-size: 11px; text-transform: uppercase;'>🏷️️ Subcategories</span>", unsafe_allow_html=True)
            for i in range(0, len(subcats), 3):
                subcat_cols = st.columns(3, gap="small")
                for idx, subcat in enumerate(subcats[i : i + 3]):
                    with subcat_cols[idx]:
                        is_sel_sub = (st.session_state.selected_subcategory == subcat)
                        sub_label = f"✨ {subcat}" if is_sel_sub else subcat
                        if st.button(sub_label, key=f"sub_btn_{i}_{idx}", use_container_width=True):
                            st.session_state.selected_subcategory = subcat
                            st.rerun()
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        if st.session_state.selected_subcategory:
            filtered_items = [p for p in product_records if p["category"] == st.session_state.selected_category and p["subcategory"] == st.session_state.selected_subcategory]
            header_title = st.session_state.selected_subcategory
        else:
            filtered_items = [p for p in product_records if p["category"] == st.session_state.selected_category]
            header_title = f"All {st.session_state.selected_category}"

        grid_head_col1, grid_head_col2 = st.columns([3, 1])
        with grid_head_col1:
            st.markdown(f"<h3 style='margin: 0; font-size: 16px; font-weight: 900; color: #0f172a;'>{header_title}</h3>", unsafe_allow_html=True)
        with grid_head_col2:
            st.markdown(f"<div style='text-align: right;'><span style='background: rgba(107,29,79,0.1); color: #6b1d4f; font-weight: 700; font-size: 11px; padding: 3px 10px; border-radius: 20px;'>{len(filtered_items)} items</span></div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

        render_product_grid(filtered_items)


elif st.session_state.current_view == "Cart":
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
                    st.session_state.current_view = "Categories"
                    st.rerun()
                else:
                    st.warning("Please provide a valid address and a 10-digit alternative phone number.")
    else:
        st.info("Your cart is empty. Click Categories to browse products.")


# --- LOCKED FIXED BOTTOM NAVIGATION BAR ---
st.markdown('<div class="fixed-bottom-nav">', unsafe_allow_html=True)
cols_footer = st.columns(4, gap="small")
with cols_footer[0]:
    if st.button("🗂️ Categories", key="b_cat_btn", use_container_width=True):
        st.session_state.current_view = "Categories"
        st.session_state.selected_category = None
        st.session_state.selected_subcategory = None
        st.rerun()
with cols_footer[1]:
    if st.button("🏠 Home", key="b_home_btn", use_container_width=True):
        st.session_state.current_view = "Home"
        st.session_state.shuffled_seed = random.randint(1, 10000)
        st.rerun()
with cols_footer[2]:
    total_cart_items = sum(st.session_state.cart.values()) if isinstance(st.session_state.cart, dict) else 0
    if st.button(f"🛒 Cart ({total_cart_items})", key="b_cart_btn", use_container_width=True):
        st.session_state.current_view = "Cart"
        st.rerun()
with cols_footer[3]:
    if st.button("🚪 Logout", key="b_logout_btn", use_container_width=True):
        st.session_state.clear()
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
