from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


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
    inventory = Column(JSON, default=list)
    equipped = Column(JSON, default=dict)
    
    base_stats = Column(JSON, default=dict)


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
