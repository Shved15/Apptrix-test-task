from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image


def apply_watermark(image, watermark_path='media/watermark/watermark.png'):
    """Метод применяет водяной знак к изображению."""

    # Открываем водяной знак и изображение, конвертируем их в формат RGBA
    watermark = Image.open(watermark_path).convert("RGBA")
    base_image = Image.open(image).convert("RGBA")

    base_width, base_height = base_image.size

    # Меняем размер изображения (1/4 от размеров базового изображения)
    watermark_width = base_width // 4
    watermark_height = base_height // 4

    # Меняем размер водяного знака с помощью алгоритма Lanczos
    watermark = watermark.resize((watermark_width, watermark_height), Image.LANCZOS)

    # Определяем позицию в правом нижнем углу, накладываем водяной знак, создаем буфер сохранения и сохраняем рез.
    watermark_position = (base_width - watermark_width, base_height - watermark_height)
    base_image.paste(watermark, watermark_position, watermark)
    output = BytesIO()
    base_image.save(output, format='PNG')
    output.seek(0)

    return ContentFile(output.read(), image.name)
