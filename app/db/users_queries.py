from sqlalchemy import select
from sqlalchemy import update

from .core import get_session
from .core import UserDB
from .dependencies import vk_get_names


async def get_or_create_user(vk_user_id: int) -> UserDB:
    async with await get_session() as session:
        result = await session.execute(
            select(UserDB).where(UserDB.user_id == vk_user_id)
        )
        db_user = result.scalar()

        if db_user:
            return db_user

        first_name, last_name = await vk_get_names(vk_user_id)
        new_user = UserDB(
            user_id=vk_user_id, first_name=first_name, last_name=last_name
        )
        session.add(new_user)
        await session.commit()
        return new_user


async def set_onboarding_true(vk_user_id: int) -> bool:
    async with await get_session() as session:
        query = select(UserDB).where(UserDB.user_id == vk_user_id)
        result = await session.execute(query)
        db_user = result.scalar()

        if db_user:
            update_stmt = (
                update(UserDB)
                .where(UserDB.user_id == vk_user_id)
                .values(onboarding=True)
            )
            await session.execute(update_stmt)
            await session.commit()
            return True

        return False


async def set_test_passed(vk_user_id: int) -> bool:
    async with await get_session() as session:
        query = select(UserDB).where(UserDB.user_id == vk_user_id)
        result = await session.execute(query)
        db_user = result.scalar()

        if db_user:
            update_stmt = (
                update(UserDB)
                .where(UserDB.user_id == vk_user_id)
                .values(is_test_passed=True)
            )
            await session.execute(update_stmt)
            await session.commit()
            return True

        return False


async def check_finished(vk_user_id: int) -> bool:
    async with await get_session() as session:
        query = select(UserDB).where(UserDB.user_id == vk_user_id)
        result = await session.execute(query)
        db_user = result.scalar()

        if db_user and db_user.is_test_passed:
            return True

        return False


async def update_attempts_count(vk_user_id: int) -> bool:
    async with await get_session() as session:
        query = select(UserDB).where(UserDB.user_id == vk_user_id)
        result = await session.execute(query)
        db_user = result.scalar()

        if db_user:
            count = db_user.attempts + 1
            update_stmt = (
                update(UserDB)
                .where(UserDB.user_id == vk_user_id)
                .values(attempts=count)
            )
            await session.execute(update_stmt)
            await session.commit()
            return True

        return False
