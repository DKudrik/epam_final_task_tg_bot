from telegram import InlineKeyboardButton

get_GIFS_keyboard = [
    [
        InlineKeyboardButton(
            "Получить GIF всех пользователей ", callback_data="all_gifs"
        ),
        InlineKeyboardButton("Получить свои GIF", callback_data="user_gifs"),
    ]
]

choose_GIF_type_keyboard = [
    [
        InlineKeyboardButton(
            "Создать приватный GIF ", callback_data="create_private_gif"
        )
    ],
    [InlineKeyboardButton("Создать общий GIF", callback_data="create_gif")],
]

select_font_and_size_keyboard = [
    [
        InlineKeyboardButton("Выбрать шрифт ", callback_data="show_fonts"),
        InlineKeyboardButton("Выбрать размер шрифта", callback_data="show_font_sizes"),
    ]
]

select_font_size_keyboard = [
    [InlineKeyboardButton("Выбрать размер шрифта ", callback_data="show_font_sizes")]
]

select_font_keyboard = [
    [InlineKeyboardButton("Выбрать шрифт ", callback_data="show_fonts")]
]
