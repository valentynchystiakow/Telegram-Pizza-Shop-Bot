# import libraries
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InputMediaPhoto
# import orm functions
from database.orm_query import orm_get_banner, orm_get_categories, orm_get_products, orm_delete_from_cart, orm_reduce_product_in_cart, orm_get_user_carts, orm_add_to_cart
# import function that generate keyboard for user
from keyboards.inline import get_user_main_btns, get_user_catalog_btns, get_products_btns, get_user_cart
# import pages Paginator class
from utils.paginator import Paginator


# function that generates main menu keyboards depending on menu level
async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds


# function that generates catalog menu
async def catalog(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    categories = await orm_get_categories(session)
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds


# pages Paginator
def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Previous."] = "previous"

    if paginator.has_next():
        btns["Next. ▶"] = "next"

    return btns


# function that generates products menu(with pagination)
async def products(session, level, category, page):
    products = await orm_get_products(session, category_id=category)

    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}\
                </strong>\n{product.description}\n Price: {round(product.price, 2)} USD.\n\
                <strong>Product {paginator.page} of {paginator.pages}</strong>",
    )
    # setting pagination buttons
    pagination_btns = pages(paginator)
    # setting keyboard
    kbds = get_products_btns(
        level=level,
        category=category,
        page=page,
        pagination_btns=pagination_btns,
        product_id=product.id,
    )

    return image, kbds


# function that generates cart menu(3-level)
async def carts(session, level, menu_name, page, user_id, product_id):
    # depending on value menu_name call different orm_functions
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, product_id)

    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(
            media=banner.image, caption=f"<strong>{
                banner.description}</strong>"
        )
        # creating keyboards using get_user_cart functions
        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            product_id=None,
        )
    # if there is at least one cart create paginator
    else:
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.name}</strong>\n{cart.product.price}$ x {cart.quantity} = {cart_price}$\
                    \nProduct {paginator.page} of {paginator.pages} in cart.\nTotal product's price in cart - {total_price} USD",
        )
        # generatins pagination buttons
        pagination_btns = pages(paginator)
        # create cart menu buttons
        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds


# function that generates menu content
async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    # default value None
    category: int | None = None,
    page: int | None = None,
    user_id: int | None = None,
    product_id: int | None = None
):
    # if menu level = 0
    if level == 0:
        return await main_menu(session, level, menu_name)
    # if menu level = 2
    elif level == 1:
        return await catalog(session, level, menu_name)
    # if menu level = 2
    elif level == 2:
        return await products(session, level, category, page)
    # if menu level -3
    elif level == 3:
        return await carts(session, level, menu_name, page, user_id, product_id)
