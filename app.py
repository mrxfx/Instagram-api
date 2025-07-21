from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SCRAPER_API_KEY = "9a0ad483f61d4dad4baded9ef1d20f17"
VALID_TOKEN = "rahul2025"

@app.route("/profile", methods=["GET"])
def profile():
    token = request.args.get("token")
    if token != VALID_TOKEN:
        return jsonify({"error": "Unauthorized access", "status_code": 403})

    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Missing username", "status_code": 400})

    try:
        target_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
        payload = {
            'api_key': SCRAPER_API_KEY,
            'url': target_url
        }
        r = requests.get('https://api.scraperapi.com/', params=payload)
        data = r.json()

        user = data.get("graphql", {}).get("user", {})
        if not user:
            return jsonify({"error": "User not found", "status_code": 404})

        return jsonify({
            "username": user.get("username"),
            "full_name": user.get("full_name"),
            "bio": user.get("biography"),
            "followers": user.get("edge_followed_by", {}).get("count"),
            "following": user.get("edge_follow", {}).get("count"),
            "posts": user.get("edge_owner_to_timeline_media", {}).get("count"),
            "is_verified": user.get("is_verified"),
            "error": None,
            "status_code": 200
        })

    except Exception as e:
        return jsonify({"error": "Failed to fetch data", "status_code": 500})
