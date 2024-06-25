# import libraries
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


# generating class from main class CallbackData
class MenuCallBack(CallbackData, prefix='menu'):
    level: int
    menu_name: str
    # default value None
    category: int | None = None
    # default page value =1
    page: int = 1
    # default value None
    product_id: int | None = None


# function that generates main buttons for user menu
def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Products 🍕": "catalog",
        "Cart 🛒": "cart",
        "About us ℹ️": "about",
        "Payment 💰": "payment",
        "Shipping ⛵": "shipping",
    }
    for text, menu_name in btns.items():
        if menu_name == 'catalog':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level+1, menu_name=menu_name).pack()))
        elif menu_name == 'cart':
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=3, menu_name=menu_name).pack()))
        else:
            keyboard.add(InlineKeyboardButton(text=text,
                                              callback_data=MenuCallBack(level=level, menu_name=menu_name).pack()))

    return keyboard.adjust(*sizes).as_markup()


# function that generates 1-level buttons(catalog menu)
def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(InlineKeyboardButton(text='Back',
                                      callback_data=MenuCallBack(level=level-1, menu_name='main').pack()))
    keyboard.add(InlineKeyboardButton(text='Cart 🛒',
                                      callback_data=MenuCallBack(level=3, menu_name='cart').pack()))

    for c in categories:
        keyboard.add(InlineKeyboardButton(text=c.name,
                                          callback_data=MenuCallBack(level=level+1, menu_name=c.name, category=c.id).pack()))

    return keyboard.adjust(*sizes).as_markup()


# function that generates 2-level buttons(product menu with categories)
def get_products_btns(*, level: int, category: int, page: int, pagination_btns: int, product_id: int, sizes: tuple[int] = (2, 1)):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Back',
                                      callback_data=MenuCallBack(level=level-1, menu_name='catalog').pack()))
    keyboard.add(InlineKeyboardButton(text='Cart 🛒',
                                      callback_data=MenuCallBack(level=3, menu_name='cart').pack()))
    keyboard.add(InlineKeyboardButton(text='Buy 💵',
                                      callback_data=MenuCallBack(level=level, menu_name='add_to_cart', product_id=product_id).pack()))

    keyboard.adjust(*sizes)

    keyboard.adjust(*sizes)
    # empty variable with pagination buttons
    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page + 1).pack()))

        elif menu_name == "previous":
            row.append(InlineKeyboardButton(text=text,
                                            callback_data=MenuCallBack(
                                                level=level,
                                                menu_name=menu_name,
                                                category=category,
                                                page=page - 1).pack()))

    return keyboard.row(*row).as_markup()


# function that generates callback inline buttons
def get_callback_btns(
    *,
    btns: dict[str, str],
    sizes: tuple[int] = (2,)


):
    # creating keyboard using class
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        # adding button to keyboard
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


# function that creates 3-level buttons (add_to_cart menu buttons)
def get_user_cart(
    *,
    level: int,
    page: int | None,
    pagination_btns: dict | None,
    product_id: int | None,
    sizes: tuple[int] = (3,)
):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(InlineKeyboardButton(text='Delete',
                                          callback_data=MenuCallBack(level=level, menu_name='delete', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='-1',
                                          callback_data=MenuCallBack(level=level, menu_name='decrement', product_id=product_id, page=page).pack()))
        keyboard.add(InlineKeyboardButton(text='+1',
                                          callback_data=MenuCallBack(level=level, menu_name='increment', product_id=product_id, page=page).pack()))

        keyboard.adjust(*sizes)

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(InlineKeyboardButton(text=text,
                                                callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page + 1).pack()))
            elif menu_name == "previous":
                row.append(InlineKeyboardButton(text=text,
                                                callback_data=MenuCallBack(level=level, menu_name=menu_name, page=page - 1).pack()))

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(text='Main🏠',
                                 callback_data=MenuCallBack(level=0, menu_name='main').pack()),
            InlineKeyboardButton(text='Order',
                                 callback_data=MenuCallBack(level=0, menu_name='order').pack()),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(text='Main 🏠',
                                 callback_data=MenuCallBack(level=0, menu_name='main').pack()))

        return keyboard.adjust(*sizes).as_markup()
