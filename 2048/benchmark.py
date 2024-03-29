from multiprocessing import Pool
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from game import TwntyFrtyEight
from agent import Agent

game = TwntyFrtyEight()
agent = Agent(game)
agent.w = np.load('w_star.npy')
features = ['points', 
            'emptiness',
            'roughness',
            'monotonicity',
            'std_vertical_dif',
            'std_horizontal_dif',
            'tile_delta',
            'mean',
            'std',
            'distance_to_corner',
            'center_sum',
            'perimeter_sum',
            'max_tile',]

def main():
    df = pd.DataFrame({'features': features, 
                       'weights': agent.w}).set_index('features')
    df = df.iloc[::-1]
    df['positive'] = df['weights'] > 0
    
    df['weights'].plot(kind='barh',
                       color=df.positive.map({True: 'b', False: 'r'}))
    
    try: df2 = pd.read_csv('benchmark.csv')
    except FileNotFoundError: df2 = generate_data(sample_size=1000)
    
    plt.figure()
    ax = df2['highest_tile'].value_counts().sort_index().plot(kind='bar')
    for container in ax.containers:
        ax.bar_label(container)
    
    df2.hist(column='score', grid=False, bins=100)
    
    df2.hist(column='total_moves', grid=False, bins=100)
    
    try: df3 = pd.read_csv('training_results.csv')
    except FileNotFoundError: print(f'Please run train.py to generate training results')
    
    df3.plot.line(x='episode_id', y='moves')
    
    df3.plot.line(x='episode_id', y='highest_tile')
    
    plt.show()
    
def get_results(i):
    board = game.new_board(row_count=4, col_count=4) # create new game
    S = game.board_to_state(board)
    score = 0
    total_moves = 0
    while True:
        direction = agent.greedy_policy(S)
        # transition the board to next state
        # done flag is used to check if the direction is a valid move
        board, points = game.move(board, direction)
        total_moves += 1
        score += points
        # add new tile of value 2 to random position on the board
        board = game.add_two(board)
        S = game.board_to_state(board)
        if game.is_terminal_state(S):
            break
    
    return np.max(board), score, total_moves

def generate_data(sample_size=1000):
    '''
    Use all CPU cores to run multiple simulations in parallel for faster data generation
    '''
    with Pool() as pool:
        data = pool.map(get_results, range(sample_size))
    
    df = pd.DataFrame(data, columns=['highest_tile', 'score', 'total_moves'])
    df.to_csv('benchmark.csv', index=False)
        
    return df
    
if __name__ == '__main__':
    main()