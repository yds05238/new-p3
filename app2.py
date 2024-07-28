from flask import Flask, jsonify, request, Blueprint

app = Flask(__name__)

# Global variable to store posts and comments
posts = {
    0: {
        "id": 0,
        "upvotes": 1,
        "title": "My dog with 2 balls in his mouth",
        "link": "https://imgur.com/gallery/im-18-624-points-from-glorious-so-heres-picture-of-dog-with-two-his-mouth-XgbZdeA",
        "username": "user98",
    }
}

comments = {
    0: {
        "id": 0,
        "post_id": 0,
        "upvotes": 8,
        "text": "Thanks for my first Reddit gold!",
        "username": "user98",
    }
}


comment_id_counter = 1
post_id_counter = 1


posts_bp = Blueprint("posts", __name__, url_prefix="/api")
# comments_bp = Blueprint('comments', __name__)


## POST ROUTES ##


@posts_bp.route("/posts/", methods=["GET"])
def get_all_posts():
    # Return list of all posts present
    # posts_list = []
    # for post in posts.values():
    #     post_data = {
    #         'id': post['id'],
    #         'upvotes': post['upvotes'],
    #         'title': post['title'],
    #         'link': post['link'],
    #         'username': post['username'],
    #     }
    #     posts_list.append(post_data)

    # return jsonify({"posts": posts_list}), 200

    return jsonify({"posts": list(posts.values())}), 200


@posts_bp.route("/posts/sorted", methods=["GET"])
def get_all_posts_ordered():
    # Return list of all posts present ordered (dec, inc) by upvotes

    ordering = request.args.get("ordering", "")
    if not ordering or ordering not in ["dec", "inc"]:
        # default to decreasing
        ordering = "dec"

    post_list = list(posts.values())
    if ordering == "dec":
        post_list.sort(key=lambda p: (-p["upvotes"], p["id"]))
    else:
        post_list.sort(key=lambda p: (p["upvotes"], p["id"]))

    return jsonify({"posts": post_list}), 200


# @posts_bp.route("/api/posts/", methods=["POST"])
@posts_bp.route("/posts/", methods=["POST"])
def create_post():
    # Create a new post using the data provided
    global post_id_counter

    # get data from request body
    data = request.json

    # check the fields in data (should have title)
    field_list = ["title", "link", "username"]
    if not all(key in data for key in field_list):
        return jsonify({"error": "Missing fields in request"}), 400

    # TODO: validate link value here

    # new post
    post = {
        "id": post_id_counter,
        "upvotes": 1,
        "title": data["title"],
        "link": data["link"],
        "username": data["username"],
        # "comments": []
    }

    # add new post to our dictionary (aka db)
    posts[post_id_counter] = post
    post_id_counter += 1

    # post_data = {
    #     "id": post['id'],
    #     "upvotes": post['upvotes'],
    #     "title": post["title"],
    #     "link": post["link"],
    #     "username": post["username"],
    # }

    # return jsonify(post_data), 201
    return jsonify(post), 201


# @posts_bp.route("/api/posts/<int:id>/", methods=["GET"])
@posts_bp.route("/posts/<int:id>/", methods=["GET"])
def get_post(id):
    # Returns the post with given id
    if id not in posts:
        return jsonify({"error": "Post not found"}), 404

    post = posts[id]
    # post_data = {
    #     "id": post['id'],
    #     "upvotes": post['upvotes'],
    #     "title": post["title"],
    #     "link": post["link"],
    #     "username": post["username"],
    # }

    # return jsonify(post_data), 200
    return jsonify(post), 200


# @posts_bp.route("/api/posts/<int:id>/", methods=["DELETE"])
@posts_bp.route("/posts/<int:id>/", methods=["DELETE"])
def delete_post(id):
    # Delete post with given id
    if id not in posts:
        return jsonify({"error": "Post not found"}), 404
    post = posts.pop(id)
    # post_data = {
    #     "id": post['id'],
    #     "upvotes": post['upvotes'],
    #     "title": post["title"],
    #     "link": post["link"],
    #     "username": post["username"],
    # }

    # # TODO: also delete the comments below
    # return jsonify(post_data), 200

    # Delete associated comments
    comments_to_delete = [
        cid for cid, comment in comments.items() if comment["post_id"] == id
    ]
    for cid in comments_to_delete:
        del comments[cid]

    return jsonify(post), 200


