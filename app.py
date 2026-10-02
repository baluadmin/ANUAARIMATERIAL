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
            font-size: 13px !important;
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
            padding-bottom: 5rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            max-width: 100% !important;
        }

        /* --- FORCE DESKTOP BROWSER GRID LAYOUT ON MOBILE --- */
        @media screen and (max-width: 768px) {
            div[data-testid="stHorizontalBlock"] {
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 4px !important;
            }
            div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
                width: 32% !important;
                flex: 1 1 32% !important;
                min-width: 30% !important;
                margin-bottom: 6px !important;
            }
        }

        /* Product Card Styling */
        div[data-testid="stVerticalBlock"] div[data-testid="stContainer"] {
            background-color: #ffffff !important;
            border: 1px solid #f3e8f1 !important;
            border-radius: 12px !important;
            padding: 8px !important;
            box-shadow: 0 3px 10px rgba(107, 29, 79, 0.04) !important;
            margin-bottom: 6px;
        }

        /* Direct Clickable Zoom Image */
        .zoom-thumb {
            width: 100% !important;
            height: 95px !important;
            object-fit: cover !important;
            border-radius: 6px !important;
            cursor: pointer;
            display: block !important;
            margin: 0 !important;
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
            max-width: 90vw;
            max-height: 80vh;
            object-fit: contain;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }
        .close-hint {
            position: absolute;
            top: -45px;
            right: 0px;
            color: #ffffff;
            font-size: 28px;
            font-weight: bold;
            text-decoration: none;
            background: rgba(0,0,0,0.5);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        /* Compact Buttons Styling */
        div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #6b1d4f 0%, #53143c 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            font-size: 10px !important;
            border-radius: 4px !important;
            padding: 0rem 0.1rem !important;
            width: 100% !important;
            min-height: 22px !important;
            box-shadow: 0 1px 3px rgba(107, 29, 79, 0.15) !important;
        }

        /* --- BOTTOM FLOATING WHITE CART BAR STYLING --- */
        .floating-cart-wrapper {
            position: fixed;
            bottom: 12px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 99999999;
            width: 92%;
            max-width: 450px;
            background: #ffffff;
            padding: 8px 12px;
            border-radius: 30px;
            box-shadow: 0 8px 25px rgba(107, 29, 79, 0.2);
            border: 1px solid #f3e8f1;
        }

        .login-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding-top: 2rem;
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
if "shuffled_seed" not in st.session_state:
    st.session_state.shuffled_seed = random.randint(1, 10000)

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyftApEC3eQJvJPF0tCSX7eFwAG52IinpEhQtlxhmVaOtpbc1J83zJZIhs9XRDRCezCZA/exec"


def log_login_to_sheet(name, phone):
    try:
        payload = {"Type": "Login", "Customer_Name": name, "Primary_Phone": phone}
        requests.post(GOOGLE_SCRIPT_URL, json=payload, timeout=5)
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

    _, login_col, _ = st.columns([0.2, 3, 0.2])

    with login_col:
        with st.form("customer_login_form", clear_on_submit=False):
            cust_name = st.text_input("Customer Name:", placeholder="Enter your name")
            raw_phone = st.text_input("10-Digit Mobile Number:", max_chars=10, placeholder="9840XXXXXX")
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
@st.cache_data(ttl=5)
def load_inventory_from_sheet():
    sheet_csv_url = "https://docs.google.com/spreadsheets/d/1SK6S8tw4KWvwm_sQS6FHMGsSla7RkQ7XFkE7uuf9GRM/gviz/tq?tqx=out:csv&sheet=need+inventory+model+for+this+ANUAARI"
    try:
        df = pd.read_csv(sheet_csv_url)
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
        {"id": "AB0001", "name": "Glassy Beads", "category": "Beads", "subcategory": "Glassy Beads", "price": "90.00", "colors": "Red, Blue", "images": "", "description": "High quality sample item."}
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
        requests.post(GOOGLE_SCRIPT_URL, json=order_data, timeout=5)
    except Exception:
        pass
    st.session_state.cart = {}
    return f"Order placed successfully ({payment_method})!"


