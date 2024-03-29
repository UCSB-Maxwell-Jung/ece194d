import numpy as np
import matplotlib.pyplot as plt

def main():
    p_h = 0.49
    p_t = 1-p_h
    discount = 1
    values = np.random.rand(100+1)
    values[0] = 0
    values[100] = 0
    
    while True:
        old = values.copy()
        for s in range(1, 100):
            potential_new_values = []
            for a in range(1, min(s, 100-s)+1):
                winning_state = s+a
                losing_state = s-a
                if winning_state < 0 or losing_state < 0:
                    print(f'{s=} {a=}')
                    raise Exception
                reward = 1 if winning_state >= 100 else 0
                v = p_h*(reward + discount*values[winning_state]) + \
                    p_t*(discount*values[losing_state])
                potential_new_values.append(v)
            values[s] = max(potential_new_values)
        new = values.copy()
        if np.linalg.norm(old-new) < 0.0001:
            print(new)
            np.save(f'{p_h} values', new)
            break
    
    policy = np.zeros(101)
    for s in range(1, 100):
        best_action = 1
        best_v = 0
        for a in range(1, min(s, 100-s)+1):
            winning_state = s+a
            losing_state = s-a
            if winning_state < 0 or losing_state < 0:
                raise Exception
            reward = 1 if winning_state >= 100 else 0
            v = p_h*(reward + discount*values[winning_state]) + \
                p_t*(discount*values[losing_state])
            if v >= best_v:
                best_v = v
                best_action = a
        policy[s] = best_action
    
    print(policy)
    np.save(f'{p_h} policy', policy)
    
    fig, ax = plt.subplots()
    ax.plot(np.arange(101), policy)

    ax.set(xlabel='current capital', ylabel='stakes',
        title=f'optimal policy for {p_h=}')
    ax.grid()

    fig.savefig(f"{p_h} optimal policy.png")
    plt.show()

if __name__ == '__main__':
    main()