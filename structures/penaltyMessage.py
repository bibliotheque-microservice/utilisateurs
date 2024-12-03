from dataclasses import dataclass

@dataclass
class PenaltyMessage:
    userId: int
    livreId: int
    amount: float
