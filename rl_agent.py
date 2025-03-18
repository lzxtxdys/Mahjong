import numpy as np
import random
import pickle  # To save and load trained Q-table

class RLAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, q_table_file="q_table.pkl"):
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor (future rewards)
        self.epsilon = epsilon  # Exploration rate
        self.q_table_file = q_table_file

        # Load Q-table if exists, else create empty table
        try:
            with open(self.q_table_file, "rb") as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            self.q_table = {}

    def get_state(self, player, game):
        """ Convert game state into a tuple representation """
        state = []

        # Encode player's hand (count of each tile)
        tile_counts = {tile: player.hand.count(tile) for tile in game.deck}
        state.extend(list(tile_counts.values()))

        # Encode exposed sets
        state.append(len(player.exposed_sets))

        # Encode discard pile
        discard_counts = {tile: game.get_discard_count(tile) for tile in game.deck}
        state.extend(list(discard_counts.values()))

        # Encode turn number
        state.append(len(game.discards))

        return tuple(state)  # Hashable type

    def get_possible_actions(self, player, game):
        """ Returns a list of valid actions AI can take. """
        actions = [("discard", tile) for tile in set(player.hand)]
        
        # Peng
        for tile in game.discards:
            if player.hand.count(tile) >= 2:
                actions.append(("peng", tile))

        # Gang
        for tile in set(player.hand):
            if player.hand.count(tile) == 4:
                actions.append(("gang", tile))

        # Hu
        if player.check_hu():
            actions.append(("hu", None))

        return actions

    def choose_action(self, player, game):
        """ Uses Q-learning to choose the best action for AI. """
        state = self.get_state(player, game)
        possible_actions = self.get_possible_actions(player, game)

        # Exploration (random choice)
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_actions)

        # Exploitation (choose best known action)
        best_action = max(possible_actions, key=lambda action: self.q_table.get((state, action), 0))
        return best_action

    def update_q_table(self, player, game, action, reward, new_state):
        """ Updates the Q-table using Q-learning update rule. """
        state = self.get_state(player, game)
        new_state = tuple(new_state)
        action = tuple(action)

        # Get current Q-value
        current_q = self.q_table.get((state, action), 0)

        # Get max Q-value for next state
        max_future_q = max(self.q_table.get((new_state, a), 0) for a in self.get_possible_actions(player, game))

        # Q-learning formula
        new_q = current_q + self.alpha * (reward + self.gamma * max_future_q - current_q)

        # Update Q-table
        self.q_table[(state, action)] = new_q

    def save_q_table(self):
        """ Save Q-table to file. """
        with open(self.q_table_file, "wb") as f:
            pickle.dump(self.q_table, f)
