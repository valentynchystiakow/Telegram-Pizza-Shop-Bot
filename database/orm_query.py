# import asyncsession for making requests to database
from sqlalchemy.ext.asyncio import AsyncSession
# import Database Product model
from database.models import Product, Banner, Category, User, Cart
# import libraries
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload


# function that ads product to database
async def orm_add_product(session: AsyncSession, data: dict):
    # database object
    obj = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data['image'],
        category_id=int(data['category'])
    )
    # add - method which adds object to database
    session.add(obj)
    # commiting data into database
    await session.commit()


# function that shows all products in database
async def orm_get_products(session: AsyncSession, category_id):
    # saving all Product database models in variable
    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    # return all products
    return result.scalars().all()


# function that shows product by id
async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    # return product by id
    return result.scalar()


# function that updates products
async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = update(Product).where(Product.id == product_id).values(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data['category'])
    )
    await session.execute(query)
    # commiting changes in database
    await session.commit()


# function that deletes product
async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


##################### Adding User to Database #####################################
# function wich ads user to database
async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    # checking if User is already in database
    if result.first() is None:
        session.add(
            User(user_id=user_id, first_name=first_name,
                 last_name=last_name, phone=phone)
        )
        await session.commit()


############# Banners(info pages)#############


# function which ads banner description
async def orm_add_banner_description(session: AsyncSession, data: dict):
    # Menu: main, about, cart, shipping, payment, catalog
    query = select(Banner)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Banner(name=name, description=description)
                    for name, description in data.items()])
    await session.commit()


# function that changes banner image
async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
    query = update(Banner).where(Banner.name == name).values(image=image)
    await session.execute(query)
    await session.commit()


# function that get's banner's name
async def orm_get_banner(session: AsyncSession, page: str):
    query = select(Banner).where(Banner.name == page)
    result = await session.execute(query)
    return result.scalar()


# function wich gets info from pages
async def orm_get_info_pages(session: AsyncSession):
    query = select(Banner)
    result = await session.execute(query)
    return result.scalars().all()


######## Categories #########


# function that gets categories
async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()


# function that creates categories
async def orm_create_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories])
    await session.commit()


######################## Work with carts #######################################
# function wich ads product to cart
async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id,
                               Cart.product_id == product_id).options(joinedload(Cart.product))
    cart = await session.execute(query)
    cart = cart.scalar()
    # checks if cart is empty
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1))
        await session.commit()


# function wich gets products in user carts
async def orm_get_user_carts(session: AsyncSession, user_id):
    query = select(Cart).filter(Cart.user_id == user_id).options(
        joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


# function which deletes products from cart
async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    query = delete(Cart).where(Cart.user_id == user_id,
                               Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


# function which reduces one product from cart
async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id,
                               Cart.product_id == product_id).options(joinedload(Cart.product))
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id)
        await session.commit()
        return False
