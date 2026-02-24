import asyncio
from typing import List, Tuple
from collections import defaultdict

from ddd_fantasy_rpg.domain.expedition import Expedition
from ddd_fantasy_rpg.domain.player import Player
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase


class PvpMatchResult:
    """Результат матчинга PVP-дуэли."""

    def __init__(
        self,
        player1_id: str,
        player2_id: str,
        player1_name: str,
        player2_name: str,
    ):
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.player1_name = player1_name
        self.player2_name = player2_name


class MatchPvpExpeditionsUseCase:
    """
    Use Case для матчинга PVP-дуэлей между игроками в активных экспедициях.
    """

    def __init__(self, start_battle_use_case: StartBattleUseCase):
        self._start_battle_uc = start_battle_use_case

    async def execute(self, uow: UnitOfWork) -> List[PvpMatchResult]:
        """
        Выполняет матчинг PVP-дуэлей и возвращает результат.
        Все изменения (прерывания экспедиций, запуск боев) сохраняются здесь.
        """
        # 1. Получаем все активные экспедиции
        active_expeditions = await uow.expeditions.get_all_active_expeditions()
        if len(active_expeditions) < 2:
            return []

        # 2. Загружаем игроков
        player_ids = [exp.player_id for exp in active_expeditions]
        players = await self._load_players(player_ids, uow)

        # 3. Фильтруем валидные пары (экспедиция + игрок)
        valid_pairs: List[Tuple[Expedition, Player]] = []
        for exp in active_expeditions:
            if exp.player_id in players:
                valid_pairs.append((exp, players[exp.player_id]))

        if len(valid_pairs) < 2:
            return []

        # 4. Группируем по дистанции
        by_distance = defaultdict(list)
        for exp, player in valid_pairs:
            by_distance[exp.distance].append((exp, player))

        # 5. Матчим пары
        matched_results: List[PvpMatchResult] = []
        matched_player_ids = set()

        for distance, pairs in by_distance.items():
            # Сортируем по уровню

            pairs.sort(key=lambda x: x[1].level)

            i = 0
            while i < len(pairs) - 1:
                exp1, p1 = pairs[i]
                exp2, p2 = pairs[i+1]

                # Пропускаем если кто-то уже в паре
                if p1.id in matched_player_ids or p2.id in matched_player_ids:
                    i += 1
                    continue

                # Проверяем баланс (разница <= 2 уровня)

                if abs(p1.level - p2.level) <= 2:
                    try:
                        # Проверяем вылазки
                        exp1.interrupt_for_duel(p2.id)
                        exp2.interrupt_for_duel(p1.id)

                        # сохраняем экспедиции
                        await uow.expeditions.save(exp1)
                        await uow.expeditions.save(exp2)

                        # TODO: убрать это и сделать запуск боя по окончании экспедиции у ближайшего конца экспедиции у игроков
                        # запускаем бой
                        await self._start_battle_uc.start_pvp_battle(p1.id, p2.id, uow)

                        # Сохряняем результат
                        matched_results.append(
                            PvpMatchResult(p1.id, p2.id, p1.name, p2.name)
                        )
                        matched_player_ids.update([p1.id, p2.id])

                        i += 2

                    except Exception:
                        # TODO: добавить логировае ошибок
                        i += 1
                else:
                    i += 1

        return matched_results

    async def _load_players(self, player_ids: List[str], uow: UnitOfWork) -> dict[str, Player]:
        """Загружает игроков и фильтрует успешные загрузки."""
        player_tasks = [uow.players.get_by_id(pid) for pid in player_ids]
        players_raw = await asyncio.gather(*player_tasks, return_exceptions=True)

        playsers = {}
        for pid, p in zip(player_ids, players_raw):
            if not isinstance(p, Expedition) and p is not None:
                playsers[pid] = p

        return playsers
