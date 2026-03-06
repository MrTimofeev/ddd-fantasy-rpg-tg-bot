from dataclasses import dataclass
from typing import Dict, List, Optional

from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass


@dataclass
class PlayerCreated(DomainEvent):
    player_id: str
    player_race: Race
    player_class: PlayerClass

@dataclass
class PlayerLevelUp(DomainEvent):
    """Событие получение уровня"""
    player_id: str
    new_level: int
    gained_stats: Dict[str, int]


@dataclass
class PlayerDied(DomainEvent):
    """Базовое событие смерти (для общих уведомлений)"""
    player_id: str

@dataclass
class PlayerDefetedByPlayer(DomainEvent):
    """Специфичное событие для PVP: содержит данные о потере золотоа и передаче лута"""
    victim_id: str
    victor_id: str
    lost_gold: int
    transferred_item_ids: list[str]
    
@dataclass
class PlayerDefetedByMonster(DomainEvent):
    """Специфичное событие для PVE: игрок потеля лут, золото сохранено"""
    player_id: str
    lost_item_ids: List[str]
    
@dataclass
class PlayerRevived(DomainEvent):
    """Событие воскрешения игрока"""
    player_id: str

@dataclass
class PlayerReceivedLoot(DomainEvent):
    player_id: str
    items: list[ItemInstance]


@dataclass
class PlayerGainedExperience(DomainEvent):
    """Событие получение опыта"""
    player_id: str
    exp_gained: int


@dataclass
class SkillChanged(DomainEvent):
    """Событие смены навыка"""
    player_id: str
    slot_index: int
    new_skill_id: Optional[str]
    old_skill_id: Optional[str]
    

@dataclass
class ItemDepositedToGuild(DomainEvent):
    """Предмет помещен в гильдейский сундук"""
    player_id: str
    item_id: str
    item_name:str
    
@dataclass
class ItemWithdrawnFromGuild(DomainEvent):
    """Предмет извлечен из гильдейского сундука"""
    player_id: str
    item_id: str
    item_name: str
    
@dataclass
class GuildStorageUpgraded(DomainEvent):
    """Вместимость сундука увеличена"""
    player_id: str
    new_capacity: int
    cost_paid: int