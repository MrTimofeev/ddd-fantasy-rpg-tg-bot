from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_battle_keyboard(player_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⚔️ Атаковать",
                                 callback_data=f"battle_attack_{player_id}"),
            InlineKeyboardButton(
                text="🏃 Побег", callback_data=f"battle_flee_{player_id}"),
        ],
        [
            InlineKeyboardButton(text="🧪 Использовать предмет",
                                 callback_data=f"battle_use_item_{player_id}"),
            InlineKeyboardButton(
                text="🌀 Скиллы", callback_data=f"battle_use_skill_{player_id}"),
        ]
    ])
