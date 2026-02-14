from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_battle_keyboard(player_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚔️ Атаковать",
                                 callback_data=f"battle_{player_id}_attack"),
            InlineKeyboardButton(
                text="🏃 Побег", callback_data=f"battle_{player_id}_flee"),
        ],
        [
            InlineKeyboardButton(text="🧪 Использовать предмет",
                                 callback_data=f"battle_{player_id}_item"),
            InlineKeyboardButton(
                text="🌀 Скиллы", callback_data=f"battle_{player_id}_skills"),
        ]
    ])
