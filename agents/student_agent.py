# Student agent: Add your own agent here
from copy import deepcopy

from agents.agent import Agent
from store import register_agent
import numpy as np
import math

import sys

moves = ((-1, 0), (0, 1), (1, 0), (0, -1))


def check_endgame(chess_board, original_position, opponent_pos):
    r1, c1, d1 = original_position
    r2, c2, d2 = opponent_pos

    si = int(chess_board[0].size/4)
    si = si

    # Union-Find
    father = dict()
    for r in range(si):
        for c in range(si):
            father[(r, c)] = (r, c)

    def find(pos):
        if father[pos] != pos:
            father[pos] = find(father[pos])
        return father[pos]

    def union(pos1, pos2):
        father[pos1] = pos2

    for r in range(si):
        for c in range(si):
            for dir, move in enumerate(
                    moves[1:3]
            ):  # Only check down and right
                if chess_board[r, c, dir + 1]:
                    continue
                pos_a = find((r, c))
                pos_b = find((r + move[0], c + move[1]))
                if pos_a != pos_b:
                    union(pos_a, pos_b)

    for r in range(si):
        for c in range(si):
            find((r, c))

    p0_r = find(tuple((r1, c1)))
    p1_r = find(tuple((r2, c2)))

    if p0_r == p1_r:
        return False

    return True


def check_boundary(board, pos):
    r, c = pos
    si = int(board[0].size/4)
    si = si - 1
    return 0 <= r < si and 0 <= c < si


def check_valid_step(chess_board, start_pos, end_pos, barrier_dir, max_step1, opponent_move):
    # Endpoint already has barrier or is boarder
    chess_board = deepcopy(chess_board)

    r, c = end_pos

    if not check_boundary(chess_board, end_pos):
        return False

    if chess_board[r, c, barrier_dir]:
        return False

    if np.array_equal(start_pos, end_pos):
        return True

    # Get position of the adversary
    adv_pos = opponent_move

    # BFS
    state_queue = [(start_pos, 0)]
    visited = {tuple(start_pos)}
    is_reached = False
    while state_queue and not is_reached:
        cur_pos, cur_step = state_queue.pop(0)
        r, c = cur_pos
        if cur_step == max_step1:
            break
        for dir, move in enumerate(moves):
            if chess_board[r, c, dir]:
                continue

            r1, c1 = move
            r2, c2 = cur_pos

            next_pos = (r2 + r1, c2 + c1)

            if (np.array_equal(next_pos, adv_pos)) or (tuple(next_pos) in visited):
                continue
            if np.array_equal(next_pos, end_pos):
                is_reached = True
                break

            visited.add(tuple(next_pos))
            state_queue.append((next_pos, cur_step + 1))

    return is_reached


def move_in(chess_board, next_position):
    chess_board = deepcopy(chess_board)
    r, c, dir1 = next_position

    chess_board[r, c, dir1] = True
    return chess_board


def all_valid_moves(chess_b, my_pos, max_step, opponent_move):
    move_list = []
    valid_list = []
    r, c = my_pos
    r1 = r - max_step
    c1 = c
    for dir1 in range(4):
        for x in range(max_step + 1):
            for y in range(-x, x + 1, 1):
                if check_valid_step(chess_b, my_pos, (r1 + x, c1 + y), dir1, max_step, opponent_move):
                    move_list.append((r1 + x, c1 + y, dir1))
                # print((r1 + x, c1 + y))

        r2 = r + max_step
        c2 = c
        for x in range(max_step - 1, -1, -1):
            for y in range(-x, x + 1, 1):
                if check_valid_step(chess_b, my_pos, (r2-x,c2-y), dir1, max_step, opponent_move):
                    move_list.append((r2 - x, c2 - y, dir1))
                # print((r2 - x, c2 - y))

    return move_list


def final_score(board, original_position, opponent_pos, max_step):
    r1, c1, d1 = original_position
    r2, c2, d2 = opponent_pos
    score1 = len(all_valid_moves(board, (r1, c1), max_step, (r2,c2)))

    score2 = len(all_valid_moves(board, (r2, c2), max_step, (r1, c1)))
    score = score1 - score2
    return score1


def minimax_layer2(board, original_position, opponent_pos, max_step): #min
    max_vale = -1000
    r1, c1, d1 = original_position
    r2, c2, d2 = opponent_pos
    score = max_vale
    for moves in all_valid_moves(board, (r1,c1), max_step, (r2, c2)):
        board = move_in(board, moves)
        score = final_score(board, moves, opponent_pos, max_step)
        if score > max_vale:
            max_vale = score
    return max_vale


def minimax_layer1_2(board, original_position, opponent_pos, max_step):
    min_val = 1000
    r1, c1, d1 = original_position
    r2, c2, d2 = opponent_pos
    score = min_val
    for moves in all_valid_moves(board, (r2, c2), max_step, (r1, c1)):
        board = move_in(board, moves)
        score = final_score(board, original_position, moves, max_step)
        if score < min_val:
            min_val = score

    return min_val


def minimax_layer1(board, original_position, opponent_pos, max_step):
    min_val = 1000
    r1, c1, d1 = original_position
    r2, c2, d2 = opponent_pos
    score = min_val
    for moves in all_valid_moves(board, (r2, c2), max_step, (r1, c1)):
        board = move_in(board, moves)
        if check_endgame(board, moves, opponent_pos):
            score = final_score(board, original_position, moves, max_step)
        else:
            score = minimax_layer2(board, original_position, moves, max_step)
        if score < min_val:
            min_val = score

    return min_val


def get_best_move(board, original_position, opponent_pos, max_step):
    max_value = -1000
    list_best_moves = []
    r1, c1, d1 = original_position
    r2, c2, d2 = opponent_pos

    value = max_value
    for moves in all_valid_moves(board, (r1, c1), max_step, (r2, c2)):
        board = move_in(board, moves)
        if check_endgame(board, moves, opponent_pos):
            value = final_score(board, moves, opponent_pos, max_step)
        else:
            value = minimax_layer1_2(board, moves, opponent_pos, max_step)
        if value > max_value:
            max_value = value
            list_best_moves.clear()
            list_best_moves.append(moves)

        if value == max_value:
            list_best_moves.append(moves)

    a = 0
    if len(list_best_moves) > 1:
        length_list = len(list_best_moves)
        a = np.random.randint(0, length_list)

    return list_best_moves[a]


@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """

        r1, c1 = my_pos
        r2, c2 = adv_pos

        original_pos = (r1, c1, 0)
        opponent_pos = (r2, c2, 0)

        list_best_moves = get_best_move(chess_board, original_pos, opponent_pos, max_step)

        r, c, dr = list_best_moves

        return (r, c), dr
