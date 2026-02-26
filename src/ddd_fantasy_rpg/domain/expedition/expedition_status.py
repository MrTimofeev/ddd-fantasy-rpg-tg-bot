from enum import Enum


class ExpeditionStatus(Enum):
    NO_ACTIVE = "no_active" # Момент когда человек еще не вышел в экспедицию
    ACTIVE = "active" # Момент когда генерируются события
    COMPLETED = "completed" # момент когда экспедиция закончилась по времени и пора запускать событие
    PVP = "pvp" # запущенное событие pvp
    PVE = 'pve' # запущенное событие pve
    TRADER = "trader" # запущено событие торговец
    RESOURCE = "recource" # запущено событие добычи ресурсов
