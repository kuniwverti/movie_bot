import os
import json
import random

from aiogram import Router
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    FSInputFile
)
from aiogram.filters import CommandStart

from data.movies import movies
from data.series import series

router = Router()

FAVORITES_FILE = "storage/favorites.json"


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎬 Фильмы")],
        [KeyboardButton(text="📺 Сериалы")],
        [KeyboardButton(text="🎲 Случайный фильм")],
        [KeyboardButton(text="🎲 Случайный сериал")],
        [KeyboardButton(text="🎯 Случайный контент")],
        [KeyboardButton(text="⭐ Избранное")]
    ],
    resize_keyboard=True
)


def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        return {}

    with open(FAVORITES_FILE, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def save_favorites(data):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def add_to_favorites(user_id, item_type, key):
    data = load_favorites()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = []

    entry = {"type": item_type, "key": key}

    if entry not in data[user_id]:
        data[user_id].append(entry)

    save_favorites(data)


def get_user_favorites(user_id):
    data = load_favorites()
    return data.get(str(user_id), [])


def build_item_keyboard(item_type, key, back_callback):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ В избранное", callback_data=f"fav_{item_type}_{key}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_callback)],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )


def movies_list_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Интерстеллар", callback_data="movie_интерстеллар")],
            [InlineKeyboardButton(text="Джон Уик", callback_data="movie_джон уик")],
            [InlineKeyboardButton(text="Аватар", callback_data="movie_аватар")],
            [InlineKeyboardButton(text="Начало", callback_data="movie_начало")],
            [InlineKeyboardButton(text="Матрица", callback_data="movie_матрица")],
            [InlineKeyboardButton(text="🎲 Случайный фильм", callback_data="random_movie")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )


def series_list_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Во все тяжкие", callback_data="series_во все тяжкие")],
            [InlineKeyboardButton(text="Викинги", callback_data="series_викинги")],
            [InlineKeyboardButton(text="Игра престолов", callback_data="series_игра престолов")],
            [InlineKeyboardButton(text="Острые козырьки", callback_data="series_острые козырьки")],
            [InlineKeyboardButton(text="Шерлок", callback_data="series_шерлок")],
            [InlineKeyboardButton(text="🎲 Случайный сериал", callback_data="random_series")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )


def make_caption(item):
    return (
        f"Название: {item['title']}\n"
        f"Тип: {item['type']}\n"
        f"Год: {item['year']}\n"
        f"Жанр: {item['genre']}\n\n"
        f"Описание: {item['description']}"
    )


def search_keyboard(query: str):
    buttons = []

    for key, item in movies.items():
        if query in key:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🎬 {item['title']}",
                    callback_data=f"movie_{key}"
                )
            ])

    for key, item in series.items():
        if query in key:
            buttons.append([
                InlineKeyboardButton(
                    text=f"📺 {item['title']}",
                    callback_data=f"series_{key}"
                )
            ])

    buttons.append([
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="main_menu"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def favorites_keyboard(favorites):
    buttons = []

    for entry in favorites:
        if entry["type"] == "movie" and entry["key"] in movies:
            buttons.append([
                InlineKeyboardButton(
                    text=f"🎬 {movies[entry['key']]['title']}",
                    callback_data=f"movie_{entry['key']}"
                )
            ])
        elif entry["type"] == "series" and entry["key"] in series:
            buttons.append([
                InlineKeyboardButton(
                    text=f"📺 {series[entry['key']]['title']}",
                    callback_data=f"series_{entry['key']}"
                )
            ])

    buttons.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def send_item_message(message_obj, item, item_type, key, back_callback):
    caption = make_caption(item)
    poster_path = item.get("poster")
    reply_markup = build_item_keyboard(item_type, key, back_callback)

    if poster_path and os.path.exists(poster_path):
        photo = FSInputFile(poster_path)
        await message_obj.answer_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup
        )
    else:
        await message_obj.answer(
            caption,
            reply_markup=reply_markup
        )


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет 👋\n\n"
        "Выбери раздел кнопками ниже\n"
        "или напиши часть названия фильма / сериала.",
        reply_markup=main_menu
    )


