import numpy as np
import logic
import math

def main():
    w = np.random.rand(2)
    discount_factor = 1
    
    for i in range(100): # repeated 100 times
        epi = Episode()
        for t in range(epi.length):
            step_size = 1/(t+1) # variable alpha
            measurement = epi.rewardAt(t+1) + discount_factor*v_hat(epi.stateAt(t+1), w) # variable U_t
            actual = v_hat(epi.stateAt(t), w)
            grad = getFeatureVector(epi.stateAt(t)) # gradient of (W^T)X is X
            print(grad)
            w = w + step_size*(measurement - actual)*grad # w_t+1 = w_t + a[U_t-v(s_t, w_t)]*grad(v(s_t, w_t))
            print(f'{t=} {w=}')

direction_logic = {
    'right': logic.right,
    'up': logic.up,
    'left': logic.left,
    'down': logic.down,
}

action_names = {
    0: 'right',
    1: 'up',
    2: 'left',
    3: 'down',
}

# define winning state number as the max state number + 1
# where max state number = 11**16-1
WINNING_STATE = 11**16

def policy(state: int):
    '''
    Pick an action given state.
    Currently set to a random policy
    '''
    return np.random.randint(len(action_names))

def v_hat(state, weight: np.ndarray):
    if isTerminalState(state):
        return 0
    else:
        x = getFeatureVector(state)
        return weight.dot(x)

def reward(current_state: int, current_action: int, next_state: int):
    '''
    Calculate reward based on current state, current action, and next state
    '''
    # reward winning
    if next_state == WINNING_STATE:
        return +100
    
    if 0 <= next_state < WINNING_STATE:
        grid = stateToGrid(next_state)
        # punish losing or choosing an action that does nothing
        if logic.game_state(grid) == 'lose' or current_state == next_state:
            return -100000
        # punish valid moves by -1
        else:
            return -1
        
def isTerminalState(state: int):
    if state == WINNING_STATE:
        return True
    
    if 0 <= state < WINNING_STATE:
        grid = stateToGrid(state)
        if logic.game_state(grid) == 'lose':
            return True
        else:
            return False

class Episode:
    def __init__(self, max_length=1000):
        self.state_history = []
        self.action_history = []
        self.reward_history = [None]
        
        initial_grid = logic.new_game(4)
        s = gridToState(initial_grid)
        self.state_history.append(s)
        
        t = 0
        while not isTerminalState(s) and t < max_length:
            a = policy(s)
            self.action_history.append(a)
            s_prime = transition(s, a)
            r = reward(s, a, s_prime)
            self.reward_history.append(r)
            t += 1
            s = s_prime
            self.state_history.append(s)
            
        self.length = len(self.action_history)
            
    def stateAt(self, t):
        if 0 <= t < len(self.state_history):
            return self.state_history[t]
        else:
            return None
    
    def actionAt(self, t):
        if 0 <= t < len(self.action_history):
            return self.action_history[t]
        else:
            return None
    
    def rewardAt(self, t):
        if 1 <= t < len(self.reward_history):
            return self.reward_history[t]
        else:
            return None

def transition(state: int, action: int):
    grid = stateToGrid(state)
    direction = action_names[action]
    grid, done = direction_logic[direction](grid)
    
    if done:
        grid = logic.add_two(grid)
        
    return gridToState(grid)

def play():
    grid = logic.new_game(4) # create new game
    while True:
        # show grid
        # each row is printed on a new line because otherwise, 
        # the nested list is printed as a single line
        print(grid)
        # ask user for input
        direction = input(f'Direction (left, right, up, down): ')
        if direction not in direction_logic.keys():
            print(f'Invalid direction. Please input a valid direction.')
            continue
        # transition the grid to next state
        # done flag is used to check if the direction is a valid move
        grid, done = direction_logic[direction](grid)
        if done:
            # add new tile of value 2 to random position on the grid
            grid = logic.add_two(grid)
            if logic.game_state(grid) == 'win':
                print('Win')
                break
            if logic.game_state(grid) == 'lose':
                print('Lose')
                break

def stateToGrid(state: int, winning_value=2048):
    '''
    converts state number s denoted by an integer 
    in the range [0, 11^16-1] to a 4x4 grid
    '''
    base = int(math.log2(winning_value))
    if not 0 <= state < base**16: return None
    
    # helper function
    def numberToBase(n, b):
        if n == 0:
            return [0]
        digits = []
        while n:
            digits.append(int(n % b))
            n //= b
        return digits[::-1]
    
    # Convert state number to 16 digit base 11 representation
    # where each digit represents a tile
    digits = numberToBase(state, base)
    # Pad 0s in the front to get total 16 digits
    zeros = [0] * (16-len(digits))
    grid = zeros + digits
    # Rearrange digits in a 4x4 grid
    grid = np.array(grid).reshape((4,4))
    # Convert digit values to tile values
    grid = np.power(2, grid)
    # Replace all tiles of value 1 with 0 (aka blank tile)
    grid[grid==1] = 0
    
    return grid

def gridToState(grid, winning_value=2048):
    '''
    Hashes a 4x4 grid to state number s in the range [0, 11^16-1]
    This function should be the inverse of stateToGrid()
    
    Works by first converting the grid to a base 11 representation
    then calculating the actual value of the base 11 representation
    '''
    base = int(math.log2(winning_value))
    arr = np.array(grid)
    tile_values = arr.flatten()
    if winning_value in tile_values:
        return WINNING_STATE
    # Replace blank tiles with 1
    arr[arr==0] = 1
    # Convert to base 11 representation
    digits = np.log2(arr.flatten()).astype('int64')
    values_per_digit = np.power(base, np.arange(len(digits)-1, -1, -1, dtype='int64'))
    state = digits.dot(values_per_digit)
    
    return state

def getFeatureVector(state: int):
    '''
    Converts state number to feature vector
    '''
    grid = stateToGrid(state)
    
    return np.array([mean(grid),
                     std(grid),])

def mean(grid: np.ndarray):
    '''
    Calculates the mean of the tiles on the grid
    '''
    return grid.mean()

def std(grid: np.ndarray):
    '''
    Calculates standard deviation of the tiles on the grid
    '''
    return grid.std()

if __name__ == '__main__':
    main()