from src.game.state import GameState
from src.game.ai.base import AIMove


def apply_move(state: GameState, move: AIMove, player_id: int) -> GameState:
    new_state = state.clone()

    hand = new_state.get_player_hand(player_id)
    if move.card_index >= len(hand):
        return new_state

    carta = hand[move.card_index]

    if move.action_type == 'play':
        slot_jogador = new_state.find_player_slot(player_id, carta.cor)
        slot_compartilhado = new_state.find_shared_slot(carta.cor)
        if slot_jogador and slot_compartilhado:
            slot_jogador.adicionar_carta(carta)
            slot_compartilhado.adicionar_carta(carta, player_id)
            hand.remove(carta)
            new_state.turn_manager.registrar_carta_jogada(carta, 'expedicao')

    elif move.action_type == 'discard':
        if new_state.deck_manager.descartar_carta(carta):
            hand.remove(carta)
            new_state.turn_manager.registrar_carta_jogada(carta, 'descarte')

    if move.draw_source == 'deck':
        carta_comprada = new_state.deck_manager.comprar_do_deck()
        if carta_comprada:
            hand.append(carta_comprada)
            new_state.turn_manager.registrar_carta_comprada('deck')

    elif move.draw_source == 'discard' and move.draw_color:
        carta_comprada = new_state.deck_manager.comprar_do_descarte(
            move.draw_color)
        if carta_comprada:
            hand.append(carta_comprada)
            new_state.turn_manager.registrar_carta_comprada('descarte')

    return new_state
