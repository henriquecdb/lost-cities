from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from config.settings import DEFAULT_RANDOM_SEED
from src.game.ai.alphabeta import AlphaBetaAI
from src.game.ai.minimax import MinimaxAI
from src.game.ai.move_generator import get_possible_moves
from src.game.ai.q_learning import DEFAULT_Q_TABLE_PATH, QLearningAI
from src.game.manager import GameManager
from src.game.ai.evaluator import evaluate_state
from src.game.ai.base import AIMove


def _execute_move(manager: GameManager, player_id: int, move: AIMove) -> bool:
    """Replica o comportamento usado no loop principal do jogo."""
    current_hand = manager.get_hand(player_id)
    if move.card_index >= len(current_hand):
        return False

    carta = current_hand[move.card_index]

    if move.action_type == "play":
        success, _ = manager.tentar_jogar_em_expedicao(carta, carta.cor)
    else:
        success, _ = manager.tentar_descartar_carta(carta)

    if not success:
        return False

    if move.draw_source == "deck":
        manager.comprar_carta_deck()
    elif move.draw_source == "discard" and move.draw_color:
        manager.comprar_carta_descarte(move.draw_color)

    return True


def _create_opponent(player_id: int, opponent: str, depth: int) -> MinimaxAI | AlphaBetaAI:
    if opponent == "alphabeta":
        return AlphaBetaAI(player_id, depth)
    return MinimaxAI(player_id, depth)


def _score_difference(state, player_id: int) -> int:
    opponent = 2 if player_id == 1 else 1
    my_score = sum(slot.calcular_pontuacao()
                   for slot in state.get_player_slots(player_id))
    opponent_score = sum(slot.calcular_pontuacao()
                         for slot in state.get_player_slots(opponent))
    return my_score - opponent_score


def train_q_table(
    episodes: int,
    opponent: str = "minimax",
    table_path: Path = DEFAULT_Q_TABLE_PATH,
    epsilon_start: float = 0.3,
    epsilon_end: float = 0.05,
    opponent_depth: int = 1,
    seed: int = DEFAULT_RANDOM_SEED,
    lock_seed: bool = False,
) -> QLearningAI:
    agent = QLearningAI(player_id=1, depth=1, table_path=table_path,
                        epsilon=0.0, learning_rate=0.15, discount=0.92)
    base_seed = seed if seed is not None else random.randint(0, 10**6)

    for episode in range(episodes):
        epsilon = max(epsilon_end, epsilon_start * (0.97 ** episode))
        episode_seed = base_seed if lock_seed else base_seed + episode
        manager = GameManager.create_default(seed=episode_seed)
        opponent_ai = _create_opponent(2, opponent, opponent_depth)

        while not manager.state.turn_manager.jogo_terminado:
            current_player = manager.get_jogador_atual()

            if current_player == agent.player_id:
                moves = get_possible_moves(manager.state, agent.player_id)
                if not moves:
                    manager.checar_fim_de_jogo()
                    break

                state_key = agent.build_state_key(
                    manager.state, agent.player_id, moves)
                move, action_key = agent.choose_action(
                    manager.state, moves, epsilon)

                before = evaluate_state(manager.state, agent.player_id)
                success = _execute_move(manager, agent.player_id, move)
                finished = manager.checar_fim_de_jogo() is not None

                after = evaluate_state(manager.state, agent.player_id)
                reward = -5.0 if not success else after - before

                if finished:
                    reward += 0.5 * \
                        _score_difference(manager.state, agent.player_id)

                next_state_key = agent.build_state_key(
                    manager.state, agent.player_id)
                agent.update_q_value(state_key, action_key,
                                     reward, next_state_key)

                if finished:
                    break
            else:
                move = opponent_ai.get_move(manager.state)
                if move is None:
                    manager.checar_fim_de_jogo()
                    break
                _execute_move(manager, current_player, move)
                if manager.checar_fim_de_jogo() is not None:
                    break

    agent.save_table()
    return agent


def run_headless_match(player1: str, player2: str, depth1: int = 1, depth2: int = 1, seed: int = 1) -> str:
    manager = GameManager.create_default(seed=seed)
    manager.set_player_type(1, player1, depth1)
    manager.set_player_type(2, player2, depth2)

    while not manager.state.turn_manager.jogo_terminado:
        move = manager.get_ai_move()
        if move is None:
            break
        _execute_move(manager, manager.get_jogador_atual(), move)
        manager.checar_fim_de_jogo()

    return manager.checar_fim_de_jogo() or "Jogo não terminou"


def cli() -> None:
    parser = argparse.ArgumentParser(
        description="Treino do agente Q-Learning")
    parser.add_argument("--episodes", type=int, default=1,
                        help="Número de episódios de treino")
    parser.add_argument(
        "--opponent", choices=["minimax", "alphabeta"], default="minimax")
    parser.add_argument("--opponent-depth", type=int, default=1)
    parser.add_argument("--seed", type=int, default=DEFAULT_RANDOM_SEED,
                        help="Seed fixa para acelerar o treino")
    parser.add_argument("--lock-seed", action="store_true",
                        help="Força todos os episódios a usarem a mesma seed")
    parser.add_argument("--table", type=Path,
                        default=DEFAULT_Q_TABLE_PATH, help="Arquivo de saída da tabela Q")
    args = parser.parse_args()

    start = time.time()
    agent = train_q_table(args.episodes, args.opponent,
                          table_path=args.table,
                          opponent_depth=args.opponent_depth,
                          seed=args.seed,
                          lock_seed=args.lock_seed)
    duration = time.time() - start
    print(
        f"Treino finalizado em {duration:.2f}s. Tabela salva em {args.table}")


if __name__ == "__main__":
    cli()
