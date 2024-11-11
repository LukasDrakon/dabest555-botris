import asyncio
import websockets
import json
import time
from collections import deque

secret_token = ''
master_key = ''

i_piece = [
    [[1, 1, 1, 1]],
    [[1],
     [1],
     [1],
     [1]]
]

j_piece = [
    [[1, 0, 0],
     [1, 1, 1]],
    
    [[1, 1],
     [1, 0],
     [1, 0]],
    
    [[1, 1, 1],
     [0, 0, 1]],
    
    [[0, 1],
     [0, 1],
     [1, 1]]
]

l_piece = [
    [[0, 0, 1],
     [1, 1, 1]],
    
    [[1, 0],
     [1, 0],
     [1, 1]],
    
    [[1, 1, 1],
     [1, 0, 0]],
    
    [[1, 1],
     [0, 1],
     [0, 1]]
]

o_piece = [
    [[1, 1],
     [1, 1]]
]

s_piece = [
    [[0, 1, 1],
     [1, 1, 0]],
    
    [[1, 0],
     [1, 1],
     [0, 1]]
]

t_piece = [
    [[0, 1, 0],
     [1, 1, 1]],
    
    [[1, 0],
     [1, 1],
     [1, 0]],
    
    [[1, 1, 1],
     [0, 1, 0]],
    
    [[0, 1],
     [1, 1],
     [0, 1]]
]

z_piece = [
    [[1, 1, 0],
     [0, 1, 1]],
    
    [[0, 1],
     [1, 1],
     [1, 0]]
]

piece_map = {
    'I': i_piece,
    'J': j_piece,
    'L': l_piece,
    'O': o_piece,
    'S': s_piece,
    'T': t_piece,
    'Z': z_piece,
    None : None
}

lines_map = {
    0: 'none',
    1: 'single',
    2: 'double',
    3: 'triple',
    4: 'quad'
}

clear_map = {
    'none': 0,
    'single': 1,
    'double': 3,
    'triple': 5,
    'quad': 8
}



def simulate_drop(board, piece, x):
    piece_height, piece_width = len(piece), len(piece[0])
    board_height = 20
    # Find the lowest y position the piece can go without collision
    lowest_y = -1
    for y in range(20 - len([row for row in board if any(row)]) - piece_height, board_height - piece_height + 1):
        collision = False
        for py in range(piece_height):
            for px in range(piece_width):
                if piece[py][px] == 1 and board[y + py][x + px] == 1:
                    collision = True
                    break
            if collision:
                break
        if collision:
            break
        lowest_y = y

    # Place the piece if it is within the board and no collision occurred
    if lowest_y == -1:
        return None  # Invalid position

    new_board = [row[:] for row in board]
    for py in range(piece_height):
        for px in range(piece_width):
            if piece[py][px] == 1:
                new_board[lowest_y + py][x + px] = 1

    return new_board

def generate_all_moves(board, piece):
    board_width = 10
    moves = []

    for rotation_index, rotation in enumerate(piece):
        piece_width = len(rotation[0])
        for x in range(board_width - piece_width + 1):
            new_board = simulate_drop(board, rotation, x)
            if new_board is not None:
                moves.append((new_board, rotation_index, x))
            else:
                break

    return moves




def clear_full_lines(board):
    new_board = []
    lines_cleared = 0

    for row in board:
        if all(cell == 1 for cell in row):
            lines_cleared += 1
        else:
            new_board.append(row)

    new_board = [[0] * 10] * lines_cleared + new_board
    if all(cell == 0 for cell in new_board[-1]):
        lines_cleared += 35
    return new_board, lines_cleared



def column_heights(board):
    board = [row for row in board if any(row)]
    rows = len(board)
    heights = [0] * 10  
    
    for x in range(10):
        for y in range(rows):
            if board[y][x] == 1:
                heights[x] = rows - y
                break
    return heights


def holes_strict(board, heights):
    regular_holes = 0
    strict_holes = 0
    max_height = max(x for x in heights)

    for y in range(max_height):
        for x in range(10):
            if board[y][x] == 1 or y >= heights[x]:
                continue
            if x > 1:
                if heights[x-1] <= y - 1 and heights[x-2] <= y:
                    regular_holes += 1
                    continue

            if x < 8:
                if heights[x+1] <= y - 1 and heights[x+2] <= y:
                    regular_holes += 1
                    continue

            strict_holes += 1

    return regular_holes, strict_holes




