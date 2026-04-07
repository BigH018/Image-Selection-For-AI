import os
import shutil

IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}


def get_image_files(directory):
    """Return a list of image filenames found in the given directory."""
    return [
        f for f in os.listdir(directory)
        if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
    ]


def move_image(src_dir, filename, dest_dir):
    """Move an image file from src_dir to dest_dir."""
    shutil.move(
        os.path.join(src_dir, filename),
        os.path.join(dest_dir, filename),
    )
