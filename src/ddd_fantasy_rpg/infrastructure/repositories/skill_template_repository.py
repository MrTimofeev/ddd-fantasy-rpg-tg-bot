import yaml
from pathlib import Path
from typing import Dict, List

from ddd_fantasy_rpg.domain.skills.skill_template import SkillTemplate

# TODO: Сделать абстрактный класс и наследоваться от него
class SkillTemplateRepository:
    """Репозиторий шаблонов скиллов (загружается из конфигурации)."""
    
    _templates: Dict[str, SkillTemplate] = {}
    _initialized: bool = False
    
    @classmethod
    def initialized(cls, config_dir: Path):
        """Инициализирует репозиторий из конфигурационных файлов."""
        if cls._initialized:
            return
        
        cls._templates = {}
        skills_config_dir = config_dir / "skills"
        
        if not skills_config_dir.exists():
            raise FileNotFoundError(f"Skills config directory not found: {skills_config_dir}")

        # загружаем все YAML файлы
        
        for yaml_file in skills_config_dir.glob("*.yaml"):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data and 'skills' in  data:
                    for skill_data in data['skills']:
                        template = SkillTemplate.from_dict(skill_data)
                        cls._templates[template.id] = template
        
        cls._initialized = True
        print(f"Lodaded {len(cls._templates)} skill templates")
        
    @classmethod
    def get_template(cls, template_id: str) -> SkillTemplate:
        """Получает шаблон по ID"""
        if not cls._initialized:
            raise RuntimeError("SkillTemplateRepository not Inintialized")
        
        if template_id not in cls._templates:
            raise ValueError(f"Skill template not found: {template_id}")
        return cls._templates[template_id]
    
    
    @classmethod
    def get_all_template(cls) -> List[SkillTemplate]:
        """Получает все шаблоны."""
        if not cls._initialized:
            raise RuntimeError("SkilltemplateRepository not initialized")
        return list(cls._templates.values())
    
    @classmethod
    def get_template_by_type(cls, skill_type: str) -> List[SkillTemplate]:
        """Получает шаблоны по типу."""
        if not cls._initialized:
            raise RuntimeError("SkillTemplateRepository not initialized")
        return [t for t in cls._templates.values() if t.skill_type.value == skill_type]