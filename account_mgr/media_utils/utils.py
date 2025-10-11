 
import os
import secrets
from PIL import Image
from account_mgr import app
from flask import Blueprint
from flask_login import current_user
from werkzeug.utils import secure_filename


img_utils = Blueprint(
    "img_utils", __name__, template_folder="templates", static_folder="static"
)


def save_user_picture(form_picture):
    # Generate a random hexadecimal name for the image
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    
    # Sanitize the filename using secure_filename
    picture_fn = secure_filename(random_hex + f_ext)
    
    # Define the picture path
    picture_path = os.path.join(
        app.root_path, "static/media", picture_fn
    )
    
    # Remove the existing user profile picture if it exists
    if os.path.exists(
        os.path.join(app.root_path, "static/media", current_user.user_profile)):
        os.remove(os.path.join(app.root_path, "static/media", current_user.user_profile))
    
    # Resize the image
    output_size = (750, 750)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn


def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return (
        "." in filename
        and os.path.splitext(filename)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def save_picture(form_picture):
    # Generate a random hexadecimal name for the image
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.config["UPLOAD_FOLDER"], secure_filename(picture_fn)
    )

    # Resize the image
    output_size = (700, 700) 
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn