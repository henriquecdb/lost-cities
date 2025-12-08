from src.game.ai.base import AIPlayer, AIMove
from src.game.state import GameState
from src.game.ai.evaluator import evaluate_state
from src.game.ai.move_generator import get_possible_moves
from src.game.ai.simulator import apply_move


class AlphaBetaAI(AIPlayer):
    def get_move(self, state: GameState) -> AIMove:
        simulation_state = state.clone()
        simulation_state.deck_manager.deck.embaralhar()

        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')

        moves = get_possible_moves(simulation_state, self.player_id)

        if not moves:
            return None

        for move in moves:
            new_state = apply_move(simulation_state, move, self.player_id)
            score = self.alphabeta(
                new_state, self.depth - 1, alpha, beta, False)

            if move.draw_source == 'discard':
                score -= 50.0

            if move.action_type == 'discard':
                score -= 2.0

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move

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

                if move.draw_source == 'discard':
                    eval -= 20.0

                if move.action_type == 'discard':
                    eval -= 1.0

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
