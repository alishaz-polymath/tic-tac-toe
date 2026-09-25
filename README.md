# QLearning tic-tac-toe Agent
In this project, we create a qlearning based tic-tac-toe agent to learn and play against pseudo logical AI, random agent and human players. The file `ttt_class.py` contains the code to create the Q Table for future references by playing against a pseudo logical agent.
In the file `ttt_performance_measure.py`, we can visualize the performance of our Q learning agent against a random agent or the pseudo logical agent using bar chart plots. In the file
 `ttt_human_vs_ai.py`, we have a very simplistic GUI based tictactoe game where we can play against the Q learning agent. The game is designed to keep count of the results of each game and restarts automatically once a game finishes. We can simply close the game
by clicking the `X` button on the window to close the game.

This project is essentially for educational and experimental purposes to see how reinforcement learning(specifically, QLearning) works in the classic game of tic tac toe.

## Installation:

```
$ git clone https://github.com/alishaz-polymath/tic-tac-toe.git
```

## Usage:

1. Run the `ttt_class.py` file to generate a newer version of `Qlearn_new.pickle` file, if you wish, else go to step 2.
2. Run the `ttt_performance_measure.py` file to visualise the performance index between various agents, which can be selected from within the file inside the `main()` definition. 
3. Run the `ttt_human_vs_ai.py` file to play against the Q Learning agent in with a simplistic GUI.

## Essential Libraries:
* numpy
* random
* matplotlib
* pickle
* pygame

## Example Performance Measure Graphs:
![Plot of Logical Agent vs Random Agent](images/ttt_plot_lavsrandom.png "Logical vs Random Agent")

![Plot of QL Agent vs Logical Agent](images/ttt_plot_performance.png "QL vs Logical Agent")

![Plot of QL Agent vs Random Agent](images/ttt_plot_qlvsrandom.png "QL vs Random Agent")

## Example Game Board:
![GUI Board](images/ttt_gui.png "GUI Board of TicTacToe")



## License:
This project is licensed under the MIT License.

## Correctness and tests

The training agent plays X against `LogicAgent` or `Random` as O. Each update
covers one X move and, unless X ends the game, the opponent's response. Terminal
rewards are +1 for an X win, -1 for an O win, and 0 for a draw. Nonterminal
updates bootstrap from the maximum **legal action value** at X's next decision
state, with learning rate 0.5 and discount 0.01.

`exploration` is the probability of a random move: 0.8 initially, then 0 after
100,000 episodes. Greedy training ties are broken randomly. This is a finite
training schedule, not a guarantee of optimal play.

The bundled `Qlearn_new.pickle` and example plots predate these correctness
fixes. Regenerate the table from scratch with `python ttt_class.py` before
assessing the corrected agent, then rerun `python ttt_performance_measure.py`.
The existing plots should not be interpreted as corrected benchmark results.

Install the plotting dependency and run the regression suite from the repository
root (the GUI additionally requires `pygame`):

```sh
python -m pip install matplotlib
python -m unittest discover -s tests -v
```

The tests cover all 5,478 legally reachable board states, tactical win priority,
legal Q-value targets, terminal rewards, and agent/opponent transition timing.
