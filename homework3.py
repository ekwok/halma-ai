import math


class Node:
    def __init__(self, state, val, parent):
        self.state = state  # State of the board as a 2D matrix
        self.val = val  # Value given by the evaluation function
        self.parent = parent  # Parent node


def getPositions(piece, board):
    res = []
    for i in range(16):
        for j in range(16):
            if board[i][j] == piece:
                res.append((i, j))
    return res


def evalFunc(piece, positions):
    if piece == 'W':
        corner = 0, 0
    else:
        corner = 15, 15

    res = 0
    for pos in positions:
        res -= math.sqrt((pos[0]-corner[0])**2 + (pos[1]-corner[1])**2)  # Euclidean distance from pos to corner

    return res  # Negated sum of distances from all pieces to opponent's corner


def single(color, time, board):
    piece = color[0]  # 'W' for WHITE and 'B' for BLACK

    positions = getPositions(piece, board)
    searchTree = Node(board, evalFunc(piece, positions), None)
    print(searchTree.val)

    return []


def game(color, time, board):
    return []


def main():
    with open('input.txt') as infile:
        TYPE = infile.readline().strip()
        COLOR = infile.readline().strip()
        TIME = float(infile.readline().strip())
        BOARD = []
        for i in range(16):
            BOARD.append(list(infile.readline().strip()))

    if TYPE == 'SINGLE':
        results = single(COLOR, TIME, BOARD)
    else:
        results = game(COLOR, TIME, BOARD)

    # print('TYPE:', TYPE)
    # print('COLOR:', COLOR)
    # print('TIME:', TIME)
    # for row in BOARD:
    #     print(row)


if __name__ == '__main__':
    main()