def render_product_grid(items, view_prefix="grid"):
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
                                    <a href="#modal_{view_prefix}_{u_key}_{img_i}_{i}_{col_idx}">
                                        <img src="{img_url}" class="zoom-thumb" alt="{prod['name']}" title="Click to Zoom" />
                                    </a>
                                    <div id="modal_{view_prefix}_{u_key}_{img_i}_{i}_{col_idx}" class="lightbox-overlay" onclick="location.href='#';">
                                        <div class="lightbox-content" onclick="event.stopPropagation();">
                                            <a href="#" class="close-hint">&times;</a>
                                            <a href="#modal_{view_prefix}_{u_key}_{prev_i}_{i}_{col_idx}" class="nav-btn prev-btn">‹</a>
                                            <img src="{img_url}" class="lightbox-img" alt="{prod['name']}" />
                                            <a href="#modal_{view_prefix}_{u_key}_{next_i}_{i}_{col_idx}" class="nav-btn next-btn">›</a>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True
                                )
                    else:
                        st.markdown("<div style='text-align:center; padding:20px 0; color:#94a3b8; font-size:10px; font-weight:700;'>No Image</div>", unsafe_allow_html=True)

                    st.markdown(
                        f"<div style='font-size: 11px; font-weight: 600; color: #475569; padding: 2px 0px; height: 32px; overflow-y: auto; line-height: 1.2;'>"
                        f"<strong>Details:</strong> {desc_text if desc_text else 'No details available.'}"
                        f"</div>", unsafe_allow_html=True
                    )
                    
                    st.markdown(
                        f"<div style='font-weight: 700; font-size: 12px; color: #0f172a; height: 28px; overflow: hidden; margin-top: 2px; line-height: 1.1;'>"
                        f"{prod['name']}"
                        f"</div>", unsafe_allow_html=True
                    )

                    raw_colors = prod.get('colors', '')
                    for sep in ['\\', ',', '&']: 
                        raw_colors = raw_colors.replace(sep, '|')
                    color_list = [c.strip() for c in raw_colors.split('|') if c.strip()]
                    selected_color = color_list[0] if color_list else "Standard"

                    if color_list:
                        selected_color = st.selectbox("Options", color_list, key=f"color_{view_prefix}_{u_key}_{i}_{col_idx}", label_visibility="collapsed")

                    item_key = f"{prod['name']} ({selected_color})"
                    current_qty = st.session_state.cart.get(item_key, 0)

                    # --- PRICE & QUANTITY CONTROLS WITH UNIQUE KEYS ---
                    price_html = f"<div style='font-weight: 800; font-size: 12px; color: #dc2626; padding-top: 4px;'>Rs. {prod['price']} <span style='font-size: 9px; color: #94a3b8; text-decoration: line-through; font-weight: 600;'>Rs. 160</span></div>"
                    
                    p_col, q_col = st.columns([1, 1.8], gap="small")
                    with p_col:
                        st.markdown(price_html, unsafe_allow_html=True)
                    with q_col:
                        q1, q2, q3 = st.columns([1, 1, 1], gap="small")
                        with q1:
                            if st.button("➖", key=f"minus_{view_prefix}_{u_key}_{selected_color}_{i}_{col_idx}", use_container_width=True):
                                if current_qty > 0:
                                    st.session_state.cart[item_key] = current_qty - 1
                                    if st.session_state.cart[item_key] == 0: 
                                        del st.session_state.cart[item_key]
                                    st.rerun()
                        with q2:
                            st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 11px; padding-top: 4px; color: #6b1d4f;'>{current_qty}</div>", unsafe_allow_html=True)
                        with q3:
                            if st.button("➕", key=f"plus_{view_prefix}_{u_key}_{selected_color}_{i}_{col_idx}", use_container_width=True):
                                st.session_state.cart[item_key] = current_qty + 1
                                st.rerun()


