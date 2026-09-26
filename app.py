import streamlit as st
import pandas as pd
from google import genai
import gspread
import json
import os
from datetime import datetime

st.set_page_config(page_title="ANUAARIMATERIAL Store", page_icon="🧵", layout="wide")

# Sidebar settings
st.sidebar.header("⚙️ Configuration")
gemini_api_key = st.sidebar.text_input("Gemini API Key:", type="password")

# Paste your published CSV links or use public sheet URLs
inventory_csv = st.sidebar.text_input("Inventory CSV URL", value="PASTE_INVENTORY_CSV_LINK")
login_csv = st.sidebar.text_input("LOGIN CSV URL", value="PASTE_LOGIN_CSV_LINK")

st.title("🧵 ANUAARIMATERIAL E-Commerce Platform")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_name = ""

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.subheader("🔐 Customer Portal Login")
    phone_input = st.text_input("Enter Registered Mobile Number:")
    
    if st.button("Login"):
        try:
            df_login = pd.read_csv(login_csv)
            df_login.columns = df_login.columns.str.strip()
            match = df_login[df_login['MOBILE NUMBER'].astype(str).str.contains(phone_input)]
            if not match.empty and phone_input:
                st.session_state.logged_in = True
                st.session_state.user_name = match.iloc[0].get('NAME', 'Customer')
                st.success(f"Welcome, {st.session_state.user_name}!")
                st.rerun()
            else:
                st.error("Mobile number not found in LOGIN records.")
        except Exception as e:
            st.error(f"Login validation error: {e}")
else:
    st.sidebar.success(f"Logged in as: {st.session_state.user_name}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- STORE CATALOG & FILTERS ---
    try:
        df_inv = pd.read_csv(inventory_csv)
        df_inv.columns = df_inv.columns.str.strip()

        if "Category" in df_inv.columns:
            cats = ["All Categories"] + list(df_inv["Category"].dropna().unique())
            sel_cat = st.sidebar.selectbox("Filter Category", cats)
            if sel_cat != "All Categories":
                df_inv = df_inv[df_inv["Category"] == sel_cat]

        st.markdown("---")
        st.header("🛍️ Product Inventory & Order Placement")

        for i in range(0, len(df_inv), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(df_inv):
                    item = df_inv.iloc[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.subheader(item.get("Item_ID", "Item"))
                            st.write(f"**Category:** {item.get('Category', '')}")
                            st.write(f"**Subcategory:** {item.get('Subcategory', '')}")
                            st.write(f"**Price:** ₹{item.get('Price (INR)', 0)}")
                            st.write(f"**Colors:** {item.get('Color Options', '')}")
                            st.success(item.get("Stock Status", "In Stock"))
                            
                            item_id = item.get("Item_ID", "")
                            if st.button(f"Buy Now ({item_id})", key=f"buy_{i+j}"):
                                st.session_state.checkout_item = item_id

        # --- CHECKOUT FORM TO SHEET ---
        if "checkout_item" in st.session_state:
            st.markdown("---")
            st.subheader(f"📦 Checkout for Item ID: {st.session_state.checkout_item}")
            with st.form("checkout_form"):
                c_name = st.text_input("Customer Name", value=st.session_state.user_name)
                p_phone = st.text_input("Primary Phone Number")
                s_phone = st.text_input("Secondary Phone Number (Optional)")
                address = st.text_area("Delivery Address")
                notes = st.text_area("Order Description / Instructions")
                
                submitted = st.form_submit_button("Submit Order")
                if submitted:
                    st.success("Order form ready! Connect your Google Service Account credentials to auto-sync this directly to your 'ANUAAARI Orders' tab[cite: 2].")

    except Exception as e:
        st.warning("⚠️ Please provide valid published CSV links in the sidebar to load your store database.")
