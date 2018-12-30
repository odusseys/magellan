from io import BytesIO
from PIL import Image


def resize_image_to_square(file, size):
    image = Image.open(file)
    image.thumbnail((size, size))
    b = BytesIO()
    image.save(b, 'PNG')
    b.seek(0)
    return b
