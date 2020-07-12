import logging


class Belief(Enum):
    NEUTRAL = auto()
    TRUE = auto()
    FALSE = auto()

    def __str__(self):
        return {
            self.NEUTRAL: '-',
            self.TRUE: 'X',
            self.FALSE: '0',
        }[self]


class NodeState:

    def __init__(self, belief, prob):
        self.belief = belief
        self.prob = prob

    def __repr__(self):
        return f'{self.belief}: {self.prob}'


class Node:

    def __init__(self, name, state=Belief.NEUTRAL, prob=0.01):
        self.name = name
        self.state = NodeState(state, prob)
        self.neighbours = []
        logging.debug(f"Created node {name}.")
        logging.debug(f"{self.pretty()}.")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def pretty(self):
        if self.neighbours:
            neighbours = ', '.join([str(n) for n in self.neighbours])
        else:
            neighbours = 'None'
        return f'{self.name}: {self.state}. Links: {neighbours}'

    def add_link(self, node):
        if node is self:
            logging.debug(f'Trying to link {self} to itself.')
        else:
            if node.name not in self.neighbours:
                self.neighbours.append(node.name)
                logging.debug(f"Linked {node} as {self}'s neighbour.")
            else:
                logging.debug(f"{node} is already a neighbour of {self}.")
            if self.name not in node.neighbours:
                node.neighbours.append(self.name)
                logging.debug(f"Created reciprocal link of {self} to {node}.")
            else:
                logging.debug(f"{self} is already a neighbour of {node}.")

    def set_belief(self, belief, prob):
        self.state.belief = belief
        self.state.prob = prob

    def add_links(self, *nodes):
        for node in nodes:
            self.add_link(node)


def node_changed_state(node, prev_nodes):
    prev = get_node_by_name(prev_nodes, node.name)
    return prev.state.belief != node.state.belief


def get_node_by_name(nodes, name):
    return list(filter(lambda x: x.name == name, nodes))[0]
