# import function for creating inline buttons
from keyboards.inline import get_callback_btns
# import libraries
from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter, or_f
from sqlalchemy.ext.asyncio import AsyncSession
# import Router Filter
from filters.chat_types import ChatTypeFilter, IsAdmin
# import orms functions
from database.orm_query import orm_add_product, orm_delete_product, orm_get_products, orm_update_product, orm_get_categories, orm_get_info_pages, orm_change_banner_image
# import function for generating keyboard buttons
from keyboards.reply import get_keyboard
# import FSM components
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# setting Router
admin_router = Router()
# filtering router message with ChatType Filter(works only for admins)
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


# Creating admin buttons with function
ADMIN_KB = get_keyboard(
    "Add product",
    'All products',
    'Add/change banner',
    placeholder="Change action",
    sizes=(2,)
)


# Finite State Machine (FSM) for changing products by admins
class AddProduct(StatesGroup):
    # state steps
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()
    product_for_change = None
    # text for every state step
    texts = {
        'AddProduct:name': 'Enter name again',
        'AddProduct:description': 'Enter description again',
        'AddProduct:price': 'Enter price again',
        'AddProduct:image': 'Enter image again',
    }


# function that processes admin command
@admin_router.message(Command("admin"))
async def add_product(message: types.Message):
    await message.answer("What you want to do?", reply_markup=ADMIN_KB)


# function that processes All products command
@admin_router.message(F.text == 'All products')
async def admin_features(message: types.Message, session: AsyncSession):
    # shows buttons with categories to choose
    categories = await orm_get_categories(session)
    btns = {category.name: f'category_{
        category.id}' for category in categories}
    await message.answer("Choose category", reply_markup=get_callback_btns(btns=btns))


# function that shows all products from chosen category
@admin_router.callback_query(F.data.startswith('category_'))
async def starring_at_product(callback: types.CallbackQuery, session: AsyncSession):
    category_id = callback.data.split('_')[-1]
    for product in await orm_get_products(session, int(category_id)):
        await callback.message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}\
                    </strong>\n{product.description}\nPrice: {round(product.price, 2)} USD.",
            reply_markup=get_callback_btns(
                # inline buttons wich change product
                btns={
                    "Delete": f"delete_{product.id}",
                    "Change": f"change_{product.id}",
                },
                sizes=(2,)
            ),
        )
    await callback.answer()
    await callback.message.answer("Ok,here is list of products ⏫")


# function that processes inline button delete product
@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    # saving product id into variable
    product_id = callback.data.split("_")[-1]
    # calling function that makes request in async session which deletes product by id
    await orm_delete_product(session, int(product_id))
    # show message to user that product was deleted
    await callback.answer("The product was deleted")
    await callback.message.answer("The product was deleted")


# MICRO FSM for changing state of banners
class AddBanner(StatesGroup):
    image = State()


