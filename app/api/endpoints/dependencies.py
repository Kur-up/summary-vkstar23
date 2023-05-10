import os
import datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from base64 import b64encode
from hashlib import sha256
from hmac import HMAC
from urllib.parse import urlencode

from typing import Annotated
from fastapi.security import APIKeyHeader
from fastapi import Depends
from fastapi import Body
from fastapi import HTTPException
from fastapi import status

from ..models.planets import PlanetModelCheckIn
from ..models.planets import PlanetModelCheckOut
from ..models.planets import planets_list

from ...db.users_queries import get_or_create_user

VK_SECRET = os.getenv("VK_SECRET")
auth_header = APIKeyHeader(name="Authorization", scheme_name="VkMALaunchParams")


async def vk_sign_check(
    launch_params: Annotated[str, Depends(auth_header)]
) -> int | HTTPException:
    launch_params = launch_params[3:]
    items = launch_params.split("&")
    query = {}
    for item in items:
        key, value = item.split("=")
        query[key] = value

    if not query.get("sign"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    vk_subset = sorted(filter(lambda key: key.startswith("vk_"), query))

    if not vk_subset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    ordered = {k: query[k] for k in vk_subset}

    hash_code = b64encode(
        HMAC(
            VK_SECRET.encode(), urlencode(ordered, doseq=True).encode(), sha256
        ).digest()
    ).decode("utf-8")

    if hash_code[-1] == "=":
        hash_code = hash_code[:-1]

    fixed_hash = hash_code.replace("+", "-").replace("/", "_")
    if not query.get("sign") == fixed_hash:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        return int(query["vk_user_id"])


async def generate_ticket(vk_user_id: int, low_quality: bool) -> None:
    db_user = await get_or_create_user(vk_user_id)
    datetime_entity = datetime.datetime.now() + datetime.timedelta(hours=3)
    day = str(datetime_entity.day)
    if len(day) == 1:
        day = "0" + day

    month = str(datetime_entity.month)
    if len(month) == 1:
        month = "0" + month

    year = str(datetime_entity.year)[2:]

    hour = str(datetime_entity.hour)
    if len(hour) == 1:
        hour = "0" + hour

    minute = str(datetime_entity.minute)
    if len(minute) == 1:
        minute = "0" + minute

    font_path = "media/fonts/VK Sans Display Bold.otf"
    image = Image.open("media/tickets/base.png")
    draw = ImageDraw.Draw(image)
    font_size = 133
    font = ImageFont.truetype(font_path, font_size)
    text_color = (112, 0, 255)

    text_position = (1357, 457)
    text = db_user.first_name
    draw.text(text_position, text, font=font, fill=text_color)

    text_position = (1357, 595)
    text = db_user.last_name
    draw.text(text_position, text, font=font, fill=text_color)

    font_path = "media/fonts/VK Sans Display Light.otf"
    font_size = 80
    font = ImageFont.truetype(font_path, font_size)
    text_color = (255, 255, 255)

    text_position = (1361, 1063)
    text = f"{day}.{month}.{year}"
    draw.text(text_position, text, font=font, fill=text_color)

    text_position = (1717, 1063)
    text = f"{hour}:{minute}"
    draw.text(text_position, text, font=font, fill=text_color)

    save_path = f"media/tickets/{vk_user_id}.png"
    if low_quality:
        width, height = image.size
        image = image.resize((width // 3, height // 3))
        save_path = f"media/tickets/{vk_user_id}low.png"

    image.save(save_path)


example = {
    "mercury": {"club_id": 0, "planet": "mercury", "user_code": 0},
    "venus": {"club_id": 0, "planet": "venus", "user_code": 0},
    "earth": {"club_id": 0, "planet": "earth", "user_code": 0},
    "mars": {"club_id": 0, "planet": "mars", "user_code": 0},
    "jupiter": {"club_id": 0, "planet": "jupiter", "user_code": 0},
    "saturn": {"club_id": 0, "planet": "saturn", "user_code": 0},
    "uranus": {"club_id": 0, "planet": "uranus", "user_code": 0},
    "neptune": {"club_id": 0, "planet": "neptune", "user_code": 0},
}


async def codes_check(
    answers: Annotated[dict[str, PlanetModelCheckIn], Body(example=example)]
):
    if not len(answers) == 8:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    planets_dict = {obj.planet: obj for obj in planets_list}

    result = {}
    for key in planets_dict.keys():
        if not answers.get(key):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        obj = PlanetModelCheckOut(
            club_id=planets_dict[key].club_id,
            planet=planets_dict[key].planet,
            user_code=answers[key].user_code,
        )

        if answers[key].user_code == planets_dict[key].code:
            obj.code_is_valid = True

        result[key] = obj

    return result
