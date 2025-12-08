from src.game.ai.base import AIPlayer, AIMove
from src.game.state import GameState
from src.game.ai.evaluator import evaluate_state
from src.game.ai.move_generator import get_possible_moves
from src.game.ai.simulator import apply_move


class MinimaxAI(AIPlayer):
    def get_move(self, state: GameState) -> AIMove:
        simulation_state = state.clone()
        simulation_state.deck_manager.deck.embaralhar()

        best_score = float('-inf')
        best_move = None

        moves = get_possible_moves(simulation_state, self.player_id)

        if not moves:
            return None

        for move in moves:
            new_state = apply_move(simulation_state, move, self.player_id)
            score = self.minimax(new_state, self.depth - 1, False)

            if move.draw_source == 'discard':
                score -= 5.0

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, state: GameState, depth: int, maximizing: bool) -> float:
        if depth == 0 or state.turn_manager.jogo_terminado:
            return evaluate_state(state, self.player_id)

        if maximizing:
            max_eval = float('-inf')
            moves = get_possible_moves(state, self.player_id)
            if not moves:
                return evaluate_state(state, self.player_id)

            for move in moves:
                new_state = apply_move(state, move, self.player_id)
                eval = self.minimax(new_state, depth - 1, False)

                if move.draw_source == 'discard':
                    eval -= 2.0

                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            opponent_id = 3 - self.player_id
            moves = get_possible_moves(state, opponent_id)
            if not moves:
                return evaluate_state(state, self.player_id)

            for move in moves:
                new_state = apply_move(state, move, opponent_id)
                eval = self.minimax(new_state, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval
