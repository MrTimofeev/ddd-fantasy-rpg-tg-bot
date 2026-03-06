from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PlayerORM(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    race = Column(String, nullable=False)
    player_profession = Column(String, nullable=False)
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    
    stats = relationship("PlayerStatsORM", back_populates="player", uselist=False, cascade="all, delete-orphan")
    items = relationship("PlayerItemORM", back_populates="player", cascade="all, delete-orphan")


class PlayerStatsORM(Base):
    __tablename__ = "player_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(String, ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    strength = Column(Integer, default=0)
    agility = Column(Integer, default=0)
    intelligence = Column(Integer, default=0)
    max_hp = Column(Integer, default=0)
    damage = Column(Integer, default=0)
    armor = Column(Integer, default=0)
    
    player = relationship("PlayerORM", back_populates="stats")

class PlayerItemORM(Base):
    __tablename__ = "player_items"
    
    id = Column(String, primary_key=True)
    player_id = Column(String, ForeignKey("players.id", ondelete="CASCADE"), nullable=False, index=True)
    
    template_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    item_type = Column(String, nullable=False)
    rariry = Column(String, default="common")
    
    stats_json = Column(JSON, default=dict)
    
    is_equipped = Column(Boolean, default=False, index=True)
    slot_name = Column(String, nullable=True)
    
    modifiers_json = Column(JSON, default=dict)
    
    player = relationship("PlayerORM", back_populates="items")

class ExpeditionORM(Base):
    __tablename__ = "expeditions"

    id = Column(String, primary_key=True)
    player_id = Column(String, nullable=False)
    distance = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    outcome_type = Column(String, nullable=True)
    outcome_data = Column(JSON, nullable=True)
    status = Column(String, default="active", nullable=True)


class BattleORM(Base):
    __tablename__ = "battles"

    id = Column(String, primary_key=True)
    attacker_id = Column(String, nullable=False)
    defender_id = Column(String, nullable=False)
    attacker_data = Column(JSON, nullable=False)
    defender_data = Column(JSON, nullable=False)
    current_turn_owner_id = Column(String, nullable=True)
    is_finished = Column(Boolean, default=False)
    winner_id = Column(String, nullable=True)


# TODO: Нормализовать хранение сложных объектов таких как: inventory, Combatant
