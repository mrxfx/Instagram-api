from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.instagram.com/"
}

def fetch_profile(username):
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    return requests.get(url, headers=HEADERS)

@app.route('/<username>', methods=['GET'])
def profile(username):
    response = fetch_profile(username)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data", "status_code": response.status_code})

    try:
        user = response.json().get("graphql", {}).get("user", {})
        if not user:
            return jsonify({"error": "User not found"})

        posts = []
        for edge in user.get("edge_owner_to_timeline_media", {}).get("edges", []):
            node = edge["node"]
            posts.append({
                "Post ID": node.get("id"),
                "Caption": node["edge_media_to_caption"]["edges"][0]["node"]["text"]
                if node["edge_media_to_caption"]["edges"] else "No Caption",
                "Likes": node["edge_liked_by"]["count"],
                "Comments": node["edge_media_to_comment"]["count"],
                "Post URL": f"https://www.instagram.com/p/{node['shortcode']}/",
                "Thumbnail": node["display_url"],
                "Type": "Video" if node.get("is_video") else "Image",
                "Posted At": node.get("taken_at_timestamp"),
                "View Count": node.get("video_view_count") if node.get("is_video") else None,
                "Alt Text": node.get("accessibility_caption")
            })

        return jsonify({
            "Profile Info": {
                "Username": user.get("username"),
                "Full Name": user.get("full_name"),
                "Bio": user.get("biography"),
                "Followers": user["edge_followed_by"]["count"],
                "Following": user["edge_follow"]["count"],
                "Total Posts": user["edge_owner_to_timeline_media"]["count"],
                "Profile Picture": user.get("profile_pic_url_hd"),
                "Private Account": user.get("is_private"),
                "Verified": user.get("is_verified"),
                "Category": user.get("category_name"),
                "Website": user.get("external_url"),
            },
            "Recent Posts": posts
        })

    except Exception as e:
        return jsonify({"error": "Failed to parse response", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
