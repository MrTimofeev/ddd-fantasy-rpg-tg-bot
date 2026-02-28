import yaml
from pathlib import Path
from typing import Dict, List

from ddd_fantasy_rpg.domain.items.item_template import ItemTemplate

# TODO: Сделать абстрактный класс и наследоваться от него
class ItemTemplateRepository:
    """Репозиторий шаблонов предметов (загружается из конфигурации)"""
    
    _templates: Dict[str, ItemTemplate] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls, config_dir: Path):
        """Инициализирует репозиторий из конфигурационных файлов."""
        
        if cls._initialized:
            return
        
        cls._templates = {}
        item_config_dir = config_dir / "items"
        
        if not item_config_dir.exists():
            raise FileNotFoundError(f"Item config directory not found: {item_config_dir}")
        
        # Загружаем все YAML файлы
        for yaml_file in item_config_dir.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data and 'items' in data:
                    for item_data in data["items"]:
                        template = ItemTemplate.from_dict(item_data)
                        cls._templates[template.id] = template
                        
        cls._initialized = True
        print(f"Loaded {len(cls._templates)} item templates")
        
        
    @classmethod
    def get_tempalate(cls, template_id: str) -> ItemTemplate:
        """Получает шаблон по ID"""
        if not cls._initialized:
            raise RuntimeError("ItemTemplateRepository not initialized")
        
        if template_id not in cls._templates:
            raise ValueError(f"Item template not found: {template_id}")
        return cls._templates[template_id]
    
    @classmethod
    def get_all_template(cls) -> List[ItemTemplate]:
        """Получаем все шаблоны."""
        if not cls._initialized:
            raise RuntimeError("ItemTemplateRepository not initialized")
        return list(cls._templates.values())