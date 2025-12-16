import json
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config.settings import Colors
from src.game.ai.base import AIPlayer, AIMove
from src.game.ai.evaluator import evaluate_state
from src.game.ai.move_generator import get_possible_moves

DEFAULT_Q_TABLE_PATH = Path("files/q_table.json")


class QLearningAI(AIPlayer):
    """IA tabular simples baseada em Q-Learning.

    Durante o jogo normal (não treino) ela apenas consulta a tabela
    já treinada para escolher o movimento com maior valor esperado.
    O processo de treino vive no módulo q_learning_trainer.py.
    """

    def __init__(
        self,
        player_id: int,
        depth: int,
        table_path: Path | str = DEFAULT_Q_TABLE_PATH,
        epsilon: float = 0.05,
        learning_rate: float = 0.1,
        discount: float = 0.95,
    ) -> None:
        super().__init__(player_id, depth)
        self.table_path = Path(table_path)
        self.epsilon = max(0.0, epsilon)
        self.learning_rate = learning_rate
        self.discount = discount
        self.q_table: Dict[str, Dict[str, float]] = {}
        self._load_table()

    # ------------------------------------------------------------------
    # Tabela Q utilitária
    # ------------------------------------------------------------------
    def _load_table(self) -> None:
        if self.table_path.exists():
            with self.table_path.open("r", encoding="utf-8") as fp:
                self.q_table = json.load(fp)
        else:
            self.q_table = {}

    def save_table(self) -> None:
        self.table_path.parent.mkdir(parents=True, exist_ok=True)
        with self.table_path.open("w", encoding="utf-8") as fp:
            json.dump(self.q_table, fp, indent=2)

    # ------------------------------------------------------------------
    # Métodos estáticos que também serão usados no treinamento
    # ------------------------------------------------------------------
    @staticmethod
    def build_state_key(state, player_id: int, moves: Optional[List[AIMove]] = None) -> str:
        """Reduz o estado a poucos números humanos."""

        hand_size = len(state.get_player_hand(player_id))
        moves = moves or get_possible_moves(state, player_id)
        playable_count = sum(1 for move in moves if move.action_type == "play")

        deck_size = state.deck_manager.deck.quantidade_cartas()
        deck_bucket = min(4, deck_size // 10)

        my_score = sum(slot.calcular_pontuacao()
                       for slot in state.get_player_slots(player_id))
        opponent_id = 2 if player_id == 1 else 1
        opponent_score = sum(slot.calcular_pontuacao()
                             for slot in state.get_player_slots(opponent_id))
        score_bucket = max(-40, min(120, my_score))
        diff_bucket = max(-120, min(120, my_score - opponent_score))

        expedition_profile = []
        colors = Colors.get_available_colors()
        for idx, color in enumerate(colors):
            slot = state.find_player_slot(player_id, color)
            if slot is None:
                expedition_profile.append(f"{idx}:0:0:0")
                continue
            total_cards = slot.get_quantidade_cartas()
            investments = sum(
                1 for carta in slot.cartas if carta.tipo_carta == "investimento")
            highest = max(
                (carta.numero for carta in slot.cartas if carta.tipo_carta == "numerada"), default=0)
            expedition_profile.append(
                f"{idx}:{total_cards}:{investments}:{highest}")

        profile_str = ",".join(expedition_profile)

        return (
            f"H{hand_size}|P{playable_count}|D{deck_bucket}|S{score_bucket}"
            f"|DIFF{diff_bucket}|EXP[{profile_str}]"
        )

    @staticmethod
    def _describe_card(card) -> str:
        color_name = Colors.get_color_names().get(card.cor, "Unknown")
        if card.tipo_carta == "investimento":
            value = "INV"
        else:
            value = str(card.numero)
        return f"{color_name}:{value}"

    @classmethod
    def build_action_key(cls, state, move: AIMove, player_id: int) -> str:
        hand = state.get_player_hand(player_id)
        if move.card_index >= len(hand):
            return f"{move.action_type}|{move.draw_source}|INVALID"
        card = hand[move.card_index]
        card_desc = cls._describe_card(card)
        draw_color = Colors.get_color_names().get(
            move.draw_color, "-") if move.draw_color else "DECK"
        return f"{move.action_type}|{move.draw_source}|{draw_color}|{card_desc}"

    def _get_q_value(self, state_key: str, action_key: str) -> float:
        return self.q_table.get(state_key, {}).get(action_key, 0.0)

    def update_q_value(
        self,
        state_key: str,
        action_key: str,
        reward: float,
        next_state_key: str,
    ) -> float:
        current = self._get_q_value(state_key, action_key)
        future = max(self.q_table.get(
            next_state_key, {}).values(), default=0.0)
        updated = current + self.learning_rate * \
            (reward + self.discount * future - current)
        self.q_table.setdefault(state_key, {})[action_key] = updated
        return updated

    # ------------------------------------------------------------------
    # Escolha de jogadas (modo inferência)
    # ------------------------------------------------------------------
    def get_move(self, state) -> Optional[AIMove]:
        moves = get_possible_moves(state, self.player_id)
        if not moves:
            return None
        action, _ = self.choose_action(state, moves, self.epsilon)
        return action

    # ------------------------------------------------------------------
    # Funções auxiliares para usar durante o treinamento offline
    # ------------------------------------------------------------------
    def choose_action(
        self,
        state,
        moves: List[AIMove],
        epsilon: float,
    ) -> Tuple[AIMove, str]:
        state_key = self.build_state_key(state, self.player_id, moves)
        if not moves:
            raise ValueError("Nenhum movimento disponível para Q-Learning")

        explore = random.random() < epsilon
        if explore:
            move = random.choice(moves)
            action_key = self.build_action_key(state, move, self.player_id)
            return move, action_key

        best_value = float("-inf")
        best_candidates: List[Tuple[AIMove, str]] = []
        for move in moves:
            action_key = self.build_action_key(state, move, self.player_id)
            value = self._get_q_value(state_key, action_key)
            if value > best_value + 1e-6:
                best_value = value
                best_candidates = [(move, action_key)]
            elif abs(value - best_value) <= 1e-6:
                best_candidates.append((move, action_key))

        if best_candidates:
            return random.choice(best_candidates)
        move = random.choice(moves)
        return move, self.build_action_key(state, move, self.player_id)

    def greedy_value(self, state) -> float:
        moves = get_possible_moves(state, self.player_id)
        if not moves:
            return 0.0
        _, action_key = self.choose_action(state, moves, epsilon=0.0)
        state_key = self.build_state_key(state, self.player_id, moves)
        return self._get_q_value(state_key, action_key)
