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
            )
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
            )
        )

        return result.scalar_one_or_none()

    async def update_image(
            self,
            session,
            product_id: int,
            image_id: str,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return None

        product.image_id = image_id

        await session.commit()

        return product

    async def get_all(
            self,
            session,
    ):
        result = await session.execute(
            select(Product)
            .order_by(Product.id)
        )

        return result.scalars().all()

    async def update_stock(
            self,
            session,
            product_id: int,
            stock: int,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return None

        product.stock = stock

        await session.commit()

        return product

    async def update_price(
            self,
            session,
            product_id: int,
            price,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return None

        product.price = price

        await session.commit()

        return product

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

    async def update_name(
            self,
            session,
            product_id: int,
            name: str,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return None

        product.name = name

        await session.commit()

        return product

    async def update_description(
            self,
            session,
            product_id: int,
            description: str,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return None

        product.description = description

        await session.commit()

        return product

    async def update_category(
            self,
            session,
            product_id: int,
            category_id: int,
    ):
        product = await self.get_by_id(
            session=session,
            product_id=product_id,
        )

        if not product:
            return None

        product.category_id = category_id

        await session.commit()

        return product

    async def search_by_name(
            self,
            session,
            name: str,
    ):
        result = await session.execute(
            select(Product).where(
                func.lower(Product.name).contains(
                    name.lower()
                )
            )
        )

        return list(result.scalars().all())

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
