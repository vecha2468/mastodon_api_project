# Created by Chanukya Vejandla and Harsha Vardhan
# with error handling and proper routes
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mastodon_service
from mastodon_service import InvalidInputError, RateLimitError, APIError

# Initialize Flask application 
app = Flask(__name__)
# Secret key needed for session management and flash messages
app.secret_key = 'supersecretkey'  # For flashing messages



@app.route("/", methods=["GET", "POST"])
def index():
    """
    Main page handler - shows form
    GET: Displays the form and retrieved post
    POST: Processes form submissions for create/delete operations
    """
    post = None
    # Check if a post ID was provided in query parameters
    post_id = request.args.get("post_id")
    
    # If post_id is present, try to retrieve the post
    if post_id:
        try:
            post = mastodon_service.retrieve(post_id)
        except InvalidInputError as e:
            # Post not found or ID invalid
            flash(f"Error: {str(e)}", "danger")
        except RateLimitError:
            # API rate limit hit
            flash("Rate limit reached. Please try again later.", "warning")
        except APIError as e:
            # Other API errors
            flash(f"API Error: {str(e)}", "danger")

    # Handle form submissions
    if request.method == "POST":
        if "create" in request.form:
            # Creating a new post
            status = request.form["status"]
            try:
                post = mastodon_service.create(status)
                flash("Post created successfully!", "success")
            except InvalidInputError as e:
                # Input validation failed
                flash(f"Error: {str(e)}", "danger")
            except RateLimitError:
                # API rate limit hit
                flash("Rate limit reached. Please try again later.", "warning")
            except APIError as e:
                # Other API errors
                flash(f"API Error: {str(e)}", "danger")
                
        elif "delete" in request.form and post_id:
            # Deleting an existing post
            try:
                success = mastodon_service.delete(post_id)
                if success:
                    flash("Post deleted successfully!", "success")
                    # Redirect to clean URL after successful deletion
                    return redirect(url_for("index"))
                else:
                    flash("Failed to delete post.", "danger")
            except InvalidInputError as e:
                # Post not found or ID invalid
                flash(f"Error: {str(e)}", "danger")
            except RateLimitError:
                # API rate limit hit
                flash("Rate limit reached. Please try again later.", "warning")
            except APIError as e:
                # Other API errors
                flash(f"API Error: {str(e)}", "danger")

    # Render template with any post data and flash messages
    return render_template("index.html", post=post)


# API Endpoints 

@app.route("/create", methods=["POST"])
def create_post():
    """
    API endpoint to create a post
    """
    try:
        # Verify content type is JSON
        if not request.is_json:
            return jsonify({"success": False, "error": "Request must be JSON"}), 400
        
        # Parse JSON data
        data = request.get_json()
        if not data or "status" not in data:
            return jsonify({"success": False, "error": "Missing status field"}), 400
        
        # Create post through service
        result = mastodon_service.create(data["status"])
        return jsonify({"success": True, "post_id": result.get("id")}), 200
        
    except InvalidInputError as e:
        # Input validation failed 
        return jsonify({"success": False, "error": str(e)}), 400
    except RateLimitError as e:
        # Rate limit exceeded 
        return jsonify({"success": False, "error": str(e)}), 429
    except APIError as e:
        # Other API errors
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/retrieve/<post_id>", methods=["GET"])
def retrieve_post(post_id):
    """
    API endpoint to retrieve a post by ID
    """
    try:
        # Retrieve post through service
        post = mastodon_service.retrieve(post_id)
        return jsonify({"success": True, "post": post}), 200
    except InvalidInputError as e:
        # Post not found 
        return jsonify({"success": False, "error": str(e)}), 404
    except RateLimitError as e:
        # Rate limit exceeded 
        return jsonify({"success": False, "error": str(e)}), 429
    except APIError as e:
        # Other errors 
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/delete/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    """
    API endpoint to delete a post by ID
    
    Deletes the post with the provided ID.
    """
    try:
        # Delete post through service
        success = mastodon_service.delete(post_id)
        if success:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "error": "Failed to delete post"}), 500
    except InvalidInputError as e:
        # Post not found 
        return jsonify({"success": False, "error": str(e)}), 404
    except RateLimitError as e:
        # Rate limit exceeded 
        return jsonify({"success": False, "error": str(e)}), 429
    except APIError as e:
        # Other API errors 
        return jsonify({"success": False, "error": str(e)}), 500

# Run the application in debug mode when executed directly
if __name__ == "__main__":
    app.run(debug=True)