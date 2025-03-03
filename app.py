#created by Chanukya Vejandla and Harsha Vardhan
from flask import Flask, render_template, request, redirect, url_for, flash
import mastodon_service

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # For flashing messages

@app.route("/", methods=["GET", "POST"])
def index():
    post = None
    post_id = request.args.get("post_id")
    if post_id:
        post = mastodon_service.retrieve(post_id)

    if request.method == "POST":
        if "create" in request.form:
            status = request.form["status"]
            post = mastodon_service.create(status)
            flash("Post created successfully!", "success")
        elif "delete" in request.form and post_id:
            mastodon_service.delete(post_id)
            flash("Post deleted successfully!", "success")
            return redirect(url_for("index"))

    return render_template("index.html", post=post)

if __name__ == "__main__":
    app.run(debug=True)