# function that processes adding/changing banner
@admin_router.message(StateFilter(None), F.text == 'Add/change banner')
async def add_image2(message: types.Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(f"Send banner's photo.\n Point for which page it must be:\
                         \n{', '.join(pages_names)}")
    await state.set_state(AddBanner.image)


# Add/changes name of tables for pages:
# main, catalog, cart(для пустой корзины), about, payment, shipping
@admin_router.message(AddBanner.image, F.photo)
async def add_banner(message: types.Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(f"Enter correct name for page, for example:\
                         \n{', '.join(pages_names)}")
        return
    await orm_change_banner_image(session, for_page, image_id,)
    await message.answer("Banner added/changed.")
    await state.clear()


# catches wrong data
@admin_router.message(AddBanner.image)
async def add_banner2(message: types.Message, state: FSMContext):
    await message.answer("Send photo of banner of decline")


# function that processes inline button change product(switches to this step of FSM)
@admin_router.callback_query(StateFilter(None), F.data.startswith('change_'))
async def delete_product_callback(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    # saving product id into variable
    product_id = callback.data.split("_")[-1]
    product_for_change = await orm_get_products(session, int(product_id))
    AddProduct.product_for_change = product_for_change
    await callback.answer()
    await callback.message.answer(
        "Enter product's name", reply_markup=types.ReplyKeyboardRemove()
    )
    # set new state with new product's name
    await state.set_state(AddProduct.name)


# function that processes Cancel command(message), * - means any user's state
@admin_router.message(StateFilter('*'), Command("Cancel"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "cancel")
async def cancel_handler(message: types.Message,  state: FSMContext) -> None:
    current_state = await state.get_state()
    # if current state is empty ends work of this hanlder
    if current_state is None:
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    # stops fms
    await state.clear()
    # sends message to user that actions was cancelled and returns default admin keyboard
    await message.answer("Actions are cancelled", reply_markup=ADMIN_KB)


# function that processes Back command(message),
@admin_router.message(StateFilter('*'), Command("Back"))
@admin_router.message(StateFilter('*'), F.text.casefold() == "back")
async def cancel_handler(message: types.Message,  state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        # if user is on first step he will get next message
        await message.answer("There is no previous step, enter good's name or write 'cancel'")
        return
    # previous step default - None
    previous = None
    # for every step states in AddProduct
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ok,you have returned to previous step. \n {AddProduct.texts[previous.state]}")
        previous = step


# function that processes action button(add product)
@admin_router.message(StateFilter(None), F.text == "Add product")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Enter product's name", reply_markup=types.ReplyKeyboardRemove()
    )
    # switching to next state step
    await state.set_state(AddProduct.name)


# function that adds products's name
@admin_router.message(AddProduct.name, or_f(F.text, F.text == '.'))
async def add_name(message: types.Message,  state: FSMContext):
    # if user entered .
    if message.text == '.':
        # update state of FSM in this way
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        # creates limitation to length of product's name
        if 4 >= len(message.text) >= 150:
            await message.answer('Products name cant be longer than 150 symbols \n or less than 4 symbols. \n Enter again')
            return
        # updates state
        await state.update_data(name=message.text)
    await message.answer("Enter product's description")
    # switches to next state step
    await state.set_state(AddProduct.description)


# function that checks if user entered correct product's name
@admin_router.message(AddProduct.name)
async def add_name(message: types.Message, state: FSMContext):
    # sends message warning to admin that he entered wrong name
    await message.answer("You have entered wrong data, please enter product's name again.")


# function that adds good's description
@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message,  state: FSMContext, session: AsyncSession):
    if message.text == '.' and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        # checkes if description is long enough
        if 4 >= len(message.text):
            await message.answer("Desription cant be shorter than 4 symbols.\n Enter again")
            return
        # updates state
        await state.update_data(description=message.text)

    # switches to choose category state
    categories = await orm_get_categories(session)
    # creates buttons with categories
    btns = {category.name: str(category.id) for category in categories}
    await message.answer('Choose category', reply_markup=get_callback_btns(btns=btns))
    # switches to next state step
    await state.set_state(AddProduct.category)


# function that processes if user entered correct description
@admin_router.message(AddProduct.description)
async def add_description2(message: types.Message, state: FSMContext):
    await message.answer('You entered wrong type of description, please try again')


# function(handler) wich catches callback of categories to choose
@admin_router.callback_query(AddProduct.category)
async def category_choice(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Now enter product's price")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Choose category from buttons below')
        await callback.answer()


# Catching any incorrect actions from user, except choosing category
@admin_router.message(AddProduct.category)
async def category_choice2(message: types.Message, state: FSMContext):
    await message.answer("'Choose category from buttons.'")


# function that adds good's price
@ admin_router.message(AddProduct.price, or_f(F.text, F.text == '.'))
async def add_price(message: types.Message,  state: FSMContext):
    if message.text == ".":
        await state.update_data(description=AddProduct.product_for_change.price)
    else:
        # updates state
        await state.update_data(price=message.text)
    await message.answer("Download product's image")
    # switches to next state step
    await state.set_state(AddProduct.image)


# function(hanlder) wich catches incorrect price data from user
@admin_router.message(AddProduct.price)
async def add_price2(message: types.Message, state: FSMContext):
    await message.answer('You entered wrong data,please enter price again')


# function that adds/changes good's image and tells admin that product was fully added
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)

    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer("Send product's image")
        return
    data = await state.get_data()
    # catches errors
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await message.answer("Product was added/changed", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(
            f"Error: \n{str(e)}\nSomething went wrong...",
            reply_markup=ADMIN_KB,
        )
        await state.clear()

    AddProduct.product_for_change = None


# Functin(handler) wich catches incorrect image data from user
@admin_router.message(AddProduct.image)
async def add_image2(message: types.Message, state: FSMContext):
    await message.answer("Send product's image")
