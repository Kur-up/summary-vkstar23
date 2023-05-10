import os

from typing import Annotated
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import HTTPException
from fastapi import status

from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse

from ...db import users_queries

from .dependencies import vk_sign_check
from .dependencies import generate_ticket

from ..models.users import UserModel

router = APIRouter()


responses = {
    200: {
        "description": "Success response",
        "content": {
            "application/json": {
                "example": {
                    "user_id": 1234567,
                    "onboarding": False,
                    "is_test_passed": False,
                    "attempts": 0,
                    "first_name": "Lev",
                    "last_name": "Kurapov",
                }
            }
        },
    }
}


@router.get(
    "/getinfo",
    name="Get all user information",
    tags=["Users"],
    response_model=UserModel,
    responses=responses,
)
async def users_get(vk_user_id: Annotated[int, Depends(vk_sign_check)]):
    """# Get all user information #
    Created to get information about the playing user, to display correct data and send data to the database.
    """

    db_user = await users_queries.get_or_create_user(vk_user_id)
    user_model = UserModel.from_orm(db_user)
    return user_model


responses = {
    200: {
        "description": "Success response",
        "content": {"application/json": {"example": {".png file"}}},
    }
}


@router.get(
    "/getticket",
    name="Get user's ticket image",
    tags=["Users"],
    response_model=None,
    responses=responses,
)
async def users_getticket(
    vk_user_id: Annotated[int, Depends(vk_sign_check)],
    low_quality: Annotated[bool, Query(description="Get low quality image if true")],
) -> FileResponse | HTTPException:
    """# Get user's ticket image #
    Created to generate a user ticket with the date and time of receipt, to issue a prize for completing the game.
    """

    if not await users_queries.check_finished(vk_user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    file_path = f"media/tickets/{vk_user_id}.png"
    if low_quality:
        file_path = f"media/tickets/{vk_user_id}low.png"

    if os.path.isfile(file_path):
        return FileResponse(path=file_path)

    await generate_ticket(vk_user_id, low_quality)
    return FileResponse(path=file_path)


responses = {
    200: {
        "description": "Success response",
        "content": {"application/json": {"example": {"OK"}}},
    }
}


@router.post(
    "/passonboarding",
    name="Set onboarding status to true",
    tags=["Users"],
    responses=responses,
)
async def users_passonboarding(
    vk_user_id: Annotated[int, Depends(vk_sign_check)]
) -> dict:
    """# Set onboarding status to true #
    It was created to set the user's status about passing the training. Required for notations within the application.
    """

    if not await users_queries.set_onboarding_true(vk_user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content="OK")
