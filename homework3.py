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


def get_end_nodes(pos, board):
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


def get_move_seqs(end_nodes):
    res = []
    for en in end_nodes:
        move_seq = [en.coord]
        node = en
        while node.parent:
            move_seq = [node.parent.coord] + move_seq
            node = node.parent
        res.append(move_seq)
    return res


def move_back_in_camp(move_seq, camp):
    if move_seq[0] not in camp and move_seq[-1] in camp:
        return False
    return True


def has_piece_in_own_camp(positions, camp):
    for p in positions:
        if p in camp:
            return True
    return False


def move_out_of_camp(move_seq, camp):
    if move_seq[0] in camp and move_seq[-1] not in camp:
        return True
    return False


def move_away_from_corner(move_seq, camp, camp_corner):
    start, end = move_seq[0], move_seq[-1]
    if start in camp and math.sqrt((end[0]-camp_corner[0])**2 + (end[1]-camp_corner[1])**2) > \
            math.sqrt((start[0]-camp_corner[0])**2 + (start[1]-camp_corner[1])**2):
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
    move_seqs = []  # List of possible move sequences
    for pos in positions:
        end_nodes = get_end_nodes(pos, board)  # List of end nodes for backtracking
        move_seqs.extend(get_move_seqs(end_nodes))

    move_seqs = list(filter(lambda x: move_back_in_camp(x, camp), move_seqs))  # Rule 1a of addendum
    if has_piece_in_own_camp(positions, camp):  # Rule 1b of addendum
        final_move_seqs = list(filter(lambda x: move_out_of_camp(x, camp), move_seqs))  # Alt. 1
        if not final_move_seqs:  # Alt. 1 not possible
            final_move_seqs = list(filter(lambda x: move_away_from_corner(x, camp, camp_corner), move_seqs))  # Alt. 2
            if not final_move_seqs:  # Alt. 2 not possible
                final_move_seqs = move_seqs
    else:
        final_move_seqs = move_seqs

    best_val = float('-inf')
    for fms in final_move_seqs:
        print(fms)
    print()

    return []


def game(color, time, board):
    return []


def main():
    with open('input4.txt') as infile:
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
