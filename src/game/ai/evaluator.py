from typing import Dict, List, Tuple
from config.settings import Colors
from src.game.state import GameState


def evaluate_state(state: GameState, player_id: int) -> float:
    opponent_id = 3 - player_id
    my_heuristic, my_board_progress = _calculate_metrics(state, player_id)
    op_heuristic, op_board_progress = _calculate_metrics(state, opponent_id)

    tempo_bonus = 0.5 if state.turn_manager.get_jogador_atual() == player_id else 0.0

    score_diff = my_heuristic - (op_heuristic * 0.5)

    board_delta = (my_board_progress - op_board_progress) * 1.0

    return float(score_diff + tempo_bonus + board_delta)


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

    desenvolvimento = len(playable_numbers) * 2.0 + soma_potencial * 0.3
    investimento_bonus = (investimentos_no_slot + playable_investments) * 4.0
    backlog_penalty = (len(hand_numbers) - len(playable_numbers)) * 1.0

    if not numeros_no_slot:
        abertura_bonus = 6.0 if playable_numbers else 0.0
        mao_pressao = (len(hand_cards) -
                       len(playable_numbers) - playable_investments) * -0.5
        return pontuacao_projetada * 0.6 + desenvolvimento + \
            investimento_bonus + abertura_bonus + mao_pressao
    else:
        progresso_real = float(actual_score)
        return pontuacao_projetada + desenvolvimento + investimento_bonus - backlog_penalty + progresso_real * 0.2
