import os
from enum import Enum

from typing import Any
from typing import Dict
from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from fastapi import HTTPException
from fastapi.responses import FileResponse

from ..models.planets import PlanetModel
from ..models.planets import PlanetModelCheckOut
from ..models.planets import planets_list

from ...db import users_queries

from .dependencies import vk_sign_check
from .dependencies import codes_check


router = APIRouter()


class StaticFilesEnum(str, Enum):
    mercury = "mercury.json"
    venus = "venus.json"
    earth = "earth.json"
    mars = "mars.json"
    jupiter = "jupiter.json"
    saturn = "saturn.json"
    uranus = "uranus.json"
    neptune = "neptune.json"


responses = {
    200: {
        "description": "Success response",
        "content": {
            "application/json": {
                "example": {
                    "mercury": {"club_id": 123456, "planet": "mercury"},
                    "venus": {"club_id": 123456, "planet": "venus"},
                    "earth": {"club_id": 123456, "planet": "earth"},
                    "mars": {"club_id": 123456, "planet": "mars"},
                    "jupiter": {"club_id": 123456, "planet": "jupiter"},
                    "saturn": {"club_id": 123456, "planet": "saturn"},
                    "uranus": {"club_id": 123456, "planet": "uranus"},
                    "neptune": {"club_id": 123456, "planet": "neptune"},
                }
            }
        },
    }
}


@router.get(
    "/get",
    name="Get information about the planets",
    tags=["Planets"],
    response_model_exclude=["code"],
    response_model=Dict[str, PlanetModel],
    responses=responses,
)
async def planets_get(vk_user_id: Annotated[int, Depends(vk_sign_check)]) -> Any:
    """# Get information about the planets #
    Created for rendering and connecting data on the frontend side of the application.
    """

    result = {}
    for planet in planets_list:
        result[planet.planet] = planet.dict()

    return result


responses = {
    200: {
        "description": "Success response",
        "content": {"application/json": {"example": "JSON dict"}},
    }
}


@router.get(
    "/getstatic/{file_path}",
    name="Get .json files of planets",
    tags=["Planets"],
    responses=responses,
)
async def static_get(file_path: StaticFilesEnum):
    """# Get .json files of planets #
    Created for design rendering. Pictures are placed on the backend for the convenience of replacing images.
    """
    file_full_path = f"static/{file_path}"

    if not os.path.isfile(file_full_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    return FileResponse(path=file_full_path)


responses = {
    200: {
        "description": "Success response",
        "content": {
            "application/json": {
                "example": {
                    "mercury": {
                        "club_id": 123456,
                        "planet": "mercury",
                        "user_code": 0,
                        "code_is_valid": True,
                    },
                    "venus": {
                        "club_id": 123456,
                        "planet": "venus",
                        "user_code": 0,
                        "code_is_valid": True,
                    },
                    "earth": {
                        "club_id": 123456,
                        "planet": "earth",
                        "user_code": 0,
                        "code_is_valid": True,
                    },
                    "mars": {
                        "club_id": 123456,
                        "planet": "mars",
                        "user_code": 0,
                        "code_is_valid": True,
                    },
                    "jupiter": {
                        "club_id": 123456,
                        "planet": "jupiter",
                        "user_code": 0,
                        "code_is_valid": False,
                    },
                    "saturn": {
                        "club_id": 123456,
                        "planet": "saturn",
                        "user_code": 0,
                        "code_is_valid": False,
                    },
                    "uranus": {
                        "club_id": 123456,
                        "planet": "uranus",
                        "user_code": 0,
                        "code_is_valid": False,
                    },
                    "neptune": {
                        "club_id": 123456,
                        "planet": "neptune",
                        "user_code": 0,
                        "code_is_valid": False,
                    },
                }
            }
        },
    }
}


@router.post(
    "/checkcode",
    name="Check the codes entered by the user",
    tags=["Planets"],
    response_model=Dict[str, PlanetModelCheckOut],
    responses=responses,
)
async def test_pass(
    vk_user_id: Annotated[int, Depends(vk_sign_check)],
    result: Annotated[dict[str, PlanetModelCheckOut], Depends(codes_check)],
) -> Any:
    """# Check the codes entered by the user #
    Created to check the codes for each of the planets for compliance with the desired values.
    """

    if not await users_queries.update_attempts_count(vk_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    fail_flag = False
    for key in result.keys():
        if not result[key].code_is_valid:
            fail_flag = True
            break

    if fail_flag:
        return result

    if not await users_queries.set_test_passed(vk_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result
