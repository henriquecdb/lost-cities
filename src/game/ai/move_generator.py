from typing import List, Tuple
from src.game.state import GameState
from src.game.ai.base import AIMove
from config.settings import Colors


def get_possible_moves(state: GameState, player_id: int) -> List[AIMove]:
    hand = state.get_player_hand(player_id)
    colors = Colors.get_available_colors()
    color_order = {cor: idx for idx, cor in enumerate(colors)}
    deck_has_cards = state.deck_manager.deck.tem_cartas()

    moves_with_keys: List[Tuple[Tuple[int, int,
                                      int, int, int, int, int], AIMove]] = []

    def append_move(move: AIMove) -> None:
        carta = hand[move.card_index]
        action_priority = 0 if move.action_type == 'play' else 1
        draw_priority = 0 if move.draw_source == 'deck' else 1
        card_type_priority = 0 if carta.tipo_carta == 'investimento' else 1
        card_color_priority = color_order.get(carta.cor, 99)
        card_value = carta.numero if carta.tipo_carta == 'numerada' else -1
        draw_color_priority = color_order.get(move.draw_color, -1)
        key = (
            action_priority,
            draw_priority,
            card_color_priority,
            card_type_priority,
            card_value,
            draw_color_priority,
            move.card_index,
        )
        moves_with_keys.append((key, move))

    for index, carta in enumerate(hand):
        slot_jogador = state.find_player_slot(player_id, carta.cor)
        pode_jogar = (
            slot_jogador is not None
            and state.turn_manager.validar_jogada_em_expedicao(carta, slot_jogador)
        )

        if pode_jogar:
            if deck_has_cards:
                append_move(AIMove(card_index=index,
                            action_type='play', draw_source='deck'))

            for cor in colors:
                topo_descarte = state.deck_manager.ver_topo_descarte(cor)
                if topo_descarte is not None:
                    append_move(AIMove(
                        card_index=index,
                        action_type='play',
                        draw_source='discard',
                        draw_color=cor,
                    ))

        if deck_has_cards:
            append_move(AIMove(card_index=index,
                        action_type='discard', draw_source='deck'))

        for cor in colors:
            if cor == carta.cor:
                continue

            topo_descarte = state.deck_manager.ver_topo_descarte(cor)
            if topo_descarte is not None:
                append_move(AIMove(
                    card_index=index,
                    action_type='discard',
                    draw_source='discard',
                    draw_color=cor,
                ))

    moves_with_keys.sort(key=lambda item: item[0])
    return [move for _, move in moves_with_keys]
