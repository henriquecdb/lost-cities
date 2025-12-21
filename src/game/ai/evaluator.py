from dataclasses import dataclass
from typing import Dict, List, Tuple

from config.settings import Colors
from src.game.state import GameState


@dataclass(frozen=True)
class HeuristicWeights:
    my_potential: float = 1.0
    opponent_potential: float = -0.5
    board_progress: float = 1.0
    tempo_bonus: float = 0.5


@dataclass(frozen=True)
class ExpeditionWeights:
    projected_score: float = 1.0
    empty_projected_multiplier: float = 0.6
    playable_count: float = 2.0
    playable_sum: float = 0.3
    investment_bonus: float = 4.0
    backlog_penalty: float = -1.0
    opening_bonus: float = 6.0
    hand_pressure: float = -0.5
    progress_bonus: float = 0.2


WEIGHTS = HeuristicWeights()
EXPEDITION_WEIGHTS = ExpeditionWeights()


def evaluate_state(state: GameState, player_id: int) -> float:
    opponent_id = 3 - player_id
    my_heuristic, my_board_progress = _calculate_metrics(state, player_id)
    op_heuristic, op_board_progress = _calculate_metrics(state, opponent_id)

    tempo_flag = 1.0 if state.turn_manager.get_jogador_atual() == player_id else 0.0

    score = 0.0
    score += WEIGHTS.my_potential * my_heuristic
    score += WEIGHTS.opponent_potential * op_heuristic
    score += WEIGHTS.board_progress * (my_board_progress - op_board_progress)
    score += WEIGHTS.tempo_bonus * tempo_flag

    return float(score)


def _calculate_metrics(state: GameState, player_id: int) -> Tuple[float, float]:
    heuristic_total = 0.0

    hand = state.get_player_hand(player_id)
    slots = state.get_player_slots(player_id)

    hand_by_color: Dict[tuple, List] = {cor: []
                                        for cor in Colors.get_available_colors()}
    for carta in hand:
        hand_by_color.setdefault(carta.cor, []).append(carta)

    cards_played_count = 0
    expeditions_score_sum = 0

    for slot in slots:
        actual_score = slot.calcular_pontuacao()
        cards_played_count += len(slot.cartas)
        expeditions_score_sum += actual_score

        cartas_mao_cor = hand_by_color.get(slot.cor, [])
        heuristic_total += _evaluate_expedition(slot,
                                                cartas_mao_cor, actual_score)

    board_progress = cards_played_count * 1.0 + expeditions_score_sum * 0.1
    return heuristic_total, board_progress


def _evaluate_expedition(slot, hand_cards: List, actual_score: int) -> float:
    cartas_no_slot = slot.cartas
    numeros_no_slot = [
        c.numero for c in cartas_no_slot if c.tipo_carta == 'numerada']
    ultimo_numero = numeros_no_slot[-1] if numeros_no_slot else 0
    investimentos_no_slot = sum(
        1 for c in cartas_no_slot if c.tipo_carta == 'investimento')

    hand_numbers = sorted(
        [c.numero for c in hand_cards if c.tipo_carta == 'numerada'])
    playable_numbers = [num for num in hand_numbers if num >= ultimo_numero]

    investment_cards_hand = [
        c for c in hand_cards if c.tipo_carta == 'investimento']

    available_investment_slots = 0 if numeros_no_slot else max(
        0, 3 - investimentos_no_slot)
    playable_investments = min(
        len(investment_cards_hand), available_investment_slots)

    soma_atual = sum(numeros_no_slot)
    soma_potencial = sum(playable_numbers)
    multiplicador = 1 + investimentos_no_slot + playable_investments

    pontuacao_projetada = (soma_atual + soma_potencial - 20) * multiplicador

    total_cartas_planejadas = len(numeros_no_slot) + \
        len(playable_numbers) + playable_investments
    if total_cartas_planejadas >= 8:
        pontuacao_projetada += 20

    score = 0.0
    projected = pontuacao_projetada * (EXPEDITION_WEIGHTS.empty_projected_multiplier
                                       if not numeros_no_slot
                                       else EXPEDITION_WEIGHTS.projected_score)
    score += projected

    score += len(playable_numbers) * EXPEDITION_WEIGHTS.playable_count
    score += soma_potencial * EXPEDITION_WEIGHTS.playable_sum
    score += (investimentos_no_slot + playable_investments) * \
        EXPEDITION_WEIGHTS.investment_bonus

    backlog = (len(hand_numbers) - len(playable_numbers)) * \
        EXPEDITION_WEIGHTS.backlog_penalty
    score += backlog

    if not numeros_no_slot:
        score += EXPEDITION_WEIGHTS.opening_bonus if playable_numbers else 0.0
        mao_pressao = (len(hand_cards) - len(playable_numbers) -
                       playable_investments) * EXPEDITION_WEIGHTS.hand_pressure
        score += mao_pressao
    else:
        progresso_real = float(actual_score)
        score += progresso_real * EXPEDITION_WEIGHTS.progress_bonus

    return score