# --- STREAMLIT POPUP DIALOG FOR CART & CHECKOUT ---
@st.dialog("🛒 Shopping Cart & Secure Checkout")
def show_cart_modal():
    if st.session_state.cart:
        with st.container(border=True):
            for item_desc, qty in list(st.session_state.cart.items()):
                cart_col1, cart_col2 = st.columns([3.2, 1], gap="small")
                with cart_col1:
                    st.markdown(f"<div style='font-size: 12px; font-weight: 700; color: #2d1524; padding-top: 4px;'>• {item_desc} <br><span style='color: #6b1d4f; font-weight: 800;'>Qty: {qty}</span></div>", unsafe_allow_html=True)
                with cart_col2:
                    if st.button("Remove", key=f"rem_{item_desc}", use_container_width=True):
                        del st.session_state.cart[item_desc]
                        st.rerun()
                st.markdown("<div style='border-top: 1px solid #f3e8f1; margin: 4px 0;'></div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        with st.form("checkout_form"):
            st.markdown("<div style='font-size: 13px; font-weight: 800; color: #6b1d4f; margin-bottom: 6px;'>📍 Shipping & Payment Details</div>", unsafe_allow_html=True)
            address = st.text_area("Delivery Address (with Pincode):", placeholder="Enter full address...")
            sec_phone = st.text_input("Alternative Contact Number:", max_chars=10, placeholder="10-digit number")
            payment_option = st.radio("Select Payment Method:", ["Cash on Delivery (COD)", "Prepaid (UPI / Cards)"], horizontal=True)
            notes = st.text_area("Custom Instructions / Notes (Optional):", placeholder="Any specific instructions...")

            st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
            if st.form_submit_button("Complete Order Now", use_container_width=True):
                if address and len(sec_phone) == 10:
                    res_msg = process_cart_checkout(address, payment_option, sec_phone, notes)
                    st.success(res_msg)
                    st.rerun()
                else:
                    st.warning("Please provide a valid delivery address and an exact 10-digit alternative phone number.")
    else:
        st.info("Your cart is empty. Add products to view them here.")


# --- BOTTOM FLOATING WHITE CART BAR ---
total_cart_items = sum(st.session_state.cart.values()) if isinstance(st.session_state.cart, dict) else 0

st.markdown('<div class="floating-cart-wrapper">', unsafe_allow_html=True)
col_lbl, col_btn = st.columns([1.5, 1], gap="small")
with col_lbl:
    st.markdown(f"<div style='font-weight: 800; font-size: 12px; color: #6b1d4f; padding-top: 6px; padding-left: 6px;'>🛒 Cart ({total_cart_items} Items)</div>", unsafe_allow_html=True)
with col_btn:
    if st.button("View Cart", use_container_width=True, key="open_cart_popup"):
        show_cart_modal()
st.markdown('</div>', unsafe_allow_html=True)


# --- MAIN STORE TABS ---
tab1, tab2 = st.tabs(["🔥 Products", "🗂 Categories"])

with tab1:
    filtered_items = list(product_records)
    random.seed(st.session_state.shuffled_seed)
    random.shuffle(filtered_items)

    grid_head_col1, grid_head_col2 = st.columns([3, 1])
    with grid_head_col1:
        st.markdown("<h3 style='margin: 0; font-size: 14px; font-weight: 900; color: #0f172a;'>Featured Products</h3>", unsafe_allow_html=True)
    with grid_head_col2:
        st.markdown(f"<div style='text-align: right;'><span style='background: rgba(107,29,79,0.1); color: #6b1d4f; font-weight: 700; font-size: 10px; padding: 2px 6px; border-radius: 20px;'>{len(filtered_items)} items</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

    render_product_grid(filtered_items, view_prefix="home")

with tab2:
    categories = sorted(list(set([p["category"] for p in product_records if p["category"]])))
    
    st.markdown("<span style='color: #6b1d4f; font-weight: 800; font-size: 11px; text-transform: uppercase;'>🗂️ Master Categories</span>", unsafe_allow_html=True)
    
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

    st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #f0e1ec;'>", unsafe_allow_html=True)

    if st.session_state.selected_category:
        subcats = sorted(list(set([p["subcategory"] for p in product_records if p["category"] == st.session_state.selected_category and p["subcategory"]])))
        
        if subcats:
            st.markdown("<span style='color: #d97706; font-weight: 800; font-size: 10px; text-transform: uppercase;'>🏷️️ Subcategories</span>", unsafe_allow_html=True)
            for i in range(0, len(subcats), 3):
                subcat_cols = st.columns(3, gap="small")
                for idx, subcat in enumerate(subcats[i : i + 3]):
                    with subcat_cols[idx]:
                        is_sel_sub = (st.session_state.selected_subcategory == subcat)
                        sub_label = f"✨ {subcat}" if is_sel_sub else subcat
                        if st.button(sub_label, key=f"sub_btn_{i}_{idx}", use_container_width=True):
                            st.session_state.selected_subcategory = subcat
                            st.rerun()
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        if st.session_state.selected_subcategory:
            filtered_items = [p for p in product_records if p["category"] == st.session_state.selected_category and p["subcategory"] == st.session_state.selected_subcategory]
            header_title = st.session_state.selected_subcategory
        else:
            filtered_items = [p for p in product_records if p["category"] == st.session_state.selected_category]
            header_title = f"All {st.session_state.selected_category}"

        grid_head_col1, grid_head_col2 = st.columns([3, 1])
        with grid_head_col1:
            st.markdown(f"<h3 style='margin: 0; font-size: 14px; font-weight: 900; color: #0f172a;'>{header_title}</h3>", unsafe_allow_html=True)
        with grid_head_col2:
            st.markdown(f"<div style='text-align: right;'><span style='background: rgba(107,29,79,0.1); color: #6b1d4f; font-weight: 700; font-size: 10px; padding: 2px 6px; border-radius: 20px;'>{len(filtered_items)} items</span></div>", unsafe_allow_html=True)
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

        render_product_grid(filtered_items, view_prefix="category")
