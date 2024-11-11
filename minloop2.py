import asyncio
import websockets
import webbrowser
import json
import time

secret_token = ''
master_key = ''

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






def decide_command(game_state, players):
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
                starts_at = message['payload']['startsAt']
                room_data = message['payload']['roomData']
                print(f"Round starts at: {starts_at}")#, Room data: {room_data}

            elif message['type'] == 'request_move' and game_started and round_started:
                game_state = message['payload']['gameState']
                players = message['payload']['players']
                start_time = time.time()
                # Decide on a command based on the game state
                command = decide_command(game_state, players)
                end_time = time.time()
                duration = (end_time - start_time) * 1000
                print(f"Time taken: {duration:.2f}ms")
                action_message = {
                    "type": "action",
                    "payload": {
                        "commands": command
                    }
                }

                await websocket.send(json.dumps(action_message))
                #print(f"Sent to server: {action_message}")

asyncio.get_event_loop().run_until_complete(connect())