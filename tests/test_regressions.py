import contextlib
import io
import random
import unittest
from unittest.mock import patch

from game_rules import winner, tactical_move, board_position
from ttt_class import tictactoe_game as TrainingGame
from ttt_performance_measure import tictactoe_game as EvaluationGame


class RegressionTests(unittest.TestCase):
    def game(self, episodes=1):
        with contextlib.redirect_stdout(io.StringIO()):
            return TrainingGame('QLAgent', 'LogicAgent', episodes, {})

    def test_every_reachable_board(self):
        # Independent oracle using rows, columns and diagonals.
        def oracle(board):
            rows = [board[i:i + 3] for i in (0, 3, 6)]
            lines = rows + list(zip(*rows)) + [board[::4], board[2:7:2]]
            for line in lines:
                if len(set(line)) == 1 and line[0] in ('X', 'O'):
                    return line[0]
            return 'Draw' if all(c in ('X', 'O') for c in board) else None

        seen = set()
        def visit(board, turn):
            if board in seen:
                return
            seen.add(board)
            expected = oracle(board)
            self.assertEqual(winner(board), expected, board)
            if expected:
                return
            for i, cell in enumerate(board):
                if cell not in ('X', 'O'):
                    visit(board[:i] + turn + board[i + 1:], 'O' if turn == 'X' else 'X')
        visit('012345678', 'X')
        self.assertEqual(len(seen), 5478)

    def test_board_click_boundaries(self):
        for point in ((50, 350), (0, 300), (-1, 10), (300, 10)):
            self.assertIsNone(board_position(*point))
        self.assertEqual(board_position(0, 0), ('0', 0, 0))
        self.assertEqual(board_position(299, 299), ('8', 2, 2))
        self.assertEqual(board_position(100, 100), ('4', 1, 1))

    def test_win_before_block(self):
        self.assertEqual(tactical_move('OO2XX5678', 'X'), (True, '5'))

    def test_q_target_uses_legal_values_not_action_indices(self):
        game = self.game()
        game.prevState = list('012345678')
        game.prevMove = 0
        game.state = list('XO2345678')
        game.valid = list('2345678')
        for state in ('012345678', 'XO2345678'):
            game.add_key(state)
        game.qtable['XO2345678'][0] = 100  # Occupied square must be ignored.
        game.qtable['XO2345678'][8] = 0.9
        game.update_qtable(0)
        self.assertAlmostEqual(game.qtable['012345678'][0], 0.0045)

    def test_terminal_reward_does_not_bootstrap(self):
        for outcome, reward in (('X', 1), ('O', -1), ('Draw', 0)):
            game = self.game()
            game.prevState = list('012345678')
            game.prevMove = 0
            game.add_key('012345678')
            game.isWinner = outcome
            game.state = list('XOXOXOOXX')
            game.update_qtable(reward)
            self.assertEqual(game.qtable['012345678'][0], 0.5 * reward)

    def test_one_update_per_agent_move_after_opponent_reply(self):
        game = self.game(100)
        agent_moves = []
        update_states = []
        original_move = game.play_move
        original_update = game.update_qtable
        def move():
            if game.current_player == 'QLAgent':
                agent_moves.append(tuple(game.state))
            original_move()
        def update(reward):
            state = ''.join(game.state)
            if game.isWinner is None:
                self.assertEqual(state.count('X'), state.count('O'))
            update_states.append(state)
            original_update(reward)
        with patch.object(game, 'play_move', side_effect=move), patch.object(game, 'update_qtable', side_effect=update):
            random.seed(123)
            game.play_game()
        self.assertEqual(len(agent_moves), len(update_states))
        self.assertEqual(game.xwin_count + game.ywin_count + game.draw_count, 100)

    def test_unsupported_training_roles_fail_explicitly(self):
        with self.assertRaises(ValueError):
            TrainingGame('Random', 'QLAgent', 1, {})

    def test_evaluation_uses_shared_full_board_result(self):
        game = EvaluationGame.__new__(EvaluationGame)
        game.valid = ['stale value']
        self.assertEqual(game.check_winner(list('XOXOXOOXX')), 'X')

    def test_exploration_probability(self):
        game = self.game()
        game.add_key('012345678')
        game.qtable['012345678'][4] = 1
        game.exploration = 0
        self.assertEqual(game.choose_action('012345678'), '4')
        game.exploration = 1
        with patch('ttt_class.random.choice', return_value='8'):
            self.assertEqual(game.choose_action('012345678'), '8')


if __name__ == '__main__':
    unittest.main()
