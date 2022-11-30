from loguru import logger

from schedule_ogu import UserModel


async def create_super_user(user_id: int, remove: bool) -> bool:
    user = await UserModel.filter(id=user_id).first()
    if not user:
        logger.error("User is not registered in bot")
        raise ValueError("User is not registered in bot")

    logger.info(
        "Loaded user {user}. It's registered at {register_date}.",
        user=user.id,
        register_date=user.created_at,
    )
    user.is_superuser = not remove
    await user.save()
    if remove:
        logger.warning("User {user} now IS NOT superuser", user=user_id)
    else:
        logger.warning("User {user} now IS superuser", user=user_id)
    return True
