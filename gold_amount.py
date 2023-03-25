from __future__ import annotations
from dataclasses import dataclass

@dataclass(order=True)
class GoldAmount:
    gold: int
    silver: int
    copper: int

    @staticmethod
    def from_copper(raw_value) -> GoldAmount:
        # Convert copper to silver
        silver = raw_value // 100
        # Convert silver to gold
        gold = silver // 100
        # Calculate remaining silver and copper
        silver %= 100
        copper = raw_value % 100
        # Return GoldAmount object
        return GoldAmount(int(gold), int(silver), int(copper))

    def to_copper(self) -> int:
        # Convert gold and silver to copper
        return (self.gold * 10**4) + \
            (self.silver * 10**2) +  \
            (self.copper * 10**0)
    
    def __add__(self, other: GoldAmount) -> GoldAmount:
        return GoldAmount.from_copper(
            self.to_copper() + other.to_copper()
        )
    
    def __dict__(self):
        return self.to_copper()

    def __mul__(self, val: int) -> GoldAmount:
        return GoldAmount.from_copper(self.to_copper() * val)
    
    def __truediv__(self, val: float) -> GoldAmount:
        return GoldAmount.from_copper(self.to_copper() / val)

    def __str__(self) -> str:
        result = ""
        if self.gold != 0:
            result += f"{self.gold:,}g"
        if self.silver != 0:
            result += f"{self.silver}s"
        result += f"{self.copper}cu"
        return result

    def __repr__(self) -> str:
        return f"GoldAmount(gold={self.gold}, silver={self.silver}, copper={self.copper})"
