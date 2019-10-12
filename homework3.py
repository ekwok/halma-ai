import math


class Node:
    def __init__(self, state, val, parent):
        self.state = state  # State of the board as a 2D matrix
        self.val = val  # Value given by the evaluation function
        self.parent = parent  # Parent node


def get_positions(piece, board):
    res = []
    for i in range(16):
        for j in range(16):
            if board[i][j] == piece:
                res.append((i, j))
    return res


def eval_func(piece, positions):
    if piece == 'W':
        corner = 0, 0
    else:
        corner = 15, 15

    res = 0
    for pos in positions:
        res -= math.sqrt((pos[0]-corner[0])**2 + (pos[1]-corner[1])**2)  # Euclidean distance from pos to corner

    return res  # Negated sum of distances from all pieces to opponent's corner


def is_in_board(pos):
    if 0 <= pos[0] < 16 and 0 <= pos[1] < 16:
        return True
    return False


def get_valid_moves(pos, board, visited, valid_moves):
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # Eight possible moves
    for m in moves:
        new_pos = pos[0] + m[0], pos[1] + m[1]
        if not is_in_board(new_pos):
            return valid_moves
        if board[new_pos[0]][new_pos[1]] != '.' and is_in_board((new_pos[0]+m[0], new_pos[1]+m[1])) and \
                board[new_pos[0]+m[0]][new_pos[1]+m[1]] == '.':
            new_pos = new_pos[0] + m[0], new_pos[1] + m[1]
            valid_moves.append(('J', pos, new_pos))  # Make a jump
        else:
            valid_moves.append(('E', pos, new_pos))  # Move to adjacent empty location


def single(color, time, board):
    piece = color[0]  # 'W' for WHITE and 'B' for BLACK

    positions = get_positions(piece, board)
    best_val = float('-inf')

    for pos in positions:
        valid_moves = get_valid_moves(pos, board, [pos], [])

    return []


def game(color, time, board):
    return []


def main():
    with open('input.txt') as infile:
        mode = infile.readline().strip()
        color = infile.readline().strip()
        time = float(infile.readline().strip())
        board = []
        for i in range(16):
            board.append(list(infile.readline().strip()))

    if mode == 'SINGLE':
        results = single(color, time, board)
    else:
        results = game(color, time, board)

    # print('mode:', mode)
    # print('color:', color)
    # print('time:', time)
    # for row in board:
    #     print(row)


if __name__ == '__main__':
    main()
