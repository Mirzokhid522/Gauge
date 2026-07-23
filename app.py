import os
from flask import Flask, jsonify, render_template
from notion_client import Client

app = Flask(__name__)

# Load credentials securely from environment variables
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

notion = Client(auth=NOTION_TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/score', methods=['GET'])
def get_macro_score():
    try:
        # Query your live Notion database
        response = notion.databases.query(
            database_id=DATABASE_ID
        )
        
        results = response.get("results", [])
        total_score = 0.0
        count = 0
        
        for page in results:
            props = page.get("properties", {})
            
            # Target the exact column header "Score" from your database
            score_prop = props.get("Score", {})
            prop_type = score_prop.get("type")
            val = None
            
            # Handle Number properties
            if prop_type == "number":
                val = score_prop.get("number")
                
            # Handle Formula outputs (if your column is a formula)
            elif prop_type == "formula":
                formula_data = score_prop.get("formula", {})
                if formula_data.get("type") == "number":
                    val = formula_data.get("number")

            if val is not None:
                total_score += float(val)
                count += 1

        # Use the live aggregated score, or fall back if empty
        score = total_score if count > 0 else -0.0835
        
        # Apply your exact scoring tiers and status logic
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

        return jsonify({"score": float(score), "status": status})

    except Exception as e:
        print(f"Error fetching live data from Notion: {e}")
        return jsonify({"error": str(e), "score": -0.0835, "status": "Bearish USD"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)