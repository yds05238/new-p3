from flask import Flask, jsonify, request
from db import db, Post, Comment
from sqlalchemy import desc, asc

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///reddit_clone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/api/posts/", methods=["GET"])
def get_all_posts():
    posts = Post.query.all()
    return jsonify({"posts": [post.serialize() for post in posts]}), 200


@app.route("/api/posts/ordered", methods=["GET"])
def get_all_posts_ordered():
    ordering = request.args.get("ordering", "dec")
    if ordering not in ["dec", "inc"]:
        return jsonify({"error": "Invalid ordering parameter"}), 400

    order = desc(Post.upvotes) if ordering == "dec" else asc(Post.upvotes)
    posts = Post.query.order_by(order).all()
    return jsonify([post.serialize() for post in posts]), 200


@app.route("/api/posts/", methods=["POST"])
def create_post():
    data = request.json
    if not all(key in data for key in ["title", "link", "username"]):
        return jsonify({"error": "Missing fields in request"}), 400

    new_post = Post(title=data["title"], link=data["link"], username=data["username"])
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.serialize()), 201


@app.route("/api/posts/<int:id>/", methods=["GET"])
def get_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post.serialize()), 200


@app.route("/api/posts/<int:id>/", methods=["DELETE"])
def delete_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify(post.serialize()), 200


@app.route("/api/posts/<int:id>/upvote/", methods=["POST"])
def upvote_post(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    upvote_offset = 1
    if request.json and "upvotes" in request.json:
        upvote_offset = request.json["upvotes"]
        if not isinstance(upvote_offset, int) or upvote_offset < 1:
            return jsonify({"error": "Invalid value in request"}), 400

    post.upvotes += upvote_offset
    db.session.commit()
    return jsonify(post.serialize()), 200


@app.route("/api/posts/<int:id>/comments/", methods=["GET"])
def get_comments(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return (
        jsonify({"comments": [comment.serialize() for comment in post.comments]}),
        200,
    )


@app.route("/api/posts/<int:id>/comments/", methods=["POST"])
def create_comment(id):
    post = Post.query.get(id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    data = request.json
    if not all(key in data for key in ["text", "username"]):
        return jsonify({"error": "Missing fields in request"}), 400

    new_comment = Comment(text=data["text"], username=data["username"], post_id=id)
    db.session.add(new_comment)
    db.session.commit()
    return jsonify(new_comment.serialize()), 201


@app.route("/api/posts/<int:pid>/comments/<int:cid>/", methods=["POST"])
def edit_comment(pid, cid):
    post = Post.query.get(pid)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    comment = Comment.query.get(cid)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    if comment.post_id != pid:
        return jsonify({"error": "Comment not for this post"}), 400

    data = request.json
    if "text" not in data:
        return jsonify({"error": "Missing fields in request"}), 400

    comment.text = data["text"]
    db.session.commit()
    return jsonify(comment.serialize()), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
