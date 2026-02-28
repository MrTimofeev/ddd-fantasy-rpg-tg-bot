from dataclasses import dataclass



    
@dataclass(frozen=True)
class Skill:
    name: str
    skill_type: SkillType
    base_power: int # например, множитель на базовое значение
    cooldown_turns: int
    
    def __post_init__(self):
        if self.cooldown_turns < 0:
            raise ValueError("Colldown must be >= 0")
        if self.base_power <=0:
            raise ValueError("Base power must be > 0")

    