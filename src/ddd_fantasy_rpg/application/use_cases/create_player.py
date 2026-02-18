from ddd_fantasy_rpg.domain.player import Player, Race, PlayerClass
from ddd_fantasy_rpg.domain.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.exceptions import PlayerAlreadyExistingError


class CreatePlayerUseCase:
    """
    Use Case для создания нового игрока.
    """
    
    async def execute(
        self,
        player_id: str,
        telegram_id: int,
        name: str,
        uow: UnitOfWork,
        race: Race = Race.HUMAN,
        player_class: PlayerClass = PlayerClass.WARRIOR,
    ):
        """
        Создает нового игрока с заданными параметрами.
        """
        
        # Проверяем, существует ли игрок
        existing = await uow.players.get_by_id(player_id)
        if existing:
            raise  PlayerAlreadyExistingError(player_id)
        
        # Создаем агрегат
        # TODO: Сделать нормыльный выбор персонажа
        player = Player(
            player_id=player_id,
            telegram_id=telegram_id,
            name=name,
            race=race,
            player_profession=player_class
        )
        
        await uow.players.save(player)
        
        return player