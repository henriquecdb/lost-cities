from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.models.carta import Carta
from src.models.slot_carta import SlotCarta
from src.models.deck import DeckManager
from src.game.turn_manager import TurnManager


@dataclass
class PlayerState:
    hand: List[Carta] = field(default_factory=list)
    slots: List[SlotCarta] = field(default_factory=list)


@dataclass
class GameState:
    deck_manager: DeckManager
    turn_manager: TurnManager
    shared_slots: List[SlotCarta] = field(default_factory=list)
    players: Dict[int, PlayerState] = field(default_factory=dict)
    fim_jogo_processado: bool = False

    def reset(self) -> None:
        self.shared_slots = []
        self.players = {}
        self.fim_jogo_processado = False

    def configure_slots(self, colors: List[Tuple[int, int, int]],
                        positions: List[Tuple[int, int]]) -> None:
        self.shared_slots = []
        for idx, cor in enumerate(colors):
            x, y = positions[idx]
            self.shared_slots.append(SlotCarta(x, y, cor))

        self.players = {}
        for jogador in (1, 2):
            player_slots: List[SlotCarta] = []
            for idx, cor in enumerate(colors):
                x, y = positions[idx]
                player_slots.append(SlotCarta(x, y, cor))
            self.players[jogador] = PlayerState(hand=[], slots=player_slots)

    def get_player_hand(self, jogador: int) -> List[Carta]:
        return self.players[jogador].hand

    def get_player_slots(self, jogador: int) -> List[SlotCarta]:
        return self.players[jogador].slots

    def find_shared_slot(self, cor) -> Optional[SlotCarta]:
        for slot in self.shared_slots:
            if slot.cor == cor:
                return slot
        return None

    def find_player_slot(self, jogador: int, cor) -> Optional[SlotCarta]:
        for slot in self.players[jogador].slots:
            if slot.cor == cor:
                return slot
        return None
