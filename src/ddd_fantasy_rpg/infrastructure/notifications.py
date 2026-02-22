from aiogram import Bot
from typing import List

from ddd_fantasy_rpg.application.use_cases.perform_battle_action import BattleActionResult
from ddd_fantasy_rpg.domain.notifications import NotificationService
from ddd_fantasy_rpg.application.use_cases.match_pvp_expeditions import PvpMatchResult
from ddd_fantasy_rpg.bot.aiogram_bot.keyboards import get_battle_keyboard



class TelegramNotificationService(NotificationService):
    """Реализация уведомлений для Telegram."""
    
    def __init__(self, bot: Bot):
        self._bot = bot
        
    
    async def notify_expedition_complete(
        self,
        player_id: str,
        monster_name: str,
        monster_level: int
    ) -> None:
        msg = (
            f"🗺️ Твоя вылазка завершена!\n"
            f"👹 Ты встретил {monster_name} (ур. {monster_level})!\n"
            f"⚔️ Бой начинается!"
        )
        
        try:
            await self._bot.send_message(
                chat_id=int(player_id),
                text=msg,
                reply_markup=get_battle_keyboard(player_id)
            )
        except Exception as e:
            print(f"Ошибка отправки уведомлений игроку {player_id}: {e}")
            
    async def notify_pvp_match_found(
        self,
        matches: List[PvpMatchResult]
    ) -> None:
        for match in matches:
            try:
                msg1 = (
                    f"⚔️ Во время вылазки ты встретил игрока {match.player2_name}!\n"
                    f"Бой начинается!"
                )
                msg2 = (
                    f"⚔️ Во время вылазки ты встретил игрока {match.player1_name}!\n"
                    f"Бой начинается!"
                )
                await self._bot.send_message(chat_id=int(match.player1_id), text=msg1)
                await self._bot.send_message(chat_id=int(match.player2_id), text=msg2)
                print(f"Уведомлеия отправлены: {match.player1_id} VS {match.player2_id}")
            except Exception as e:
                print(f"Ошибка оправки PvP уведомлений: {e}")
    
    async def notify_battle_turn(
        self,
        player_id: str,
        battle_state: str
    ) -> None:
        try:
            await self._bot.send_message(
                chat_id=int(player_id),
                text=battle_state,
                reply_markup=get_battle_keyboard(player_id)
            )
        except Exception as e:
            print(f"Ошибка отправки уведомлений о ходе: {e}")
            
    async def notify_battle_action_result(
        self,
        player_id: str,
        result: BattleActionResult,
        is_current_player: bool = True
    ) -> None:
        """Уведомляет игрока о результате действия в бою."""
        try:
            if is_current_player:
                # Для текущего игрока - обновляем интерфейс
                await self._bot.send_message(
                    chat_id=int(player_id),
                    text=result.message,
                    reply_markup=get_battle_keyboard(player_id)
                )
            else:
                # Для противника в PvP - уведомление о ходе
                opponent_msg = (
                    f"⚔️ Твой противник сделал ход!\n"
                    f"❤️ Твоё HP: {self._extract_player_hp(result.message)}\n"
                    f"Твоя очередь атаковать!"
                )
                await self._bot.send_message(
                    chat_id=int(player_id),
                    text=opponent_msg,
                    reply_markup=get_battle_keyboard(player_id)
                )
        except Exception as e:
            print(f"Ошибка отправки уведомления игроку {player_id}: {e}")
            
    async def notify_battle_finished(
        self,
        winner_id: str,
        loser_id: str,
        battle_outcome: dict
    ) -> None:
        """Уведомляет игроков о завершении боя."""
        try:
            # Уведомление победителю
            if battle_outcome.get("winner") == "player":
                await self._bot.send_message(winner_id,  "🏆 Победа! Добыча получена.")
            
            # Уведомление проигравшему
            if battle_outcome.get("player_died"):
                await self._bot.send_message(loser_id, "💀 Ты пал в бою... Весь инвентарь потерян!")
            elif battle_outcome.get("winner") == "monster":
                await self._bot.send_message(loser_id, "💀 Ты пал в бою...")
        except Exception as e:
            print(f"Ошибка отправки финальных уведомлений: {e}")
                
    def _extract_player_hp(self, message: str) -> str:
        """Извлекает HP игрока из сообщения."""
        try:
            # Ищем строку с HP игрока
            lines = message.split('\n')
            for line in lines:
                if 'Твое HP:' in line:
                    return line.split('Твое HP: ')[1].split()[0]
            return "0"
        except:
            return "0"