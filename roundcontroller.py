import operator
import functools
import random
from utils import random_percentage


class RoundController(object):
    def __init__(self, nodes, prev_round_convinced):
        self.nodes = nodes
        self.prev_round_convinced = prev_round_convinced

    def get_nodes_to_convince(self):
        neighbours = set()
        for name in self.prev_round_convinced:
            for neighbour in self.nodes.get(name).neighbours:
                neighbours.add(neighbour)
        return neighbours

    def calc_node_probabilities(self, node):
        """Gets the convince threshold for each neighbour having changed state
        in the previous round. Then produces a map of probabilties for each
        event to happen."""
        neighbours = self.prev_round_convinced.intersection(node.neighbours)
        thresholds = node.get_belief_thresholds(self.nodes, neighbours)

        chances = {}
        for belief in thresholds:
            chances[belief] = functools.reduce(operator.mul,
                                               thresholds[belief])

        probabilities = {}
        if len(chances) == 1:
            belief = list(chances.keys())[0]
            probability = list(chances.values())[0]
            # Neighbour wins
            probabilities[belief] = probability
            # Neighbour loses
            probabilities[str(node.state.belief)] = 1 - probability
        elif len(chances) == 2:
            x, y = set(chances.keys())
            # x wins and y loses
            probabilities[x] = chances[x] * (1 - chances[y])
            # y wins and x loses
            probabilities[y] = chances[y] * (1 - chances[x])
            # None wins
            probabilities['remain'] = (1 - chances[x]) * (1 - chances[y])
            # Both win, split decision
            probabilities[f"{x}split{y}"] = chances[x] * chances[y]
        return chances, probabilities

    def draw_result(self, probabilities):
        """Makes a weighted choice based on the probabilties we computed"""
        choices, weights = list(), list()
        for choice, weight in probabilities.items():
            choices.append(choice)
            weights.append(weight)
        return random.choices(choices, weights=weights, k=1)[0]

    def get_winner(self, chances, probabilities, beliefs):
        """Recalculates the treshold based on each belief's probability of
        winning and draws a new random number to decide the winner."""
        x, y = beliefs.split('split')
        threshold = (1 - chances[x]) / (1 - chances[x] + 1 - chances[y])
        r = random_percentage()
        if r <= threshold:
            return x, (chances[x] * probabilities[beliefs])
        return y, (chances[y] * probabilities[beliefs])

    def get_next_node_state(self, node):
        """Fetches the cumulated chances for each belief and their individual
        result probabilities before drawing a random result. If the result is a
        split decision, draws a second time and returns the winner."""
        chances, probabilities = self.calc_node_probabilities(node)
        if len(chances) > 0 and len(probabilities) > 0:
            result = self.draw_result(probabilities)
            if 'split' in result:
                return self.get_winner(chances, probabilities, result)
            if 'remain' in result or str(node.state.belief) in result:
                return None
            return result, chances[result]
        return None

    def get_round_convinced(self):
        to_convince = self.get_nodes_to_convince()
        round_convinced = {}
        for name in to_convince:
            node = self.nodes.get(name)
            next_state = self.get_next_node_state(node)
            if next_state:
                round_convinced[name] = next_state
        return round_convinced
