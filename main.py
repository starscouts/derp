import requests
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO

import config.raindrops as config

DERPI_ENDPOINT = "https://derpibooru.org/api/v1/json/search/images"
NOTIFY_ENDPOINT = f"https://notifications.equestria.dev/derpibooru-{config.user_name}"


def should_notify(target_post, sent_list):
    return target_post['id'] not in sent_list and target_post['processed'] and not target_post["deletion_reason"]


def do_request(query, filter_id):
    params = {"key": api_key, "q": query, "filter_id": filter_id, "per_page": 50}

    return requests.get(DERPI_ENDPOINT, params=params)


def get_artists(tags):
    artists = filter(lambda tag: tag.startswith("artist:"), tags)
    artists = map(lambda tag: tag.removeprefix("artist:"), artists)
    artists = format_artists(list(artists))

    return artists


def format_artists(artists):
    if len(artists) == 0:
        return "Anonymous artist"

    if len(artists) == 1:
        return artists[0]

    return ", ".join(artists[:-1]) + " and " + artists[-1]


def get_censored_tags(tags, trigger_tags):
    overlap = tags.intersection(trigger_tags)
    return overlap


def get_thumbnail(image_url, censor, resolution, target_post):
    if not target_post['mime_type'].startswith("image/"):
        return None

    image = Image.open(BytesIO(requests.get(image_url).content))
    image = image.convert("RGBA")

    thumb = image.resize(resolution)
    thumb = thumb.filter(ImageFilter.GaussianBlur(80))
    thumb = ImageEnhance.Brightness(thumb).enhance(0.5)

    if censor:
        image = image.filter(ImageFilter.GaussianBlur(40))

    image = ImageOps.contain(image, resolution)
    thumb.paste(image, ((resolution[0] - image.size[0]) // 2, 0))

    buffer = BytesIO()
    thumb.save(buffer, format="PNG")

    return buffer


def get_prefix(censored_tags):
    if len(censored_tags) > 0:
        prefix = "⚠️ " + ", ".join(censored_tags)
    else:
        prefix = "safe"

    return prefix


def get_description(target_post):
    if not target_post["description"]:
        return None

    return target_post["description"].replace("\r", " ").replace("\n", " ").strip()


def get_notify_data(target_post, thumb_res, trigger_tags):
    post_id = target_post["id"]
    width = target_post["width"]
    height = target_post["height"]
    tags = target_post["tags"]
    censor_tags = get_censored_tags(set(tags), trigger_tags)
    censor = "safe" not in tags

    artists = get_artists(tags)
    prefix = get_prefix(censor_tags)
    description = get_description(target_post)

    title = f"#{post_id} - by {artists}"
    message = f"{prefix} - {width}x{height}"

    if description:
        message += f" - {description}"

    click = f"https://derpibooru.org/images/{post_id}"
    thumb = get_thumbnail(target_post['representations']['medium'], censor, thumb_res, target_post)
    notify_data = {"title": title, "message": message, "click": click, "thumb": thumb}

    return notify_data


def send_notification(notify_data, auth):
    requests.post(NOTIFY_ENDPOINT, data=notify_data["thumb"].getvalue() if notify_data["thumb"] else None,
                  headers={"Authorization": f"Basic {auth}", "User-Agent": "Mozilla/5.0 (+Derp/0.0)",
                           "Tags": "derpibooru", "Title": notify_data["title"].encode("utf-8"),
                           "Message": notify_data["message"].encode("utf-8"),
                           "Click": notify_data["click"].encode("utf-8"),
                           "Icon": "https://derpicdn.net/img/view/2020/7/23/2406370.png"})


api_key = open(config.token_path, "r").read().strip()
ntfy_auth = open("auth.txt", "r").read().strip()

response = do_request(config.query, config.filter_id if config.filter_id >= 0 else None)
data = response.json()

with open(config.sent_list_path, "r+") as f:
    sent = [int(image_id.strip()) for image_id in f.readlines()]

    for post in reversed(data['images']):
        if not should_notify(post, sent):
            continue

        post_notify_data = get_notify_data(post, config.resolution, config.triggers)
        send_notification(post_notify_data, ntfy_auth)

        print(post['id'])
        sent.append(post['id'])
        f.write(f"{post['id']}\n")