def calculate_heuristic(board, lines):
    heights = column_heights(board)
    aggregate_height = sum(x for x in heights)
    max_height = max(x for x in heights)
    holes, strict_holes = holes_strict(board, heights)
    bumpiness = -1
    bumpiness_sq = -1
    previous_height = -1
    lines_cleared = lines
    previous_height = heights[0]
    for x in range(10):
        
    
        column_height = heights[x]
        dh = abs(column_height - previous_height)

        if previous_height != -1:
            bumpiness += dh
            bumpiness_sq += dh * dh


        previous_height = column_height

    #print(f"agg height:{aggregate_height}, max height:{max_height}, holes:{holes}, strict holes:{strict_holes}, bumpiness:{bumpiness}, lines cleared:{lines_cleared}")
    weight_aggregate_height = -1.5
    weight_max_height = -2.0
    weight_holes = -3.0
    weight_strict_holes = -2.5
    weight_bumpiness = -0.5
    weight_bumpiness_sq = -0.1
    weight_lines_cleared = 2.0
    

    score = (weight_aggregate_height * aggregate_height +
             weight_max_height * (2 ** max_height) +
             weight_holes * holes +
             weight_bumpiness * bumpiness +
             weight_bumpiness_sq * bumpiness_sq +
             weight_strict_holes * strict_holes +
             weight_lines_cleared * lines_cleared)

    return score




