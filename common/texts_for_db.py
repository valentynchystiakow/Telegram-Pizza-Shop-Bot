# import libraries
from aiogram.utils.formatting import Bold, as_list, as_marked_section

# categories
categories = ['Food', 'Drinks']

# description for different types of info pages
description_for_info_pages = {
    "main": "Welcome!",
    "about": "Pizza shop.\n We are working 24/7",
    "payment": as_marked_section(
        Bold("Payment methods:"),
        "By card in bot",
        "After receiving by card/cash",
        "In shop",
        marker="✅ ",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Shipping/ordering methods:"),
            "Courier",
            "Self pick-up",
            "Will eat in your shop",
            marker="✅ ",
        ),
        as_marked_section(Bold("Forbidden:"), "By mail",
                          "By pigeons", marker="❌ "),
        sep="\n----------------------\n",
    ).as_html(),
    'catalog': 'Categories:',
    'cart': 'There is nothing in card!'
}
