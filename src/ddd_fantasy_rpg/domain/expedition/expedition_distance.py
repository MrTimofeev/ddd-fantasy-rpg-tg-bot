from enum import Enum


class ExpeditionDistance(Enum):
    NEAR = ("near", 1)  # 10
    MEDIUM = ("medium", 1)  # 20
    FAR = ("far", 1)  # 30

    def __init__(self, key: str, duration: int):
        self.key = key
        self.duration_minutes = duration
