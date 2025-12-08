from typing import Dict, List, Tuple
from config.settings import Colors
from src.game.state import GameState


def evaluate_state(state: GameState, player_id: int) -> float:
    opponent_id = 3 - player_id
    my_heuristic, my_board_progress = _calculate_metrics(state, player_id)
    op_heuristic, op_board_progress = _calculate_metrics(state, opponent_id)

    tempo_bonus = 0.5 if state.turn_manager.get_jogador_atual() == player_id else 0.0
    board_delta = (my_board_progress - op_board_progress) * 1.2

    return float(my_heuristic - op_heuristic + tempo_bonus + board_delta)


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
    if not slot.cartas and not hand_cards:
        return 0.0

    numbers_on_board = [
        c.numero for c in slot.cartas if c.tipo_carta == 'numerada']
    investments_played = sum(
        1 for c in slot.cartas if c.tipo_carta == 'investimento')
    last_value = numbers_on_board[-1] if numbers_on_board else 0

    hand_numbers = sorted(
        [c.numero for c in hand_cards if c.tipo_carta == 'numerada'])
    playable_numbers = [num for num in hand_numbers if num >= last_value]

    investment_cards = [
        c for c in hand_cards if c.tipo_carta == 'investimento']

    if numbers_on_board:
        playable_investments = 0
        dead_investments = len(investment_cards)
    else:
        available_slots = max(0, 3 - investments_played)
        playable_investments = min(len(investment_cards), available_slots)
        dead_investments = len(investment_cards) - playable_investments

    current_sum = sum(numbers_on_board)
    potential_sum = sum(playable_numbers)
    total_investments = investments_played + playable_investments
    multiplier = 1 + total_investments

    projected_raw_score = (current_sum + potential_sum - 20) * multiplier

    projected_cards_count = len(slot.cartas) + \
        len(playable_numbers) + playable_investments
    if projected_cards_count >= 8:
        projected_raw_score += 20

    if not slot.cartas:
        if projected_raw_score > 0:
            return projected_raw_score * 0.4
        else:
            raw_potential = (current_sum + potential_sum) * multiplier

            if playable_investments > 0:
                return 2.0 + raw_potential * 0.2 + len(playable_numbers) * 1.0

            return raw_potential * 0.15 + len(playable_numbers) * 0.8

    else:
        score = float(actual_score)

        if actual_score < 0:
            if projected_raw_score > 0:
                score = max(score, 0.0)
                score += 4.0
            elif projected_raw_score > actual_score:
                cards_in_hand_count = len(
                    playable_numbers) + playable_investments
                confidence = min(1.0, cards_in_hand_count / 2.0)
                mitigation = 20.0 * confidence
                score += mitigation
        if projected_raw_score > actual_score:
            potential_gain = projected_raw_score - actual_score
            score += potential_gain * 0.8

        score -= dead_investments * 10.0

        score += investments_played * 10.0

        blocked_numbers = len(hand_numbers) - len(playable_numbers)
        score -= blocked_numbers * 5.0

        return score
