import os
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps

def save_avatar(uploaded_file, public_id):
    filename = secure_filename(uploaded_file.filename)
    _, ext = os.path.splitext(filename)
    if not ext:
        ext = '.png'
    ext = ext.lower()
    filename = f"avatar{ext}"
    avatar_folder = os.path.join(current_app.root_path, "static", "avatars", public_id)
    if not os.path.exists(avatar_folder):
        os.makedirs(avatar_folder)
    file_path = os.path.join(avatar_folder, filename)
    uploaded_file.save(file_path)

    with Image.open(file_path) as img:
        img = ImageOps.exif_transpose(img)
        size = min(img.width, img.height)
        img_cropped = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))
        img_resized = img_cropped.resize((256, 256), Image.Resampling.LANCZOS)
        img_resized.save(file_path)

    relative_path = os.path.join(public_id, filename)
    return relative_path, filename

def rename_avatar_directory(old_public_id, new_public_id):
    old_path = os.path.join(current_app.root_path, "static", "avatars", old_public_id)
    new_path = os.path.join(current_app.root_path, "static", "avatars", new_public_id)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)

def clear_old_avatars(public_id, current_filename):
    folder = os.path.join(current_app.root_path, "static", "avatars", public_id)
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            if filename != current_filename:
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)