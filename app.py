import os
import requests
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/score', methods=['GET'])
def get_macro_score():
    try:
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, headers=HEADERS, timeout=5)
        
        if response.status_code != 200:
            print(f"Notion API Error: {response.status_code} - {response.text}")
            return jsonify({"error": f"Notion API error {response.status_code}", "score": 0.0, "status": "Error"}), 500

        data = response.json()
        results = data.get("results", [])
        
        total_score = 0.0
        count = 0

        for page in results:
            props = page.get("properties", {})
            score_prop = props.get("Score", {})
            p_type = score_prop.get("type")
            
            val = None
            # Extract score based on property type
            if p_type == "rollup":
                val = score_prop.get("rollup", {}).get("number")
            elif p_type == "number":
                val = score_prop.get("number")
            elif p_type == "formula":
                val = score_prop.get("formula", {}).get("number")

            if val is not None:
                total_score += float(val)
                count += 1

        score = round(total_score, 4) if count > 0 else 0.0

        # Determine directional bias
        if score > 0.3:
            status = "Very Bullish USD"
        elif score > 0.05:
            status = "Bullish USD"
        elif score < -0.3:
            status = "Very Bearish USD"
        elif score < -0.05:
            status = "Bearish USD"
        else:
            status = "Neutral USD"

        return jsonify({
            "score": score,
            "status": status
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e), "score": 0.0, "status": "Error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)