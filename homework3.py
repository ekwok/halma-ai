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


def get_empty_camp(opp_camp, board):
    empty = []
    for pos in opp_camp:
        if board[pos[0]][pos[1]] == '.':
            empty.append(pos)
    return empty


# Calculates [(Negated sum of distances from all pieces to opponent's corner) + (Credit for reaching opponent's camp)]
def eval_func(piece, board):
    if piece == 'W':
        opp_camp = BLACK_CAMP
        opp_corner = 0, 0
    else:
        opp_camp = WHITE_CAMP
        opp_corner = 15, 15

    empty = get_empty_camp(opp_camp, board)  # List of empty positions in opponent's camp

    res = 0
    for i in range(16):
        for j in range(16):
            if board[i][j] == piece and (i, j) not in opp_camp:
                res -= math.sqrt((i-opp_corner[0])**2 + (j-opp_corner[1])**2)  # Euclidean distance to opp_corner
                for pos in empty:
                    res -= math.sqrt((i-pos[0])**2 + (j-pos[1])**2)  # Euclidean dist. to empty positions in opp_camp
                # if (i, j) in opp_camp:
                #     res += 1  # Give credit to pieces that made it to opponent's camp
                # else:
                #     res -= 1  # Penalize pieces not in opponent's camp

    return res


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
            continue
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


def not_leave_opp_camp(move_seq, piece):
    if piece == 'W':
        opp_camp = BLACK_CAMP
    else:
        opp_camp = WHITE_CAMP

    if move_seq[0][1] in opp_camp and move_seq[-1][1] not in opp_camp:
        return False
    return True


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


def move_away_from_corner_in_camp(move_seq, camp, piece):
    start, end = move_seq[0][1], move_seq[-1][1]
    if start in camp:
        if piece == 'B' and (end[0] <= start[0] or end[1] <= start[1]):  # Do not move closer to corner (0, 0)
            return False
        elif piece == 'W' and (end[0] >= start[0] or end[1] >= start[1]):  # Do not move closer to corner (15, 15)
            return False
        return True
    return False


def not_in_camp(move_seq, camp, piece):
    start, end = move_seq[0][1], move_seq[-1][1]
    if start not in camp:
        if piece == 'B' and (end[0] <= start[0] or end[1] <= start[1]):  # Do not move closer to corner (0, 0)
            return False
        elif piece == 'W' and (end[0] >= start[0] or end[1] >= start[1]):  # Do not move closer to corner (15, 15)
            return False
        return True
    return False


def move_away_from_corner(move_seq, piece):
    start, end = move_seq[0][1], move_seq[-1][1]
    if piece == 'B' and (end[0] <= start[0] or end[1] <= start[1]):  # Do not move closer to corner (0, 0)
        return False
    elif piece == 'W' and (end[0] >= start[0] or end[1] >= start[1]):  # Do not move closer to corner (15, 15)
        return False
    return True


def get_final_move_seqs(piece, board, camp):
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
            final_move_seqs = list(filter(lambda x: move_away_from_corner_in_camp(x, camp, piece), move_seqs))  # Alt. 2
            if not final_move_seqs:  # Alt. 2 not possible (so move piece outside of camp)
                final_move_seqs = list(filter(lambda x: not_in_camp(x, camp, piece), move_seqs))
    else:
        final_move_seqs = list(filter(lambda x: move_away_from_corner(x, piece), move_seqs))

    if not final_move_seqs:
        return move_seqs

    return final_move_seqs


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


