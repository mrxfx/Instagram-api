from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

# Basic spoofed headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.instagram.com/"
}

# Allow public API calls like: /davit_moder
@app.route('/<username>', methods=['GET'])
def profile(username):
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    response = requests.get(url, headers=HEADERS, allow_redirects=True)

    if not response.ok or 'application/json' not in response.headers.get("Content-Type", ""):
        return jsonify({"error": "Failed to fetch data", "status_code": response.status_code}), response.status_code

    try:
        user = response.json().get("graphql", {}).get("user", {})
        if not user:
            return jsonify({"error": "User not found"}), 404

        posts = []
        for edge in user.get("edge_owner_to_timeline_media", {}).get("edges", []):
            node = edge["node"]
            posts.append({
                "post_id": node.get("id"),
                "caption": node["edge_media_to_caption"]["edges"][0]["node"]["text"]
                if node["edge_media_to_caption"]["edges"] else "No Caption",
                "likes": node["edge_liked_by"]["count"],
                "comments": node["edge_media_to_comment"]["count"],
                "post_url": f"https://www.instagram.com/p/{node['shortcode']}/",
                "thumbnail": node["display_url"],
                "type": "Video" if node.get("is_video") else "Image",
                "posted_at": node.get("taken_at_timestamp"),
                "view_count": node.get("video_view_count") if node.get("is_video") else None,
                "alt_text": node.get("accessibility_caption")
            })

        # Final response
        return jsonify({
            "status": "success",
            "profile_info": {
                "username": user.get("username"),
                "full_name": user.get("full_name"),
                "bio": user.get("biography"),
                "followers": user["edge_followed_by"]["count"],
                "following": user["edge_follow"]["count"],
                "total_posts": user["edge_owner_to_timeline_media"]["count"],
                "profile_picture": user.get("profile_pic_url_hd"),
                "private_account": user.get("is_private"),
                "verified": user.get("is_verified"),
                "category": user.get("category_name"),
                "website": user.get("external_url")
            },
            "recent_posts": posts
        })

    except Exception as e:
        return jsonify({"error": "Failed to parse response", "message": str(e)}), 500

# Required for Render or other cloud hosts
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
