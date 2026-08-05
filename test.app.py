import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_and_print_properties():
    if not NOTION_TOKEN or not DATABASE_ID:
        print("Error: NOTION_TOKEN or DATABASE_ID is missing from your .env file.")
        return

    print("Connecting to Notion API...")
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    try:
        response = requests.post(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            print(f"Notion API Error: {response.status_code} - {response.text}")
            return

        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print("Database query returned 0 rows/pages. Make sure your database has content.")
            return

        # Grab properties from the first page/row
        first_page_properties = results[0].get("properties", {})
        
        print("\n========================================")
        print("     NOTION DATABASE PROPERTIES         ")
        print("========================================")
        for prop_name, prop_details in first_page_properties.items():
            p_type = prop_details.get("type")
            print(f"Property Name: '{prop_name}'  -->  Type: {p_type}")
        print("========================================\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    fetch_and_print_properties()