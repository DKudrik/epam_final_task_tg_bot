import os
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


def get_final_image_url(
    user_id: int,
    text: Optional[str] = None,
    font: Optional[str] = None,
    font_size: Optional[int] = None,
    private: Optional[bool] = None,
) -> str:
    """
    Gets the url of the final images from one of the aux funcs and returns it
    further.

    :param user_id: user id
    :param text: text for adding on the image
    :param font: selected font
    :param font_size: selected font size
    :param private: private GIF flag
    :return: url of the final image
    """
    images = []

    for file in os.listdir("."):
        if file.endswith(("jpg", "jpeg", "png")) and file.startswith(str(user_id)):
            images.append(file)

    if len(images) > 1:
        return create_gif_and_return_url(images, private=private)
    elif len(images) == 1:
        image_name = images[0]
        return add_text_on_image_and_return_url(text, image_name, font, font_size)


def create_gif_and_return_url(images: list, private: Optional[bool] = None) -> str:
    if not os.path.exists("GIFS"):
        os.makedirs("GIFS")
    name = images[0]
    gif_name = name.split(".")[0] + ".gif"
    if private:
        gif_name = "private-" + gif_name
    frames = []
    max_width = 0
    max_height = 0
    for image in images:
        width, height = Image.open(image).size
        max_width = width if width > max_width else max_width
        max_height = height if height > max_height else max_height
    for image in images:
        resize_and_draw_watermark(max_width, max_height, image)
        new_frame = Image.open(image)
        frames.append(new_frame)
    frames[0].save(
        f"GIFS/{gif_name}",
        append_images=frames[1:],
        save_all=True,
        duration=800,
        Loop=0,
    )
    url = "GIFS/" + gif_name
    for image in images:
        os.remove(image)
    return url


def resize_and_draw_watermark(max_width: int, max_height: int, image: str) -> None:
    """
    Opens an image from the received, resizes if needed and adds watermark
    on it so the final GIF would be with watermark.

    :param max_height: max height to resize smaller images
    :param max_width: max width to resize smaller images
    :param image: url as a string
    :return: None
    """
    with Image.open(image) as image:
        rgb_image = image.convert("RGB")
        rgb_image.save(image.filename)
        background = Image.new("RGB", (max_width, max_height), (255, 255, 255))
        offset = ((max_width - image.width) // 2, (max_height - image.height) // 2)
        background.paste(rgb_image, offset)
        draw = ImageDraw.Draw(background)
        text = "Picture process bot"
        font = ImageFont.truetype("fonts/UKIJDiY.ttf", 62, encoding="UTF-8")
        width, height = background.size
        draw.text((0, height // 2), text, (240, 240, 240), font=font)
        background.save(image.filename)
        background.close()
        rgb_image.close()


def add_text_on_image_and_return_url(
    text, image_name, font=None, font_size=None
) -> str:
    if not os.path.exists("Processed_images"):
        os.makedirs("Processed_images")
    with Image.open(image_name) as image:
        rgb_image = image.convert("RGB")
        draw = ImageDraw.Draw(rgb_image)
        text = text
        font_size = font_size if font_size else 32
        font_type = ("fonts/" + font + ".ttf") if font else "fonts/UKIJDiY.ttf"
        font = ImageFont.truetype(font_type, font_size, encoding="UTF-8")
        draw.text((0, 0), text, (255, 0, 0), font=font)
        new_name = "Processed_images/" + image_name
        rgb_image.save(new_name)
        rgb_image.close()
    os.remove(image_name)
    return new_name
