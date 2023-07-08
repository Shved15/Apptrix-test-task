from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


def apply_watermark(image, watermark_path='media/watermark/watermark.png'):
    watermark = Image.open(watermark_path).convert("RGBA")
    base_image = Image.open(image).convert("RGBA")

    base_width, base_height = base_image.size

    watermark_width = base_width // 4
    watermark_height = base_height // 4

    watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)

    watermark_position = (base_width - watermark_width, base_height - watermark_height)
    base_image.paste(watermark, watermark_position, watermark)

    output = BytesIO()
    base_image.save(output, format='PNG')
    output.seek(0)

    return ContentFile(output.read(), image.name)
