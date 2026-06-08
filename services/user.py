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
        return await self.repository.get_or_create(
            session=session,
            telegram_id=telegram_id,
            username=username,
        )
