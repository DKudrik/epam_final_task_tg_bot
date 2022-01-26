import os

from PIL import Image, ImageDraw, ImageFont


def count_images(user_id, text=None, font=None, font_size=None, private=None):
    images = []

    for file in os.listdir("."):
        if file.endswith(("jpg", "jpeg", "png")) and file.startswith(str(user_id)):
            images.append(file)

    if len(images) > 1:
        return create_gif(images, private=private)
    elif len(images) == 1:
        image_name = images[0]
        return add_text_on_image(text, image_name, font, font_size)


def create_gif(images, private=None):
    if not os.path.exists("GIFS"):
        os.makedirs("GIFS")
    name = images[0]
    gif_name = name.split(".")[0] + ".gif"
    if private:
        gif_name = "private-" + gif_name
    frames = []
    for image in images:
        draw_watermark(image)
        new_frame = Image.open(image)
        frames.append(new_frame)
    frames[0].save(
        f"GIFS/{gif_name}",
        append_images=frames[1:],
        save_all=True,
        duration=500,
        Loop=0,
    )
    url = "GIFS/" + gif_name
    for image in images:
        os.remove(image)
    return url


def draw_watermark(image):
    with Image.open(image) as image:
        rgb_image = image.convert("RGB")
        draw = ImageDraw.Draw(rgb_image)
        text = "Picture process bot"
        font = ImageFont.truetype("fonts/UKIJDiY.ttf", 62, encoding="UTF-8")
        width, height = image.size
        draw.text((0, height // 2), text, (240, 240, 240), font=font)
        rgb_image.save(image.filename)
        rgb_image.close()


def add_text_on_image(text, image_name, font=None, font_size=None):
    if not os.path.exists("Processed_images"):
        os.makedirs("Processed_images")
    with Image.open(image_name) as image:
        rgb_image = image.convert("RGB")
        draw = ImageDraw.Draw(rgb_image)
        text = text
        font_size = int(font_size) if font_size else 32
        font = ("fonts" + font + ".ttf") if font else "fonts/UKIJDiY.ttf"
        font = ImageFont.truetype(font, font_size, encoding="UTF-8")
        draw.text((0, 0), text, font=font)
        new_name = "Processed_images/" + image_name
        rgb_image.save(new_name)
        rgb_image.close()
    os.remove(image_name)
    return new_name
