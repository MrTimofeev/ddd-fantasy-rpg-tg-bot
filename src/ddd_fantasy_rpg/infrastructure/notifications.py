from aiogram import Bot

from ddd_fantasy_rpg.application.use_cases.perform_battle_action import BattleTurnResult
from ddd_fantasy_rpg.domain.common.notifications import NotificationService
from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult, PlayerVictory, PvpVictory, MonsterVictory
from ddd_fantasy_rpg.domain.player import Player
from ddd_fantasy_rpg.application.formatters.battle_formatter import BattleMessageFormatter
from ddd_fantasy_rpg.bot.aiogram_bot.keyboards import get_battle_keyboard



class TelegramNotificationService(NotificationService):
    """Реализация уведомлений для Telegram."""
    
    def __init__(self, bot: Bot, message_formatter: BattleMessageFormatter):
        self._bot = bot
        self._forrmater = message_formatter
        
    
    async def notify_expedition_complete(
        self,
        player_id: str,
        player_hp: int,
        monster_name: str,
        monster_level: int,
        monster_hp: int
    ) -> None:
        msg = (
            f"🗺️ Твоя вылазка завершена!\n"
            f"👹 Ты встретил {monster_name} (ур. {monster_level})!\n"
            f"❤️ Твоё HP {player_hp} 👹 HP {monster_hp}\n"
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
        player1: Player,
        player2: Player,
    ) -> None:
        try:
            msg1 = (
                f"⚔️ Во время вылазки ты встретил игрока {player2.name}!\n"
                f"Бой начинается!"
            )
            msg2 = (
                f"⚔️ Во время вылазки ты встретил игрока {player1.name}!\n"
                f"Бой начинается!"
            )
            await self._bot.send_message(chat_id=int(player1.id), text=msg1)
            await self._bot.send_message(chat_id=int(player2.id), text=msg2)
            print(f"Уведомлеия отправлены: {player1.id} VS {player2.id}")
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
        result: BattleTurnResult,
        is_current_player: bool = True,
    ) -> None:
        """Уведомляет игрока о результате действия в бою."""
        try:
            # Форматируем сообщение
            message_text = self._forrmater.format_turn(result)
            
            if is_current_player:
                # Для PVE - говорим что сделал монстр
                if not result.is_opponent_player:
                    opponent_msg = (
                        f"⚔️Монстр сделал ход!\n"
                        f"💥 Тебе нанесено {result.action_result.damage} урона!\n"
                        f"❤️ Твоё HP: {result.player_hp}\n"
                        f"Твоя очередь атаковать!"
                    )
                    
                    await self._bot.send_message(
                        chat_id=int(player_id),
                        text=opponent_msg,
                    )
                    
                
                # Для текущего игрока - обновляем интерфейс
                await self._bot.send_message(
                    chat_id=int(player_id),
                    text=message_text,
                    reply_markup=get_battle_keyboard(player_id)
                )
                
                
            else:
                # Для противника в PVP - уведомление о ход
                opponent_msg = (
                    f"⚔️ Твой противник сделал ход!\n"
                    f"❤️ Твоё HP: {result.player_hp}\n"
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
        battle_result: BattleResult,
    ) -> None:
        """Уведомляет игроков о завершении боя."""
        
        if isinstance(battle_result.outcome,  PlayerVictory):
            await self._bot.send_message(
                battle_result.outcome.winner.id,
                "🏆 Победа! Добыча получена."
            )
            
            if battle_result.outcome.loot:
                # TODO: отправить информацию о луте
                pass
        
        elif isinstance(battle_result.outcome, MonsterVictory):
            await self._bot.send_message(
                battle_result.outcome.loser.id,
                "💀 Ты пал в бою... Весь инвентарь потерян!"
            )
            
        elif isinstance(battle_result.outcome, PvpVictory):
            await self._bot.send_message(
                battle_result.outcome.winner.id,
                "🏆 Победа в дуэли! Добыча получена."
            )
            
            await self._bot.send_message(
                battle_result.outcome.loser.id,
                "💀 Ты проиграл дуэль... Весь инвентарь потерян!"
            )
        
                
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