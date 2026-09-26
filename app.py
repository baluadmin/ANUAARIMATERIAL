import streamlit as st
import pandas as pd
from google import genai
import gspread
import json
import os
from datetime import datetime

st.set_page_config(page_title="ANUAARIMATERIAL Store", page_icon="🧵", layout="wide")

# --- HARDCODED CONFIGURATION ---
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"

# Direct CSV Export Links generated from your Google Sheet ID
INVENTORY_CSV_URL = "https://docs.google.com/spreadsheets/d/1SK6S8tw4KWvwm_sQS6FHMGsSla7RkQ7XFkE7uuf9GRM/gviz/tq?tqx=out:csv&sheet=need+inventory+model+for+this+ANUAARI"
LOGIN_CSV_URL = "https://docs.google.com/spreadsheets/d/1SK6S8tw4KWvwm_sQS6FHMGsSla7RkQ7XFkE7uuf9GRM/gviz/tq?tqx=out:csv&sheet=LOGIN"

# Google Service Account Credentials for writing orders directly to sheet
GOOGLE_CREDS_JSON = {
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}

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
            df_login = pd.read_csv(LOGIN_CSV_URL)
            df_login.columns = df_login.columns.str.strip()
            
            # Match phone number against MOBILE NUMBER column
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
        df_inv = pd.read_csv(INVENTORY_CSV_URL)
        df_inv.columns = df_inv.columns.str.strip()

        if "Category" in df_inv.columns:
            cats = ["All Categories"] + list(df_inv["Category"].dropna().unique())
            sel_cat = st.sidebar.selectbox("Filter Category", cats)
            if sel_cat != "All Categories":
                df_inv = df_inv[df_inv["Category"] == sel_cat]

        st.markdown("---")
        st.header("🛍️ Product Inventory & Order Placement")

        if df_inv.empty:
            st.warning("No items found in your inventory sheet. Add products to your 'need inventory model for this ANUAARI' tab.")
        else:
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
                    try:
                        creds_path = "temp_order_creds.json"
                        with open(creds_path, "w") as f:
                            json.dump(GOOGLE_CREDS_JSON, f)

                        gc = gspread.service_account(filename=creds_path)
                        sheet = gc.open("ANUAARIMATERIAL").worksheet("ANUAAARI Orders")
                        
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        row_data = [
                            timestamp,
                            c_name,
                            p_phone,
                            st.session_state.checkout_item,
                            address,
                            s_phone,
                            notes
                        ]
                        
                        sheet.append_row(row_data)
                        
                        if os.path.exists(creds_path):
                            os.remove(creds_path)
                            
                        st.success("🎉 Order successfully placed and saved directly to your ANUAAARI Orders sheet!")
                    except Exception as e:
                        st.error(f"Failed to save order to Google Sheet: {e}")

    except Exception as e:
        st.warning(f"⚠️ Could not load inventory. Make sure your Google Sheet is shared with 'Anyone with the link can view'. Error: {e}")
