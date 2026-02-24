import random

from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider


class SystemRandomProvider(RandomProvider):
    def randint(self, a: int, b: int) -> int:
        return random.randint(a, b)
    
    def choice(self, seq):
        return random.choice(seq)
 
    def random(self):
        return random.random()   