# @posts_bp.route("/api/posts/<int:id>/upvote/", methods=["POST"])
@posts_bp.route("/posts/<int:id>/upvote/", methods=["POST"])
def upvote_post(id):
    # Increment upvotes on a specific post (default +1)
    if id not in posts:
        return jsonify({"error": "Post not found"}), 404

    upvote_offset = 1  # default
    if request.data:
        # request body provided
        data = request.json
        field_list = ["upvotes"]
        if not all(key in data for key in field_list):
            return jsonify({"error": "Missing fields in request"}), 400
        # validate request body value
        if not isinstance(data["upvotes"], int) or data["upvotes"] < 1:
            return jsonify({"error": "Invalid value in request"}), 400

        upvote_offset = data["upvotes"]

    post = posts[id]
    post["upvotes"] += upvote_offset

    # post_data = {
    #     "id": post['id'],
    #     "upvotes": post['upvotes'],
    #     "title": post["title"],
    #     "link": post["link"],
    #     "username": post["username"],
    # }

    # return jsonify(post_data), 200

    return jsonify(post), 200


## COMMENT ROUTES ##


@app.route("/api/posts/<int:id>/comments/", methods=["GET"])
def get_comments(id):
    # Get the list of comments for a specific post
    if id not in posts:
        return jsonify({"error": "Post not found"}), 404

    comments_list = []
    for comment in posts[id]["comments"]:
        comment_data = {
            "id": comment["id"],
            "upvotes": comment["upvotes"],
            "text": comment["text"],
            "username": comment["username"],
        }
        comments_list.append(comment_data)

    # return jsonify({"comments": posts[id]["comments"]}), 200
    return jsonify({"comments": comments_list}), 200


@app.route("/api/posts/<int:id>/comments/", methods=["POST"])
def create_comment(id):
    # Post a comment for a specific post
    global comment_id_counter
    if id not in posts:
        return jsonify({"error": "Post not found"}), 404

    data = request.json
    fields_list = ["text", "username"]
    if not all(key in data for key in fields_list):
        return jsonify({"error": "Missing fields in request"}), 400

    comment = {
        "id": comment_id_counter,
        "post_id": id,
        "upvotes": 1,
        "text": data["text"],
        "username": data["username"],
    }
    posts[id]["comments"].append(comment)
    comment_id_counter += 1

    comment_data = {
        "id": comment["id"],
        "upvotes": comment["upvotes"],
        "text": comment["text"],
        "username": comment["username"],
    }

    # return jsonify(comment), 201
    return jsonify(comment_data), 201


@app.route("/api/posts/<int:pid>/comments/<int:cid>/", methods=["POST"])
def edit_comment(pid, cid):
    # Edit a specific comment on a specific post
    if pid not in posts:
        return jsonify({"error": "Post not found"}), 404

    if cid not in comments:
        return jsonify({"error": "Comment not found"}), 404

    comment = comments[cid]
    if comment["post_id"] != pid:
        return jsonify({"error": "Comment is on different Post"}), 404

    # can only update text field of comments
    data = request.json
    fields_list = ["text"]
    if not all(key in data for key in fields_list):
        return jsonify({"error": "Missing text field in request"}), 400

    comment["text"] = data["text"]

    comment_data = {
        "id": comment["id"],
        "upvotes": comment["upvotes"],
        "text": comment["text"],
        "username": comment["username"],
    }
    return jsonify(comment_data), 200


app.register_blueprint(posts_bp)
# app.register_blueprint(comments_bp)


if __name__ == "__main__":
    print(app.url_map)
    app.run(host="0.0.0.0", port=5000, debug=True)
