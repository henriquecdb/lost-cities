from src.game.ai.base import AIPlayer, AIMove
from src.game.state import GameState
from src.game.ai.evaluator import evaluate_state
from src.game.ai.move_generator import get_possible_moves
from src.game.ai.simulator import apply_move, determinize_state


class AlphaBetaAI(AIPlayer):
    def __init__(self, player_id: int, depth: int, simulation_runs: int = 5):
        super().__init__(player_id, depth)
        self.simulation_runs = max(1, simulation_runs)

    def get_move(self, state: GameState) -> AIMove:
        best_score = float('-inf')
        best_move = None

        moves = get_possible_moves(state, self.player_id)

        if not moves:
            return None

        for move in moves:
            score = self._evaluate_move_with_sampling(state, move)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _evaluate_move_with_sampling(self, root_state: GameState, move: AIMove) -> float:
        total_score = 0.0

        for _ in range(self.simulation_runs):
            simulation_state = root_state.clone()
            determinize_state(simulation_state, self.player_id)
            new_state = apply_move(simulation_state, move, self.player_id)
            total_score += self.alphabeta(
                new_state, self.depth - 1, float('-inf'), float('inf'), False)

        return total_score / self.simulation_runs

    def alphabeta(self, state: GameState, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        if depth == 0 or state.turn_manager.jogo_terminado:
            return evaluate_state(state, self.player_id)

        if maximizing:
            max_eval = float('-inf')
            moves = get_possible_moves(state, self.player_id)
            if not moves:
                return evaluate_state(state, self.player_id)

            for move in moves:
                new_state = apply_move(state, move, self.player_id)
                eval = self.alphabeta(new_state, depth - 1, alpha, beta, False)

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            opponent_id = 3 - self.player_id
            moves = get_possible_moves(state, opponent_id)
            if not moves:
                return evaluate_state(state, self.player_id)

            for move in moves:
                new_state = apply_move(state, move, opponent_id)
                eval = self.alphabeta(new_state, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
