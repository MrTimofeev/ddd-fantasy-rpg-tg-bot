from enum import Enum

class SkillType(Enum):
    DAMAGE = "damage"
    HEAL = "HEAL"
    BUFF = "buff"
    DEBUFF = 'debuff'
    UTILITY = "utility"