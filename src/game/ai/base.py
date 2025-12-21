from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple
from src.game.state import GameState


@dataclass
class AIMove:
    card_index: int
    action_type: str
    draw_source: str
    draw_color: Optional[Tuple[int, int, int]] = None


class AIPlayer(ABC):
    def __init__(self, player_id: int, depth: int):
        self.player_id = player_id
        self.depth = depth

    @abstractmethod
    def get_move(self, state: GameState) -> AIMove:
        pass
