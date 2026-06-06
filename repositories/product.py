from sqlalchemy import select, func

from models.product import Product


class ProductRepository:

    async def get_by_category(
            self,
            session,
            category_id: int,
    ):
        result = await session.execute(
            select(Product).where(
                Product.category_id == category_id,
                Product.stock > 0,
            ).order_by(Product.name)
        )

        return list(result.scalars().all())

    async def get_by_id(
            self,
            session,
            product_id: int,
    ):
        result = await session.execute(
            select(Product).where(
                Product.id == product_id
            ).order_by(Product.name)
        )

        return result.scalar_one_or_none()

    async def get_all(
            self,
            session,
    ):
        result = await session.execute(
            select(Product)
            .order_by(Product.name)
        )

        return result.scalars().all()

    async def create(
            self,
            session,
            name: str,
            description: str,
            price,
            stock: int,
            category_id: int,
    ):
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )

        session.add(product)

        await session.commit()
        await session.refresh(product)

        return product

    async def delete(
            self,
            session,
            product_id: int,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return False

        await session.delete(product)
        await session.commit()

        return True

    async def update_fields(
            self,
            session,
            product_id: int,
            **fields,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return None

        for key, value in fields.items():
            setattr(product, key, value)

        await session.commit()

        return product

    async def get_page(
            self,
            session,
            offset: int,
            limit: int = 5,
    ):
        result = await session.execute(
            select(Product)
            .offset(offset)
            .limit(limit)
            .order_by(Product.id)
        )

        return list(result.scalars().all())

    async def count(
            self,
            session,
    ):
        result = await session.execute(
            select(func.count(Product.id))
        )

        return result.scalar()