def minimax(depth, board, is_max, piece, alpha, beta, max_depth):
    score = eval_func(piece, board)

    if piece == 'W':
        camp = WHITE_CAMP
        opp_piece = 'B'
    else:
        camp = BLACK_CAMP
        opp_piece = 'W'

    if won_game(piece, board) or depth == max_depth:
        return score, []

    if is_max:
        max_score = float('-inf')
        final_move_seqs = get_final_move_seqs(piece, board, camp)
        best_move_seq = []
        for fms in final_move_seqs:
            start = fms[0][1]
            end = fms[-1][1]

            # Make the move
            board[start[0]][start[1]] = '.'
            board[end[0]][end[1]] = piece

            # Compute evaluation function for this move
            val, move_seq = minimax(depth+1, board, False, piece, alpha, beta, max_depth)

            # Undo the move
            board[start[0]][start[1]] = piece
            board[end[0]][end[1]] = '.'

            if val > max_score:
                max_score = val
                best_move_seq = fms

            if max_score >= beta:
                return max_score, best_move_seq
            alpha = max(alpha, max_score)

        return max_score, best_move_seq
    else:
        min_score = float('inf')
        final_move_seqs = get_final_move_seqs(opp_piece, board, camp)
        best_move_seq = []
        for fms in final_move_seqs:
            start = fms[0][1]
            end = fms[-1][1]

            # Make the move
            board[start[0]][start[1]] = '.'
            board[end[0]][end[1]] = opp_piece

            # Compute evaluation function for this move
            val, move_seq = minimax(depth+1, board, True, piece, alpha, beta, max_depth)

            # Undo the move
            board[start[0]][start[1]] = opp_piece
            board[end[0]][end[1]] = '.'

            if val < min_score:
                min_score = val
                best_move_seq = fms

            if min_score <= alpha:
                return min_score, best_move_seq
            beta = min(beta, min_score)

        return min_score, best_move_seq


def print_board(board):
    for row in board:
        print(row)


def write_board(mode, color, time_left, board):
    with open('board.txt', 'w') as outfile:
        outfile.write(mode + '\n')
        outfile.write(color + '\n')
        outfile.write(str(time_left) + '\n')
        for row in board:
            outfile.write(''.join(row) + '\n')


def main():
    with open('vocareum_inputs/input6.txt') as infile:
        mode = infile.readline().strip()
        color = infile.readline().strip()
        time_given = float(infile.readline().strip())
        board = []
        for i in range(16):
            board.append(list(infile.readline().strip()))

    # score, results = minimax(0, board, True, color[0], float('-inf'), float('inf'), 1)

    min_time = float('inf')
    max_time = float('-inf')

    piece = 'W'
    white_counter, black_counter = 1, 1
    white_moves_so_far, black_moves_so_far = 0, 0
    white_time, black_time = 600.0, 600.0
    while white_time > 0 and black_time > 0:
        if piece == 'W':
            write_board('GAME', 'WHITE', white_time, board)
            print('Moves so far: ' + str(white_moves_so_far))
            white_moves_so_far += 1
        else:
            write_board('GAME', 'BLACK', black_time, board)
            print('Moves so far: ' + str(black_moves_so_far))
            black_moves_so_far += 1

        max_depth = 1
        print('Max depth: ' + str(max_depth))

        begin = time.time()
        if won_game('W', board):
            print('White won!')
            break
        if won_game('B', board):
            print('Black won!')
            break
        score, results = minimax(0, board, True, piece, float('-inf'), float('inf'), max_depth)
        if results:
            start, end = results[0][1], results[-1][1]
            board[start[0]][start[1]] = '.'
            board[end[0]][end[1]] = piece
        if piece == 'W':
            print('W ' + str(white_counter))
            white_counter += 1
        else:
            print('B ' + str(black_counter))
            black_counter += 1
        print_board(board)
        time_taken = time.time() - begin
        print('Time taken: ' + str(time_taken))
        print()
        if time_taken < min_time:
            min_time = time_taken
        elif time_taken > max_time:
            max_time = time_taken

        if piece == 'W':
            white_time -= time_taken
            piece = 'B'
        else:
            black_time -= time_taken
            piece = 'W'

    print('Min time: ' + str(min_time))
    print('Max time: ' + str(max_time))

    if white_time <= 0:
        print('White lost!')
    elif black_time <= 0:
        print('Black lost!')

    # with open('output.txt', 'w') as outfile:
    #     start = results[0][1]
    #     for i in range(1, len(results)):
    #         move = results[i][0]
    #         end = results[i][1]
    #         outfile.write(move + ' ' + str(start[1]) + ',' + str(start[0]) + ' ' + str(end[1]) + ',' + str(end[0]))
    #         if i < len(results) - 1:
    #             outfile.write('\n')
    #         start = end


if __name__ == '__main__':
    main()
