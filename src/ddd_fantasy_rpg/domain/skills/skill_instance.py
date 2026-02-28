from dataclasses import dataclass
from typing import Optional

from ddd_fantasy_rpg.domain.skills.skill_template import SkillTemplate

@dataclass 
class SKillInstance:
    """Экземпляр скилла, привязанный к игроку."""
    template_id: str
    owner_id: str
    current_cooldown: int = 0
    
    # Уникальные модификаторы (если нужно будет)
    
    level: int = 1
    
    @property
    def template(self) -> SkillTemplate:
        """Получает шаблон скилла."""
        from ddd_fantasy_rpg.infrastructure.repositories.skill_template_repository import SkillTemplateRepository
        return SkillTemplateRepository.get_template(self.template_id)
    
    @property
    def is_ready(self) -> bool:
        """Проверяет, готов ли скилл к использованию."""
        return self.current_cooldown == 0
    
    def start_cooldown(self):
        """Начинает отсчет кулдауна."""
        self.current_cooldown = self.template.cooldown_turns
        
    def reduce_cooldown(self):
        """Уменьшает кулдаунт на 1."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1
    
