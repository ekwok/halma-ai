import math
import time

WHITE_CAMP = [
    (11, 14), (11, 15),
    (12, 13), (12, 14), (12, 15),
    (13, 12), (13, 13), (13, 14), (13, 15),
    (14, 11), (14, 12), (14, 13), (14, 14), (14, 15),
    (15, 11), (15, 12), (15, 13), (15, 14), (15, 15)
]

BLACK_CAMP = [
    (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
    (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
    (2, 0), (2, 1), (2, 2), (2, 3),
    (3, 0), (3, 1), (3, 2),
    (4, 0), (4, 1)
]


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


def eval_func(piece, board):
    if piece == 'W':
        corner = 0, 0
    else:
        corner = 15, 15

    res = 0
    for i in range(16):
        for j in range(16):
            if board[i][j] == piece:
                res -= math.sqrt((i-corner[0])**2 + (j-corner[1])**2)  # Euclidean distance from piece to corner

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
        move_seq = [(en.move, en.coord)]
        node = en.parent
        while node:
            move_seq = [(node.move, node.coord)] + move_seq
            node = node.parent
        res.append(move_seq)
    return res


def not_move_back_in_camp(move_seq, camp):
    if move_seq[0][1] not in camp and move_seq[-1][1] in camp:
        return False
    return True


def has_piece_in_own_camp(positions, camp):
    for p in positions:
        if p in camp:
            return True
    return False


def move_out_of_camp(move_seq, camp):
    if move_seq[0][1] in camp and move_seq[-1][1] not in camp:
        return True
    return False


def move_away_from_corner(move_seq, camp, camp_corner):
    start, end = move_seq[0][1], move_seq[-1][1]
    if start in camp and math.sqrt((end[0]-camp_corner[0])**2 + (end[1]-camp_corner[1])**2) > \
            math.sqrt((start[0]-camp_corner[0])**2 + (start[1]-camp_corner[1])**2):
        return True
    return False


def initial_config(opp_piece, opp_camp, board):
    for coord in opp_camp:
        if board[coord[0]][coord[1]] != opp_piece:
            return False
    return True


def won_game(piece, board):
    if piece == 'W':
        opp_piece = 'B'
        opp_camp = BLACK_CAMP
    else:
        opp_piece = 'W'
        opp_camp = WHITE_CAMP

    if initial_config(opp_piece, opp_camp, board):
        return False

    for coord in opp_camp:
        if board[coord[0]][coord[1]] == '.':
            return False

    return True


def not_leave_opp_camp(move_seq, piece):
    if piece == 'W':
        opp_camp = BLACK_CAMP
    else:
        opp_camp = WHITE_CAMP

    if move_seq[0][1] in opp_camp and move_seq[-1][1] not in opp_camp:
        return False
    return True


def get_final_move_seqs(piece, board, camp, camp_corner):
    positions = get_positions(piece, board)
    move_seqs = []  # List of possible move sequences
    for pos in positions:
        end_nodes = get_end_nodes(pos, board)  # List of end nodes for backtracking
        move_seqs.extend(get_move_seqs(end_nodes))

    move_seqs = list(filter(lambda x: not_leave_opp_camp(x, piece), move_seqs))  # Cannot leave opposing camp
    move_seqs = list(filter(lambda x: not_move_back_in_camp(x, camp), move_seqs))  # Rule 1a of addendum
    if has_piece_in_own_camp(positions, camp):  # Rule 1b of addendum
        final_move_seqs = list(filter(lambda x: move_out_of_camp(x, camp), move_seqs))  # Alt. 1
        if not final_move_seqs:  # Alt. 1 not possible
            final_move_seqs = list(filter(lambda x: move_away_from_corner(x, camp, camp_corner), move_seqs))  # Alt. 2
            if not final_move_seqs:  # Alt. 2 not possible
                final_move_seqs = move_seqs
    else:
        final_move_seqs = move_seqs

    return final_move_seqs


def minimax(nodes, depth, board, is_max, piece, alpha, beta):
    score = eval_func(piece, board)

    if piece == 'W':
        camp = WHITE_CAMP
        camp_corner = 15, 15
        opp_piece = 'B'
    else:
        camp = BLACK_CAMP
        camp_corner = 0, 0
        opp_piece = 'W'

    if depth == 4 or won_game(piece, board):
        return nodes, score

    if is_max:
        max_score = float('-inf')
        final_move_seqs = get_final_move_seqs(piece, board, camp, camp_corner)
        total_nodes = len(final_move_seqs)
        for fms in final_move_seqs:
            start = fms[0][1]
            end = fms[-1][1]

            # Make the move
            board[start[0]][start[1]] = '.'
            board[end[0]][end[1]] = opp_piece

            # Compute evaluation function for this move
            res = minimax(nodes, depth+1, board, not is_max, opp_piece, alpha, beta)
            total_nodes += res[0]
            max_score = max(max_score, res[1])

            # Undo the move
            board[start[0]][start[1]] = opp_piece
            board[end[0]][end[1]] = '.'

            if max_score >= beta:
                return total_nodes, max_score
            alpha = max(alpha, max_score)

        return total_nodes, max_score
    else:
        min_score = float('inf')
        final_move_seqs = get_final_move_seqs(piece, board, camp, camp_corner)
        total_nodes = len(final_move_seqs)
        for fms in final_move_seqs:
            start = fms[0][1]
            end = fms[-1][1]

            # Make the move
            board[start[0]][start[1]] = '.'
            board[end[0]][end[1]] = opp_piece

            # Compute evaluation function for this move
            res = minimax(nodes, depth+1, board, not is_max, opp_piece, alpha, beta)
            total_nodes += res[0]
            min_score = min(min_score, res[1])

            # Undo the move
            board[start[0]][start[1]] = opp_piece
            board[end[0]][end[1]] = '.'

            if min_score <= alpha:
                return total_nodes, min_score
            beta = min(beta, min_score)

        return total_nodes, min_score


def single(color, time_rem, board, start_time):
    piece = color[0]  # 'W' for WHITE and 'B' for BLACK

    if piece == 'W':
        camp = WHITE_CAMP
        camp_corner = 15, 15
    else:
        camp = BLACK_CAMP
        camp_corner = 0, 0

    final_move_seqs = get_final_move_seqs(piece, board, camp, camp_corner)

    best_val = float('-inf')
    best_move_seq = []
    total_nodes = 0
    for fms in final_move_seqs:
        start = fms[0][1]
        end = fms[-1][1]

        # Make the move
        board[start[0]][start[1]] = '.'
        board[end[0]][end[1]] = piece

        # Compute evaluation function for this move
        res = minimax(0, 0, board, False, piece, float('-inf'), float('inf'))

        total_nodes += res[0]
        val = res[1]

        print('fms:', fms)
        print('val:', val)
        print()

        # Undo the move
        board[start[0]][start[1]] = piece
        board[end[0]][end[1]] = '.'

        if val > best_val:
            best_val = val
            best_move_seq = fms

    print('best_move_seq:', best_move_seq)
    return total_nodes


def main():
    start_time = time.time()
    with open('input.txt') as infile:
        mode = infile.readline().strip()
        color = infile.readline().strip()
        time_rem = float(infile.readline().strip())
        board = []
        for i in range(16):
            board.append(list(infile.readline().strip()))

    total_nodes = single(color, time_rem, board, start_time)

    with open('calibration.txt', 'w') as outfile:
        outfile.write(str(total_nodes))

    print('Time taken:', time.time() - start_time)


if __name__ == '__main__':
    main()
