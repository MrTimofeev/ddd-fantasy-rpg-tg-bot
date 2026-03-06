from dataclasses import dataclass, field
from typing import List, Optional

from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.player.events import (
    ItemDepositedToGuild,
    ItemWithdrawnFromGuild,
    GuildStorageUpgraded
)

from ddd_fantasy_rpg.domain.player.exceptions import DomainError


@dataclass
class GuildStorage:
    """
    Агрегат Гильдейского Сундука.
    Хранит предметы, которые не теряются при сметри игрока.
    """
    owner_id: str
    items: List[ItemInstance] = field(default_factory=list)
    max_capacity: int = 20  # начальная вместимость
    _pendings_events: List[DomainEvent] = field(
        default_factory=list, repr=False)

    def deposit(self, item: ItemInstance) -> None:
        """
        Положиьт предмет в сундук.
        Инварианты:
        - Предмет не должен быть экипирован.
        - Вместимость не должна быть превышена.
        - Предмет должен принадлежать игроку
        """

        if len(self.items) >= self.max_capacity:
            raise DomainError(
                f"Сундук переполнен. Вместимость: {self.max_capacity}")

        if item.is_equipped:
            raise DomainError(
                f"Нельзя положить экипированный предмет в сундук. Сначала смените его.")

        if any(i.id == item.id for i in self.items):
            raise DomainError("Такой предмет уже находится в сундуке")

        self.items.append(item)

        self._pendings_events.append(ItemDepositedToGuild(
            player_id=self.owner_id,
            item_id=item.id,
            item_name=item.name
        ))

    def withdraw(self, item_id: str) -> ItemInstance:
        """
        Забрать предмет из сундука.
        Возвращать объект предмета.
        """

        item = next((i for i in self.items if i.id == item_id), None)
        if not item:
            raise DomainError("Предмет не найден в гильдейском сундуке")

        self.items.remove(item)

        self._pendings_events.append(ItemWithdrawnFromGuild(
            player_id=self.owner_id,
            item_id=item.id,
            item_name=item.name
        ))

        return item

    def upgrade_capacity(self, cost: int, current_player_gold: int) -> int:
        """
        Увеличить вместимосьт сундука за золото.
        Возвращаьт сумму, которую нужно списать у игрока.
        """

        if current_player_gold < cost:
            raise DomainError("Недостаточно золота для улучшения сундука")

        # TODO: Сделать сервис расчета цены
        old_capacity = self.max_capacity
        self.max_capacity += 5

        self._pendings_events.append(GuildStorageUpgraded(
            player_id=self.owner_id,
            new_capacity=self.max_capacity,
            cost_paid=cost,
        ))

        return cost

    def get_items(self) -> List[ItemInstance]:
        return list(self.items)

    def find_item_by_id(self, item_id: str) -> Optional[ItemInstance]:
        return next((i for i in self.items if i.id == item_id), None)

    def pop_pending_events(self) -> List[DomainEvent]:
        events = list(self._pendings_events)
        self._pendings_events.clear()
        return events

    def __repr__(self) -> str:
        return f"GuildStorage(owner={self.owner_id}, items_count={len(self.items)}, capacity={self.max_capacity})"
