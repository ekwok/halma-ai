import math


class MoveNode(object):
    def __init__(self, move, coord, parent):
        self.move = move  # Type of move ('E' for 'empty' or 'J' for 'jump')
        self.coord = coord  # Coordinate at end of move
        self.parent = parent  # Parent node (contains coordinate at start of move)


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


def add_jumps(start, board, visited, end_nodes):
    jumps = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]  # Eight possible jumps
    pos = start.coord
    for j in jumps:
        new_pos = pos[0] + j[0], pos[1] + j[1]
        if not is_in_board(new_pos):
            return
        if board[pos[0]+int(j[0]/2)][pos[1]+int(j[1]/2)] != '.' and board[new_pos[0]][new_pos[1]] == '.' and \
                new_pos not in visited:
            child = MoveNode('J', new_pos, start)  # Make a jump
            end_nodes.append(child)
            add_jumps(child, board, visited+[new_pos], end_nodes)


def get_valid_moves(pos, board):
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]  # Eight possible directions
    root = MoveNode(None, pos, None)  # All possible moves organized in a tree
    end_nodes = []  # List of nodes containing ending coordinates of possible moves (used for backtracking)
    for d in directions:
        new_pos = pos[0] + d[0], pos[1] + d[1]
        if not is_in_board(new_pos):
            continue
        elif board[new_pos[0]][new_pos[1]] == '.':
            child = MoveNode('E', new_pos, root)  # Move to adjacent empty location
            end_nodes.append(child)
        elif is_in_board((new_pos[0]+d[0], new_pos[1]+d[1])) and board[new_pos[0]+d[0]][new_pos[1]+d[1]] == '.':
            child = MoveNode('J', (new_pos[0]+d[0], new_pos[1]+d[1]), root)  # Make a jump
            end_nodes.append(child)
            visited = [pos, child.coord]  # List of visited coordinates for loop detection
            add_jumps(child, board, visited, end_nodes)  # Find additional jumps
    return end_nodes


def get_move_seq(end_node):
    move_seq = [end_node.coord]
    node = end_node
    while node.parent:
        move_seq = [node.parent.coord] + move_seq
        node = node.parent
    return move_seq


def has_piece_in_own_camp(positions, camp):
    for p in positions:
        if p in camp:
            return True
    return False


def is_first_possible(valid_moves, camp):
    for move in valid_moves:
        move_seq = get_move_seq(move)
        if move_seq[0] in camp and move_seq[-1] not in camp:  # First possibility of Rule 1b
            return True
    return False


def single(color, time, board):
    piece = color[0]  # 'W' for WHITE and 'B' for BLACK

    if piece == 'W':
        camp = [
            (11, 14), (11, 15),
            (12, 13), (12, 14), (12, 15),
            (13, 12), (13, 13), (13, 14), (13, 15),
            (14, 11), (14, 12), (14, 13), (14, 14), (14, 15),
            (15, 11), (15, 12), (15, 13), (15, 14), (15, 15)
        ]
        camp_corner = 15, 15
    else:
        camp = [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 0), (2, 1), (2, 2), (2, 3),
            (3, 0), (3, 1), (3, 2),
            (4, 0), (4, 1)
        ]
        camp_corner = 0, 0

    positions = get_positions(piece, board)
    best_val = float('-inf')

    for pos in positions:
        valid_moves = get_valid_moves(pos, board)
        print('pos:', pos)
        print('valid_moves:')
        first_possible = is_first_possible(valid_moves, camp)
        for move in valid_moves:
            move_seq = get_move_seq(move)
            if move_seq[0] not in camp and move_seq[-1] in camp:  # Rule 1a of addendum
                continue
            if has_piece_in_own_camp(positions, camp):  # Rule 1b of addendum
                if first_possible and (move_seq[0] not in camp or (move_seq[0] in camp and move_seq[-1] in camp)):
                    continue
            print(move_seq)
        print()

    return []


def game(color, time, board):
    return []


def main():
    with open('input3.txt') as infile:
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
