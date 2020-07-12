# The game of Trust
A game inspired from Conway's game of life.

# Rules

The game is composed of a cluster of linked nodes.

Each node is linked with one or more other nodes.

Every node has a state, composed of a belief and and probability. The belief represents a given node's view on an imaginary fact called X. The confidence in that belief is represented by a probabily (0.1 to 1.0).

The possible states are:
- Neutral
- Positive
- Negative

The game is rythmed by rounds.

During a round, all nodes are enumerated. If a node has changed belief since the last round, it will try to convince its neighbours.

If a neighbour already has the same belief, we pass on to the next. If a neighbour has a different belief, a conversation starts.

A random number between 0.1 and 1.0 is picked, if the node's confidence in X mutiplied by the inverse of the neighbour's confidence in its belief is superior to that random number, the neighbour is convinced. Nothing happens otherwise.

Each node starts in a neutral state with a probability of 0.1.

We then introduce at least one node with a belief different than neutral and set a desired confidence. This change of state then triggers the start of the game.
 
Rounds go on until the nodes' states are stable across the across the whole board.

# Ideas

Add a node-to-neighbour trust level:
- The more a node trusts a neighbour, the more likely it is to believe him.
- When a neighbour believes the node:
  - The trust level between both nodes inceases
  - The node's confidence in its belief increases.
- If a neighbour does not believe the node:
  - The trust level between both nodes decreases.
  - The confidence in both's beliefs decreases.
- The trust level is unidirectional, i.e. A can trust B at 70% even though B might trust A at only 20%.

# UI
## Step 1: Board
- Design a file format or protocol to display the board from the game's output
- Find an interesting way to highlight the following states:
  - Neutral, ligh grey
  - Positive, black
  - Negative, white
  - Convinced into positive, green
  - Convinced into negative, red
## Step 2: Graph
- Two-dimensiobal graph with nodes and links.
  - The confidence level influence the node's size
  - find a way to higlight the node-to-node trust level
