from dataclasses import dataclass

@dataclass
class EmpruntReturned:
    empruntId: int
    returned: bool
