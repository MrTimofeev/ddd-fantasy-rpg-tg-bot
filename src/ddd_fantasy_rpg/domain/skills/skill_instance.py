from dataclasses import dataclass
from typing import Optional

from ddd_fantasy_rpg.domain.skills.skill_template import SkillTemplate

@dataclass 
class SkillInstance:
    """Экземпляр скилла, привязанный к игроку."""
    id: str
    template_id: str
    owner_id: str
    current_cooldown: int = 0
    
    # Уникальные модификаторы (если нужно будет)
    
    level: int = 1
    
    @property
    def is_ready(self) -> bool:
        """Проверяет, готов ли скилл к использованию."""
        return self.current_cooldown == 0
    
    def start_cooldown(self, turns: int) -> None:
        """Начинает отсчет кулдауна."""
        self.current_cooldown = turns
        
    def reduce_cooldown(self):
        """Уменьшает кулдаунт на 1."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