@router.message()
async def text_handler(message: Message):
    text = message.text.lower().strip()

    if text in ["фильмы", "🎬 фильмы"]:
        await message.answer(
            "🎬 Выбери фильм:",
            reply_markup=movies_list_keyboard()
        )
        return

    if text in ["сериалы", "📺 сериалы"]:
        await message.answer(
            "📺 Выбери сериал:",
            reply_markup=series_list_keyboard()
        )
        return

    if text in ["⭐ избранное", "избранное"]:
        favorites = get_user_favorites(message.from_user.id)

        if not favorites:
            await message.answer("У тебя пока нет избранного.", reply_markup=main_menu)
            return

        await message.answer(
            "⭐ Твоё избранное:",
            reply_markup=favorites_keyboard(favorites)
        )
        return

    if text in ["🎲 случайный фильм", "случайный фильм"]:
        key = random.choice(list(movies.keys()))
        item = movies[key]
        await send_item_message(message, item, "movie", key, "back_movies")
        return

    if text in ["🎲 случайный сериал", "случайный сериал"]:
        key = random.choice(list(series.keys()))
        item = series[key]
        await send_item_message(message, item, "series", key, "back_series")
        return

    if text in ["🎯 случайный контент", "случайный контент"]:
        content_type = random.choice(["movie", "series"])

        if content_type == "movie":
            key = random.choice(list(movies.keys()))
            item = movies[key]
            await send_item_message(message, item, "movie", key, "back_movies")
        else:
            key = random.choice(list(series.keys()))
            item = series[key]
            await send_item_message(message, item, "series", key, "back_series")
        return

    if text in movies:
        item = movies[text]
        await send_item_message(message, item, "movie", text, "back_movies")
        return

    if text in series:
        item = series[text]
        await send_item_message(message, item, "series", text, "back_series")
        return

    movie_matches = [key for key in movies if text in key]
    series_matches = [key for key in series if text in key]

    if movie_matches or series_matches:
        await message.answer(
            "Я нашёл варианты. Выбери:",
            reply_markup=search_keyboard(text)
        )
        return

    await message.answer(
        "Ничего не найдено.\n"
        "Выбери раздел или напиши часть названия.",
        reply_markup=main_menu
    )


@router.callback_query(lambda c: c.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    await callback.message.answer(
        "🏠 Главное меню\n\nВыбери раздел:",
        reply_markup=main_menu
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_movies")
async def back_movies_handler(callback: CallbackQuery):
    await callback.message.answer(
        "🎬 Выбери фильм:",
        reply_markup=movies_list_keyboard()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_series")
async def back_series_handler(callback: CallbackQuery):
    await callback.message.answer(
        "📺 Выбери сериал:",
        reply_markup=series_list_keyboard()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "random_movie")
async def random_movie_handler(callback: CallbackQuery):
    key = random.choice(list(movies.keys()))
    item = movies[key]
    await send_item_message(callback.message, item, "movie", key, "back_movies")
    await callback.answer()


@router.callback_query(lambda c: c.data == "random_series")
async def random_series_handler(callback: CallbackQuery):
    key = random.choice(list(series.keys()))
    item = series[key]
    await send_item_message(callback.message, item, "series", key, "back_series")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("movie_"))
async def movie_handler(callback: CallbackQuery):
    key = callback.data.replace("movie_", "", 1)
    item = movies[key]
    await send_item_message(callback.message, item, "movie", key, "back_movies")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("series_"))
async def series_handler(callback: CallbackQuery):
    key = callback.data.replace("series_", "", 1)
    item = series[key]
    await send_item_message(callback.message, item, "series", key, "back_series")
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("fav_"))
async def favorite_handler(callback: CallbackQuery):
    _, item_type, key = callback.data.split("_", 2)

    add_to_favorites(callback.from_user.id, item_type, key)

    await callback.answer("Добавлено в избранное ⭐", show_alert=True)










 

    

