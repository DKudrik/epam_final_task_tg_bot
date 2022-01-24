import os

from PIL import Image, ImageDraw, ImageFont


def count_images(user_id, text=None):
    images = []

    for file in os.listdir("."):
        if file.endswith(("jpg", "jpeg", "png")) and file.startswith(str(user_id)):
            images.append(file)

    if len(images) > 1:
        print("creating gif")
        return create_gif(images)
    else:
        image_name = images[0]
        print("adding text")
        return add_text_on_image(text, image_name)


def create_gif(images):
    if not os.path.exists("GIFS"):
        os.makedirs("GIFS")
    name = images[0]
    gif_name = name.split(".")[0] + ".gif"
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
        font = ImageFont.truetype("UKIJDiY.ttf", 62, encoding="UTF-8")
        width, height = image.size
        draw.text((0, height // 2), text, (240, 240, 240), font=font)
        rgb_image.save(image.filename)
        rgb_image.close()


def add_text_on_image(text, image_name):
    if not os.path.exists("processed_images"):
        os.makedirs("processed_images")
    with Image.open(image_name) as image:
        rgb_image = image.convert("RGB")
        draw = ImageDraw.Draw(rgb_image)
        text = text
        font = ImageFont.truetype("UKIJDiY.ttf", 62, encoding="UTF-8")
        draw.text((0, 0), text, font=font)
        new_name = "processed_images/" + image_name
        rgb_image.save(new_name)
        rgb_image.close()
    os.remove(image_name)
    return new_name