def move_piece(current_piece, held_piece, rotation, x, hold):
    
    if hold:
        moves = ['hold',]
        piece = held_piece
    else:
        moves = []
        piece = current_piece
    if piece in ('T', 'J', 'L'):      
        if rotation == 0:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left'])
            elif x == 1:
                moves.extend(['move_left', 'move_left'])
            elif x == 2:
                moves.extend(['move_left'])
            elif x == 3:
                moves.extend(['none'])
            elif x == 4:
                moves.extend(['move_right'])
            elif x == 5:
                moves.extend(['move_right', 'move_right'])
            elif x == 6:
                moves.extend(['move_right', 'move_right', 'move_right'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right'])
        elif rotation == 1:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left', 'rotate_cw', 'move_left'])
            elif x == 1:
                moves.extend(['move_left', 'move_left', 'move_left', 'rotate_cw'])
            elif x == 2:
                moves.extend(['move_left', 'move_left', 'rotate_cw'])
            elif x == 3:
                moves.extend(['move_left', 'rotate_cw'])
            elif x == 4:
                moves.extend(['rotate_cw'])
            elif x == 5:
                moves.extend(['move_right', 'rotate_cw'])
            elif x == 6:
                moves.extend(['move_right', 'move_right', 'rotate_cw'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'move_right', 'rotate_cw'])
            elif x == 8:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right', 'rotate_cw'])
        elif rotation == 2:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left', 'rotate_cw', 'rotate_cw'])
            elif x == 1:
                moves.extend(['move_left', 'move_left', 'rotate_cw', 'rotate_cw'])
            elif x == 2:
                moves.extend(['move_left', 'rotate_cw', 'rotate_cw'])
            elif x == 3:
                moves.extend(['rotate_cw', 'rotate_cw'])
            elif x == 4:
                moves.extend(['move_right', 'rotate_cw', 'rotate_cw'])
            elif x == 5:
                moves.extend(['move_right', 'move_right', 'rotate_cw', 'rotate_cw'])
            elif x == 6:
                moves.extend(['move_right', 'move_right', 'move_right', 'rotate_cw', 'rotate_cw'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right', 'rotate_cw', 'rotate_cw'])
        elif rotation == 3:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left', 'rotate_ccw'])
            elif x == 1:
                moves.extend(['move_left', 'move_left', 'rotate_ccw'])
            elif x == 2:
                moves.extend(['move_left', 'rotate_ccw'])
            elif x == 3:
                moves.extend(['rotate_ccw'])
            elif x == 4:
                moves.extend(['move_right', 'rotate_ccw'])
            elif x == 5:
                moves.extend(['move_right', 'move_right', 'rotate_ccw'])
            elif x == 6:
                moves.extend(['move_right', 'move_right', 'move_right', 'rotate_ccw'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right', 'rotate_ccw'])
            elif x == 8:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right', 'rotate_ccw', 'move_right'])
    
    elif piece in ('S', 'Z'):
        if rotation == 0:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left'])
            elif x == 1:
                moves.extend(['move_left', 'move_left'])
            elif x == 2:
                moves.extend(['move_left'])
            elif x == 3:
                moves.extend(['none'])
            elif x == 4:
                moves.extend(['move_right'])
            elif x == 5:
                moves.extend(['move_right', 'move_right'])
            elif x == 6:
                moves.extend(['move_right', 'move_right', 'move_right'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right'])
        elif rotation == 1:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left', 'rotate_ccw'])
            elif x == 1:
                moves.extend(['move_left', 'move_left', 'rotate_ccw'])
            elif x == 2:
                moves.extend(['move_left', 'rotate_ccw'])
            elif x == 3:
                moves.extend(['rotate_ccw'])
            elif x == 4:
                moves.extend(['rotate_cw'])
            elif x == 5:
                moves.extend(['move_right', 'rotate_cw'])
            elif x == 6:
                moves.extend(['move_right', 'move_right', 'rotate_cw'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'move_right', 'rotate_cw'])
            elif x == 8:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right', 'rotate_cw'])
            
    elif piece in ('I',):
        if rotation == 0:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left'])
            elif x == 1:
                moves.extend(['move_left', 'move_left'])
            elif x == 2:
                moves.extend(['move_left'])
            elif x == 3:
                moves.extend(['none'])
            elif x == 4:
                moves.extend(['move_right'])
            elif x == 5:
                moves.extend(['move_right', 'move_right'])
            elif x == 6:
                moves.extend(['move_right', 'move_right', 'move_right'])
        elif rotation == 1:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left', 'rotate_ccw', 'move_left'])
            elif x == 1:
                moves.extend(['move_left', 'move_left', 'move_left', 'rotate_ccw'])
            elif x == 2:
                moves.extend(['move_left', 'move_left', 'rotate_ccw'])
            elif x == 3:
                moves.extend(['move_left', 'rotate_ccw'])
            elif x == 4:
                moves.extend(['rotate_ccw'])
            elif x == 5:
                moves.extend(['rotate_cw'])
            elif x == 6:
                moves.extend(['move_right', 'rotate_cw'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'rotate_cw'])
            elif x == 8:
                moves.extend(['move_right', 'move_right', 'move_right', 'rotate_cw'])
            elif x == 9:
                moves.extend(['move_right', 'move_right', 'move_right', 'rotate_cw', 'move_right'])
    
    elif piece in ('O',):
        if rotation == 0:
            if x == 0:
                moves.extend(['move_left', 'move_left', 'move_left', 'move_left'])
            elif x == 1:
                moves.extend(['move_left', 'move_left', 'move_left'])
            elif x == 2:
                moves.extend(['move_left', 'move_left'])
            elif x == 3:
                moves.extend(['move_left'])
            elif x == 4:
                moves.extend(['none'])
            elif x == 5:
                moves.extend(['move_right'])
            elif x == 6:
                moves.extend(['move_right', 'move_right'])
            elif x == 7:
                moves.extend(['move_right', 'move_right', 'move_right'])
            elif x == 8:
                moves.extend(['move_right', 'move_right', 'move_right', 'move_right'])
        
    


    else:
        moves.extend(['move_right', 'rotate_ccw', 'rotate_ccw', 'rotate_ccw', 'rotate_ccw'])
    
    return moves


def bfs_best_move(board, piece, held_piece, max_depth, game_state):
    from functools import lru_cache

    # Memoize heuristic calculation
    @lru_cache(None)
    def memoized_heuristic(board_tuple, cumulative_lines):
        return calculate_heuristic(board_tuple, cumulative_lines)
    
    queue = deque([(board, piece, held_piece, 0, None, None, None, None, False, 0)])
    best_score = float('-inf')
    best_move = (0, 0)
    best_hold = False

    while queue:
        current_board, current_piece, current_held_piece, current_depth, initial_rotation, initial_x, current_rotation, current_x, hold_used, cumulative_lines = queue.popleft()
        
        if current_board != []:
            current_board, lines = clear_full_lines(current_board)
        else:
            lines = 0
        cumulative_lines += lines
        
        if current_depth == max_depth:
            board_tuple = tuple(map(tuple, current_board))
            score = memoized_heuristic(board_tuple, cumulative_lines)
            
            if score > best_score:
                best_score = score
                best_move = (initial_rotation, initial_x)
                best_hold = hold_used
            continue
        
        if current_board == []:
            all_moves = generate_all_moves([[0]*10 for _ in range(20)], current_piece)
        else:
            current_board.extend([[0]*10 for _ in range(20-len(current_board))])
            all_moves = generate_all_moves(current_board, current_piece)

        sorted_moves = sorted(all_moves, key=lambda move: memoized_heuristic(tuple(map(tuple, move[0])), cumulative_lines), reverse=True)
        
        pruned_moves = sorted_moves[:5]
        
        next_piece = piece_map.get(game_state['queue'][current_depth])
        
        for new_board, rotation_index, x in pruned_moves:
            if current_depth == 0:
                queue.append((new_board, next_piece, current_held_piece, current_depth + 1, rotation_index, x, rotation_index, x, hold_used, cumulative_lines))
            else:
                queue.append((new_board, next_piece, current_held_piece, current_depth + 1, initial_rotation, initial_x, rotation_index, x, hold_used, cumulative_lines))
        
        if current_held_piece:
            held_piece_moves = generate_all_moves(current_board, current_held_piece)
            sorted_moves = sorted(held_piece_moves, key=lambda move: memoized_heuristic(tuple(map(tuple, move[0])), cumulative_lines), reverse=True)
            pruned_moves = sorted_moves[:5]

            for new_board, rotation_index, x in pruned_moves:
                if current_depth == 0:
                    queue.append((new_board, next_piece, current_piece, current_depth + 1, rotation_index, x, rotation_index, x, True, cumulative_lines))
                else:
                    queue.append((new_board, next_piece, current_piece, current_depth + 1, initial_rotation, initial_x, rotation_index, x, hold_used, cumulative_lines))
        else:
            next_piece = piece_map.get(game_state['queue'][current_depth])
            queue.append((current_board, next_piece, current_piece, current_depth, initial_rotation, initial_x, None, None, True, cumulative_lines))

    return best_move, best_hold
piece_order = 0
bag5_queue = []
def bag1(game_state):
    if game_state['current']['piece'] == 'I':
        return ['rotate_cw', 'move_right', 'move_right', 'move_right', 'move_right']
    elif game_state['current']['piece'] == 'O':
        return ['move_right', 'sonic_drop', 'move_right']
    elif game_state['current']['piece'] == 'J':
        return ['rotate_ccw', 'move_right', 'sonic_drop', 'move_left',]
    elif game_state['current']['piece'] == 'S':
        if game_state['board'] != []: 
            if any(game_state['board'][i][0] == 'T' for i in range(len(game_state['board']))):
                return ['move_left', 'move_left', 'move_left', 'rotate_cw', 'sonic_drop', 'rotate_cw',]
            else:
                return ['move_left', 'move_left', 'move_left', 'rotate_cw', 'sonic_drop', 'rotate_cw', 'move_right']
        else:
            return ['move_left', 'move_left', 'move_left', 'rotate_cw', 'sonic_drop', 'rotate_cw', 'move_right']
    
        
    
            
            
    elif game_state['held'] == 'I':
        return ['hold', 'rotate_cw', 'move_right', 'move_right', 'move_right', 'move_right']
   
    elif game_state['held'] == 'O':
        return ['hold', 'move_right', 'sonic_drop', 'move_right']
    elif game_state['held'] == 'J':
        return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'move_left',]
    elif game_state['held'] == 'S':
        if any(game_state['board'][i][0] == 'T' for i in range(len(game_state['board']))):
            return ['hold', 'move_left', 'move_left', 'move_left', 'rotate_cw', 'sonic_drop', 'rotate_cw',]
        else:
            return ['hold', 'move_left', 'move_left', 'move_left', 'rotate_cw', 'sonic_drop', 'rotate_cw', 'move_right']
        
    
    elif game_state['current']['piece'] == 'L':
        return ['rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right']
    elif game_state['held'] == 'L':
        return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right']

    elif game_state['current']['piece'] == 'T':
        return ['rotate_cw', 'move_left', 'move_left', 'move_left', 'move_left']
    elif game_state['held'] == 'T':
        return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left', 'move_left']
        
    elif game_state['held'] == None:
        if game_state['queue'][0] == 'I':
            return ['hold', 'rotate_cw', 'move_right', 'move_right', 'move_right', 'move_right']
        elif game_state['queue'][0] == 'L':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right']
        elif game_state['queue'][0] == 'O':
            return ['hold', 'move_right', 'sonic_drop', 'move_right']
        elif game_state['queue'][0] == 'J':
            return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'move_left',]
        elif game_state['queue'][0] == 'S':
            if any(game_state['board'][i][0] == 'T' for i in range(len(game_state['board']))):
                return ['hold', 'move_left', 'move_left', 'move_left', 'rotate_cw', 'sonic_drop', 'rotate_cw',]
            else:
                return ['hold', 'move_left', 'move_left', 'move_left', 'rotate_cw', 'sonic_drop', 'rotate_cw', 'move_right']
        elif game_state['queue'][0] == 'T':
            return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left', 'move_left']
    else:
        return ['hold', 'move_left', 'move_left', 'move_left']


def bag2(game_state):
    if game_state['current']['piece'] == 'I':
        return ['rotate_cw']
    elif game_state['current']['piece'] == 'Z':
        return ['move_left', 'sonic_drop', 'rotate_cw']
    elif game_state['current']['piece'] == 'O':
        return ['move_left', 'move_left', 'move_left', 'move_left']
    elif game_state['current']['piece'] == 'J':
        return ['rotate_cw', 'move_right', 'move_right']
    elif game_state['current']['piece'] == 'S':
        return ['rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
    elif game_state['current']['piece'] == 'T':
        return ['move_left', 'move_left', 'rotate_cw']
        
    elif game_state['held'] == None:
        if game_state['queue'][0] == 'I':
            return ['hold', 'rotate_cw']
        elif game_state['queue'][0] == 'Z':
            return ['hold','move_left', 'sonic_drop', 'rotate_cw']
        elif game_state['queue'][0] == 'O':
            return ['hold', 'move_left', 'move_left', 'move_left', 'move_left']
        elif game_state['queue'][0] == 'J':
            return ['hold', 'rotate_cw', 'move_right', 'move_right']
        elif game_state['queue'][0] == 'S':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        elif game_state['queue'][0] == 'T':
            return ['hold', 'move_left', 'move_left', 'rotate_cw']
            
            
    elif game_state['held'] == 'I':
        return ['hold', 'rotate_cw']
    elif game_state['held'] == 'Z':
        return ['hold', 'move_left', 'sonic_drop', 'rotate_cw']
    elif game_state['held'] == 'O':
        return ['hold', 'move_left', 'move_left', 'move_left', 'move_left']
    elif game_state['held'] == 'J':
        return ['hold', 'rotate_cw', 'move_right', 'move_right']
    elif game_state['held'] == 'S':
        return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
    elif game_state['held'] == 'T':
        return ['hold', 'move_left', 'move_left', 'rotate_cw']
        
        
    else:
        return ['hold', 'move_right', 'move_right', 'move_right', 'move_right']


def bag3(game_state):
    
    if game_state['current']['piece'] == 'L':
        if sum(game_state['board'][i][7] == 'S' for i in range(len(game_state['board']))) > 1:
            return ['move_right', 'move_right', 'sonic_drop', 'rotate_cw', 'drop', 'drop', 'move_right']
        else:
            return ['move_right', 'move_right', 'rotate_cw']
    elif game_state['current']['piece'] == 'J':
        return ['move_left', 'rotate_ccw', 'sonic_drop', 'move_left']
    elif game_state['current']['piece'] == 'Z':
        return ['rotate_ccw', 'move_left', 'move_left', 'move_left']
    elif game_state['current']['piece'] == 'S': 
        if any(game_state['board'][i][9] == 'T' for i in range(len(game_state['board']))):
            return ['move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        else:
            return ['move_right', 'move_right', 'move_right', 'rotate_cw']
    elif game_state['current']['piece'] == 'T':
        return ['rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right']
        
    elif game_state['held'] == None:
        if game_state['queue'][0] == 'I':
            return ['hold', 'rotate_cw', 'move_left', 'sonic_drop', 'move_right', 'drop', 'rotate_cw']
        elif game_state['queue'][0] == 'L':
            if sum(game_state['board'][i][7] == 'S' for i in range(len(game_state['board']))) > 1:
                return ['hold', 'move_right', 'move_right', 'sonic_drop', 'rotate_cw', 'drop', 'drop', 'move_right']
            else:
                return ['hold', 'move_right', 'move_right', 'rotate_cw']
        elif game_state['queue'][0] == 'J':
            return ['hold', 'move_left', 'rotate_ccw', 'sonic_drop', 'move_left']
        elif game_state['queue'][0] == 'Z':
            return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left']
        elif game_state['queue'][0] == 'S':
            if any(game_state['board'][i][9] == 'T' for i in range(len(game_state['board']))):
                return ['hold', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            else:
                return ['hold', 'move_right', 'move_right', 'move_right', 'rotate_cw']
        elif game_state['queue'][0] == 'T':
            return['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right']
            
            
    
    elif game_state['held'] == 'L':
        if sum(game_state['board'][i][7] == 'S' for i in range(len(game_state['board']))) > 1:
            return ['hold', 'move_right', 'move_right', 'sonic_drop', 'rotate_cw', 'drop', 'drop', 'move_right']
        else:
            return ['hold', 'move_right', 'move_right', 'rotate_cw']
    elif game_state['held'] == 'J':
        return ['hold', 'move_left', 'rotate_ccw', 'sonic_drop', 'move_left']
    elif game_state['held'] == 'Z':
        return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left']
    elif game_state['held'] == 'S':
        if any(game_state['board'][i][9] == 'T' for i in range(len(game_state['board']))):
            return ['hold', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        else:
            return ['hold', 'move_right', 'move_right', 'move_right', 'rotate_cw']
    elif game_state['held'] == 'T':
        return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right']
        
    if game_state['current']['piece'] == 'I':
        return ['rotate_cw', 'move_left', 'sonic_drop', 'move_right', 'drop', 'rotate_cw']
    elif game_state['held'] == 'I':
        return ['hold', 'rotate_cw', 'move_left', 'sonic_drop', 'move_right', 'drop', 'rotate_cw']
    else:
        return ['hold', 'move_left']



def bag4(game_state):
    if game_state['current']['piece'] == 'O':
        return ['move_left', 'move_left']
    elif game_state['current']['piece'] == 'L':
        if sum(game_state['board'][i][7] == 'S' for i in range(len(game_state['board']))) > 2:
            return ['move_right', 'move_right', 'sonic_drop', 'rotate_cw', 'drop', 'drop', 'move_right']
        else:
            return ['move_right', 'move_right', 'rotate_cw']
    elif game_state['current']['piece'] == 'J':
        return ['move_right', 'rotate_ccw', 'sonic_drop', 'move_left']
    elif game_state['current']['piece'] == 'Z':
        return ['move_left', 'move_left', 'move_left', 'rotate_ccw']
    elif game_state['current']['piece'] == 'S': 
        if sum(game_state['board'][i][9] == 'T' for i in range(len(game_state['board']))) > 3:
            return ['move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        else:
            return ['move_right', 'move_right', 'move_right', 'rotate_cw']
    elif game_state['current']['piece'] == 'T':
        return ['move_right', 'move_right', 'move_right', 'move_right', 'rotate_ccw', 'move_right']
        
    elif game_state['held'] == None:
        if game_state['queue'][0] == 'O':
            return ['hold', 'move_left', 'move_left']
        elif game_state['queue'][0] == 'L':
            if sum(game_state['board'][i][7] == 'S' for i in range(len(game_state['board']))) > 2:
                return ['hold', 'move_right', 'move_right', 'sonic_drop', 'rotate_cw', 'drop', 'drop', 'move_right']
            else:
                return ['hold', 'move_right', 'move_right', 'rotate_cw']
        elif game_state['queue'][0] == 'J':
            return ['hold', 'move_right', 'rotate_ccw', 'sonic_drop', 'move_left']
        elif game_state['queue'][0] == 'Z':
            return ['hold', 'move_left', 'move_left', 'move_left', 'rotate_ccw']
        elif game_state['queue'][0] == 'S':
            if sum(game_state['board'][i][9] == 'T' for i in range(len(game_state['board']))) > 3:
                return ['hold', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            else:
                return ['hold', 'move_right', 'move_right', 'move_right', 'rotate_cw']
        elif game_state['queue'][0] == 'T':
            return['hold', 'move_right', 'move_right', 'move_right', 'move_right', 'rotate_ccw', 'move_right']
            
            
    elif game_state['held'] == 'O':
        return ['hold', 'move_left', 'move_left']
    elif game_state['held'] == 'L':
        if sum(game_state['board'][i][7] == 'S' for i in range(len(game_state['board']))) > 2:
            return ['hold', 'move_right', 'move_right', 'sonic_drop', 'rotate_cw', 'drop', 'drop', 'move_right']
        else:
            return ['hold', 'move_right', 'move_right', 'rotate_cw']
    elif game_state['held'] == 'J':
        return ['hold', 'move_right', 'rotate_ccw', 'sonic_drop', 'move_left']
    elif game_state['held'] == 'Z':
        return ['hold', 'move_left', 'move_left', 'move_left', 'rotate_ccw']
    elif game_state['held'] == 'S':
        if sum(game_state['board'][i][9] == 'T' for i in range(len(game_state['board']))) > 3:
            return ['hold', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        else:
            return ['hold', 'move_right', 'move_right', 'move_right', 'rotate_cw']
    elif game_state['held'] == 'T':
        return ['hold', 'move_right', 'move_right', 'move_right', 'move_right', 'rotate_ccw', 'move_right']
        
        
    else:
        return ['hold', 'rotate_cw']


def bag5(game_state):
    
        if game_state['current']['piece'] == 'I':
            return ['rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        
        elif game_state['held'] == 'O':
            return ['hold', 'move_left', 'move_left',]
        elif game_state['held'] == 'L':
            return ['hold', 'rotate_ccw', 'sonic_drop', 'rotate_cw', 'sonic_drop', 'move_right', 'rotate_ccw']
        
        elif game_state['current']['piece'] == 'L':
            return ['rotate_ccw', 'sonic_drop', 'rotate_cw', 'sonic_drop', 'move_right', 'rotate_ccw']
        elif game_state['current']['piece'] == 'O':
            return ['move_left', 'move_left']
        elif game_state['current']['piece'] == 'S':
            return ['rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            
        elif game_state['held'] == None:
            if game_state['queue'][0] == 'I':
                return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'L':
                return ['hold', 'rotate_ccw', 'sonic_drop', 'rotate_cw', 'sonic_drop', 'move_right', 'rotate_ccw']
            elif game_state['queue'][0] == 'O':
                return ['hold', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'S':
                return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            elif game_state['queue'][0] == 'J':
                return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'T':
                return['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
                
        elif game_state['held'] == 'I':
            return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        elif game_state['held'] == 'S':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        
        
        elif game_state['current']['piece'] == 'J': 
            return ['rotate_cw', 'move_left', 'move_left', 'move_left']
        elif game_state['held'] == 'J':
            return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
            
        elif game_state['current']['piece'] == 'T':
            return ['rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
        elif game_state['held'] == 'T':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
            
        else:
            return ['hold', 'rotate_cw', 'sonic_drop', 'rotate_cw']


def bag5_1(game_state):
    
        if game_state['current']['piece'] == 'I':
            return ['rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        
        elif game_state['held'] == 'O':
            return ['hold', 'move_left', 'move_left',]
        
        elif game_state['current']['piece'] == 'O':
            return ['move_left', 'move_left']
        elif game_state['current']['piece'] == 'S':
            return ['rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            
        elif game_state['held'] == None:
            if game_state['queue'][0] == 'I':
                return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'Z':
                return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
            elif game_state['queue'][0] == 'O':
                return ['hold', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'S':
                return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            elif game_state['queue'][0] == 'J':
                return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'T':
                return['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
                
        elif game_state['held'] == 'I':
            return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        elif game_state['held'] == 'S':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        
        elif game_state['current']['piece'] == 'T':
            return ['rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
        elif game_state['held'] == 'T':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
        
        elif game_state['current']['piece'] == 'J': 
            return ['rotate_cw', 'move_left', 'move_left', 'move_left']
        elif game_state['held'] == 'J':
            return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
        
        elif game_state['current']['piece'] == 'Z':
            return ['rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
        elif game_state['held'] == 'Z':
            return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
            
            
        else:
            return ['hold', 'rotate_ccw', 'move_right']


def bag5_2(game_state):
    
        if game_state['current']['piece'] == 'I':
            return ['rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        
        elif game_state['current']['piece'] == 'L':
            return ['rotate_ccw', 'sonic_drop', 'rotate_cw', 'sonic_drop', 'move_right', 'rotate_ccw']
        elif game_state['held'] == 'L':
            return ['hold', 'rotate_ccw', 'sonic_drop', 'rotate_cw', 'sonic_drop', 'move_right', 'rotate_ccw']
       
       
                
        elif game_state['held'] == 'I':
            return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        
        elif game_state['current']['piece'] == 'T':
            return ['rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
        elif game_state['held'] == 'T':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
        
        
        elif game_state['current']['piece'] == 'J': 
            return ['rotate_cw', 'move_left', 'move_left', 'move_left']
        elif game_state['held'] == 'J':
            return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
        
        elif game_state['current']['piece'] == 'S':
            return ['rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        elif game_state['held'] == 'S':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            

        elif game_state['current']['piece'] == 'Z':
            if sum(game_state['board'][i][1] == 'J' for i in range(len(game_state['board']))) > 2:
                return ['rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
            else:
                return ['rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw']
        elif game_state['held'] == 'Z':
            if sum(game_state['board'][i][1] == 'J' for i in range(len(game_state['board']))) > 2:
                return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
            else:
                return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw']

        
        elif game_state['held'] == None:
            if game_state['queue'][0] == 'I':
                return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'L':
                return ['hold', 'rotate_ccw', 'sonic_drop', 'rotate_cw', 'sonic_drop', 'move_right', 'rotate_ccw']
            elif game_state['queue'][0] == 'Z':
                if sum(game_state['board'][i][1] == 'J' for i in range(len(game_state['board']))) > 2:
                    return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
                else:
                    return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw']
            elif game_state['queue'][0] == 'S':
                return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            elif game_state['queue'][0] == 'J':
                return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'T':
                return['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
            
        else:
            return ['hold', 'move_left', 'move_left']


def bag5_3(game_state):
    
        if game_state['current']['piece'] == 'I':
            return ['rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        
        elif game_state['held'] == 'O':
            return ['hold', 'move_left', 'sonic_drop', 'move_left']
        
        elif game_state['current']['piece'] == 'O':
            return ['move_left', 'sonic_drop', 'move_left']
        elif game_state['current']['piece'] == 'S':
            return ['rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            
        elif game_state['held'] == None:
            if game_state['queue'][0] == 'I':
                return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'Z':
                return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
            elif game_state['queue'][0] == 'O':
                return ['hold', 'move_left', 'sonic_drop', 'move_left']
            elif game_state['queue'][0] == 'S':
                return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
            elif game_state['queue'][0] == 'J':
                return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
            elif game_state['queue'][0] == 'T':
                return['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
                
        elif game_state['held'] == 'I':
            return ['hold', 'rotate_ccw', 'move_left', 'move_left', 'move_left', 'move_left']
        elif game_state['held'] == 'S':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'move_right', 'move_right', 'move_right', 'sonic_drop', 'rotate_ccw']
        
        elif game_state['current']['piece'] == 'T':
            return ['rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
        elif game_state['held'] == 'T':
            return ['hold', 'rotate_ccw', 'move_right', 'move_right', 'rotate_ccw']
        
        elif game_state['current']['piece'] == 'J': 
            return ['rotate_cw', 'move_left', 'move_left', 'move_left']
        elif game_state['held'] == 'J':
            return ['hold', 'rotate_cw', 'move_left', 'move_left', 'move_left']
        
        elif game_state['current']['piece'] == 'Z':
            return ['rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
        elif game_state['held'] == 'Z':
            return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw', 'sonic_drop', 'move_left']
            
            
        else:
            return ['hold', 'rotate_ccw', 'move_right']



def opener(game_state):
    if game_state['piecesPlaced'] % 35 <= 5:
        return bag1(game_state)
    elif  game_state['piecesPlaced'] % 35 == 6:
        if game_state['current']['piece'] == 'Z':
            return ['move_left', 'move_left', 'move_left']
        else:
            return ['hold', 'move_left', 'move_left', 'move_left']
    elif game_state['piecesPlaced'] % 35 <= 12:
        return bag2(game_state)
    elif  game_state['piecesPlaced'] % 35 == 13:
        if game_state['current']['piece'] == 'L':
            return ['move_right', 'move_right', 'move_right', 'move_right']
        else:
            return ['hold', 'move_right', 'move_right', 'move_right', 'move_right']
    elif game_state['piecesPlaced'] % 35 <= 19:
        return bag3(game_state)
    elif  game_state['piecesPlaced'] % 35 == 20:
        if game_state['current']['piece'] == 'O':
            return ['move_left']
        else:
            return ['hold', 'move_left']
        
    elif game_state['piecesPlaced'] % 35 <= 26:
        return bag4(game_state)
    elif  game_state['piecesPlaced'] % 35 == 27:
        global piece_order
        global bag5_queue
        piece_order = 0
        bag5_queue = []
        bag5_queue.append(game_state['current']['piece'])
        bag5_queue.extend(game_state['queue'])
        j, o, z, t, l = [bag5_queue.index(piece) for piece in 'JOZTL']
        if (j > o) and ((t > l or z > l) or (o > l)):
            piece_order = 1
        elif (j > o) and (z > o or l > o):
            piece_order = 2
        elif (o > j) and (z > l or o > l):
            piece_order = 3
        elif (z > o or l > o):
            piece_order = 4
        #print(''.join(bag5_queue))
        #print('piece order: ' + str(piece_order))
        if game_state['current']['piece'] == 'I':
                return ['rotate_cw']
        else:
            return ['hold', 'rotate_cw']
    elif game_state['piecesPlaced'] % 35 <= 33:
        if piece_order == 1:
            return bag5(game_state)
        elif piece_order == 2:
            return bag5_1(game_state)
        elif piece_order == 3:
            return bag5_2(game_state)
        elif piece_order == 4:
            return bag5_3(game_state)
    elif  game_state['piecesPlaced'] % 35 == 34:
        if piece_order == 1:
            if game_state['current']['piece'] == 'Z':
                return ['rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw']
            else:
                return ['hold', 'rotate_ccw', 'move_right', 'sonic_drop', 'rotate_ccw']
        elif piece_order == 2:
            if game_state['current']['piece'] == 'L':
                return ['rotate_ccw', 'move_right']
            else:
                return ['hold', 'rotate_ccw', 'move_right']
        elif piece_order == 3:
            if game_state['current']['piece'] == 'O':
                return ['move_left', 'move_left']
            else:
                return ['hold', 'move_left', 'move_left']
        elif piece_order == 4:
            if game_state['current']['piece'] == 'L':
                return ['rotate_ccw', 'move_right']
            else:
                return ['hold', 'rotate_ccw', 'move_right']
    else:
        return ['move_right']
open_count = 0
open = True

def decide_command(game_state, players):
    start_time = time.time()
    board = game_state['board']
    piece = game_state['current']['piece']
    held_piece = game_state['held']
    global open_count
    global open
    if len(board) >= 15:
        open = False
    if open_count%35 == 0:
        if board != []:
            open = False
    
    if open is True:
        open_count += 1
        return opener(game_state)
    if board != []:
        board = [[0 if y is None else 1 for y in x] for x in board]
        board.extend([[0]*10 for _ in range(20-len(board))])
        board = board[::-1]
    else:
        board = ([[0]*10 for _ in range(20)])

        
    depth = 2
    best_move, best_hold = bfs_best_move(board, piece_map.get(piece), piece_map.get(held_piece), depth, game_state)
    end_time = time.time()
    duration = (end_time - start_time) * 1000
    print(f"Time taken: {duration:.2f}ms")
    return move_piece(piece, held_piece, best_move[0], best_move[1], best_hold)





async def connect():
    token = secret_token
    roomKey = master_key
    url = f"wss://botrisbattle.com/ws?token={token}&roomKey={roomKey}"

    game_started = False
    round_started = False

    async with websockets.connect(url) as websocket:
        print("Connected to WebSocket server")

        while True:
            # Receive a message from the server
            response = await websocket.recv()
            message = json.loads(response)
            #print(f"Received from server: {message}")

            if message['type'] == 'player_joined':
                player_data = message['payload']['playerData']
                print(f"Player joined: {player_data}")

            elif message['type'] == 'game_started':
                game_started = True
                print("Game started")

            elif message['type'] == 'round_started':
                round_started = True
                global open_count, open
                open_count = 0
                open = True
                starts_at = message['payload']['startsAt']
                room_data = message['payload']['roomData']
                print(f"Round starts at: {starts_at}")#, Room data: {room_data}
                

            elif message['type'] == 'request_move' and game_started and round_started:
                game_state = message['payload']['gameState']
                players = message['payload']['players']

                # Decide on a command based on the game state
                command = decide_command(game_state, players)

                action_message = {
                    "type": "action",
                    "payload": {
                        "commands": command
                    }
                }

                await websocket.send(json.dumps(action_message))
                #print(f"Sent to server: {action_message}")


asyncio.get_event_loop().run_until_complete(connect())