import os
import json
import requests
from bs4 import BeautifulSoup
from google import genai
import gspread

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_CREDS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")

SPREADSHEET_NAME = "ANUAARIMATERIAL"
WORKSHEET_NAME = "need inventory model for this ANUAARI" #[cite: 3]
TARGET_URL = "https://aarimaterials.com/collections/crystal-beads"

def scrape_and_extract():
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(TARGET_URL, headers=headers, timeout=10)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    for script in soup(["script", "style", "nav", "footer"]):
        script.extract()
    page_text = soup.get_text(separator=' ', strip=True)[:6000]

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = (
        "Extract product details from the following website text. "
        "Return a clean comma-separated list with these exact columns: "
        "Item_ID, Category, Subcategory, Price (INR), Color Options, Stock Status.[cite: 3] "
        "Generate a unique Item ID starting with AB (e.g. AB0001). "
        "Only output raw rows without markdown formatting."
        f"\n\nWebsite Text:\n{page_text}"
    )

    response = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
    return response.text

def update_google_sheet(data_text):
    creds_dict = json.loads(GOOGLE_CREDS_JSON)
    creds_path = "temp_creds.json"
    with open(creds_path, "w") as f:
        json.dump(creds_dict, f)

    gc = gspread.service_account(filename=creds_path)
    sheet = gc.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)
    
    lines = data_text.strip().split("\n")
    for line in lines:
        if "," in line and "Item_ID" not in line:
            row_data = [item.strip() for item in line.split(",")]
            if len(row_data) >= 6:
                sheet.append_row(row_data[:6])
                
    if os.path.exists(creds_path):
        os.remove(creds_path)

if __name__ == "__main__":
    data = scrape_and_extract()
    if data:
        update_google_sheet(data)
