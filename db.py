from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upvotes = db.Column(db.Integer, default=1)
    title = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    comments = db.relationship("Comment", backref="post", lazy=True)

    def serialize(self):
        return {
            "id": self.id,
            "upvotes": self.upvotes,
            "title": self.title,
            "link": self.link,
            "username": self.username,
        }


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    upvotes = db.Column(db.Integer, default=1)
    text = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(50), nullable=False)

    def serialize(self):
        return {
            "id": self.id,
            "upvotes": self.upvotes,
            "text": self.text,
            "username": self.username,
        }
