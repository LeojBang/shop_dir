from repositories.user import UserRepository


class UserService:

    def __init__(self):
        self.repository = UserRepository()

    async def register_user(
        self,
        session,
        telegram_id: int,
        username: str | None,
    ):
        user = await self.repository.get_by_telegram_id(
            session=session,
            telegram_id=telegram_id,
        )

        if user:
            return user

        return await self.repository.create(
            session=session,
            telegram_id=telegram_id,
            username=username,
        )