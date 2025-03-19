import numpy as np
import random
import pickle
import os
from collections import Counter

class RLAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, q_table_file="q_table.pkl"):
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor (future rewards)
        self.epsilon = epsilon  # Exploration rate
        self.q_table_file = q_table_file
        self.last_state = None
        self.last_action = None
        self.last_hand = None
        self.last_exposed_sets = None
        self.tiles_seen = set()
        self.winning_patterns = {}  # Track patterns that led to wins
        
        # Load Q-table if exists, else create empty table
        try:
            with open(self.q_table_file, "rb") as f:
                self.q_table = pickle.load(f)
            print(f"Loaded Q-table with {len(self.q_table)} entries")
        except FileNotFoundError:
            self.q_table = {}
            print("Created new Q-table")
    
    def reset_for_new_game(self):
        """Reset agent state for a new game"""
        self.last_state = None
        self.last_action = None
        self.last_hand = None
        self.last_exposed_sets = None
        self.tiles_seen = set()
    
    def get_state(self, player, game):
        """
        Generate a simple state representation that captures the essential features
        """
        # Update tiles seen
        for tile in game.discards:
            self.tiles_seen.add(tile)
        for p in game.players:
            for exposed_set in p.exposed_sets:
                for tile in exposed_set:
                    self.tiles_seen.add(tile)
        
        # Analyze hand composition
        hand_counts = Counter(player.hand)
        pairs = sum(1 for _, count in hand_counts.items() if count == 2)
        triplets = sum(1 for _, count in hand_counts.items() if count >= 3)
        
        # Count tiles by suit
        suit_counts = {"W": 0, "B": 0, "T": 0}
        for tile in player.hand:
            suit = tile[-1]
            suit_counts[suit] += 1
        
        # Analyze potential straights
        straight_potential = 0
        for suit in ["W", "B", "T"]:
            if suit == player.banned_suit:
                continue
                
            nums_in_suit = [int(t[:-1]) for t in player.hand if t.endswith(suit)]
            for num in range(1, 8):  # Check for potential straights (1-2-3, 2-3-4, etc)
                sequence = [num, num+1, num+2]
                matching = sum(1 for n in sequence if n in nums_in_suit)
                if matching == 3:  # Complete straight
                    straight_potential += 1
                elif matching == 2:  # Potential straight (need one more tile)
                    straight_potential += 0.5
        
        # Distance to winning
        exposed_melds = len(player.exposed_sets)
        hand_melds = triplets + int(straight_potential)
        total_melds = exposed_melds + hand_melds
        
        # For seven pairs
        seven_pairs_potential = min(7, pairs)
        
        # For regular hu (4 melds + 1 pair)
        regular_hu_potential = total_melds + (1 if pairs > 0 else 0)
        
        # Distance to winning (0-5, lower is better)
        distance_to_win = max(0, min(5, min(
            7 - seven_pairs_potential,  # Distance to seven pairs
            5 - regular_hu_potential  # Distance to regular hu
        )))
        
        # Game stage (early, mid, late)
        if len(game.deck) > 70:
            game_stage = 0  # early
        elif len(game.deck) > 40:
            game_stage = 1  # mid
        else:
            game_stage = 2  # late
        
        # Create a simplified state tuple
        state = (
            min(3, pairs),   # 0-3 pairs
            min(2, triplets),  # 0-2 triplets
            min(3, suit_counts["W"] // 4),  # W tiles (0-3)
            min(3, suit_counts["B"] // 4),  # B tiles (0-3)
            min(3, suit_counts["T"] // 4),  # T tiles (0-3)
            min(3, exposed_melds),  # exposed sets (0-3)
            1 if player.banned_suit == "W" else 0,  # banned suit W?
            1 if player.banned_suit == "B" else 0,  # banned suit B?
            1 if player.banned_suit == "T" else 0,  # banned suit T?
            game_stage,  # game stage (0-2)
            distance_to_win  # distance to winning (0-5)
        )
        
        # Store current hand for reward calculation
        self.last_hand = player.hand.copy()
        self.last_exposed_sets = [s.copy() for s in player.exposed_sets]
        
        return state

    def get_possible_actions(self, player, game):
        """Returns a list of valid actions the player can take."""
        actions = []
        
        # Always include discard actions for each unique tile in hand
        for tile in set(player.hand):
            actions.append(("discard", tile))
        
        # Peng action for the last discarded tile
        if game.discards and player.hand.count(game.discards[-1]) >= 2:
            if not game.discards[-1].endswith(player.banned_suit):  # Can't peng banned suit
                actions.append(("peng", game.discards[-1]))
        
        # Gang action for tiles in hand
        for tile in set(player.hand):
            if player.hand.count(tile) == 4 and not tile.endswith(player.banned_suit):
                actions.append(("gang", tile))
        
        # Check for hu (winning)
        if player.check_hu():
            actions.append(("hu", None))
            
        return actions

    def choose_action(self, player, game):
        """Choose the best action based on advanced strategic rules and Q-values."""
        state = self.get_state(player, game)
        possible_actions = self.get_possible_actions(player, game)
        
        # No valid actions
        if not possible_actions:
            return None, None
        
        # Store state for learning
        self.last_state = state
        
        # STRATEGY 1: Always choose Hu if available (winning)
        for action in possible_actions:
            if action[0] == "hu":
                self.last_action = action
                return action
        
        # STRATEGY 2: Always discard banned suit tiles first (critical rule)
        banned_tiles = [action for action in possible_actions 
                      if action[0] == "discard" and action[1].endswith(player.banned_suit)]
        if banned_tiles:
            # Choose the best banned tile to discard
            best_banned = self._choose_best_banned_tile(banned_tiles, player)
            self.last_action = best_banned
            return best_banned
        
        # STRATEGY 3: Always choose Gang if available (powerful move)
        gang_actions = [action for action in possible_actions if action[0] == "gang"]
        if gang_actions:
            chosen_action = gang_actions[0]
            self.last_action = chosen_action
            return chosen_action
        
        # STRATEGY 4: Almost always choose Peng if available (important for sets)
        peng_actions = [action for action in possible_actions if action[0] == "peng"]
        if peng_actions and random.random() < 0.98:  # 98% chance to Peng
            chosen_action = peng_actions[0]
            self.last_action = chosen_action
            return chosen_action
        
        # STRATEGY 5: Use exploration/exploitation for discard decisions
        if random.random() < self.epsilon:  # Exploration
            # During exploration, still use smart heuristics for discard
            chosen_action = self._choose_strategic_discard(player, game, possible_actions)
            self.last_action = chosen_action
            return chosen_action
        else:  # Exploitation
            # Use Q-values + enhanced heuristics
            return self._exploit_with_advanced_strategy(state, player, game, possible_actions)
    
    def _choose_best_banned_tile(self, banned_actions, player):
        """Choose the best banned suit tile to discard strategically"""
        # Prefer to discard singles over pairs
        singles = [action for action in banned_actions 
                 if player.hand.count(action[1]) == 1]
        if singles:
            return random.choice(singles)
        
        # Prefer to discard tiles that don't break potential straights
        non_straight_tiles = []
        for action in banned_actions:
            tile = action[1]
            suit = tile[-1]
            num = int(tile[:-1])
            
            is_part_of_straight = False
            for start in range(max(1, num-2), min(8, num+1)):
                potential = [f"{start+i}{suit}" for i in range(3)]
                matching = sum(1 for t in potential if t in player.hand)
                if matching >= 2:  # Part of potential straight
                    is_part_of_straight = True
                    break
            
            if not is_part_of_straight:
                non_straight_tiles.append(action)
        
        if non_straight_tiles:
            return random.choice(non_straight_tiles)
        
        # Otherwise just pick randomly
        return random.choice(banned_actions)
    
    def _choose_strategic_discard(self, player, game, possible_actions):
        """Choose a tile to discard using advanced strategic heuristics"""
        discard_actions = [a for a in possible_actions if a[0] == "discard"]
        if not discard_actions:
            return random.choice(possible_actions)
        
        # Analyze hand to find best discard
        tile_scores = {}
        for action in discard_actions:
            tile = action[1]
            score = 0
            
            # Avoid discarding tiles that are part of pairs
            if player.hand.count(tile) == 2:
                score -= 10
            
            # Count tiles needed for potential straights
            suit = tile[-1]
            num = int(tile[:-1])
            
            for start in range(max(1, num-2), min(8, num+1)):
                potential = [f"{start+i}{suit}" for i in range(3)]
                matching = sum(1 for t in potential if t in player.hand)
                
                if matching == 3:  # Complete straight
                    score -= 12  # Heavily penalize breaking a complete straight
                elif matching == 2:  # Potential straight
                    if tile in potential:  # Only if tile is part of it
                        score -= 8  # Penalize breaking potential straight
            
            # Prefer to discard terminal tiles (1, 9) over middle tiles
            if num == 1 or num == 9:
                score += 3  # Terminals are less flexible for straights
            elif num == 2 or num == 8:
                score += 2  # Near-terminals are somewhat flexible
            else:
                score += 0  # Middle numbers are most flexible, no bonus
            
            # Prefer to discard tiles that have been seen frequently
            seen_count = sum(1 for t in self.tiles_seen if t == tile)
            score += seen_count * 1.5
            
            # Prefer to discard tiles from suits with fewer tiles
            suit_count = sum(1 for t in player.hand if t.endswith(suit))
            if suit_count <= 3:  # Few tiles of this suit
                score += 4  # Good to discard from minority suits
            
            tile_scores[action] = score
        
        # Choose the tile with the highest score
        return max(tile_scores, key=tile_scores.get)
    
    def _exploit_with_advanced_strategy(self, state, player, game, possible_actions):
        """Use Q-values with advanced strategy enhancements"""
        discard_actions = [a for a in possible_actions if a[0] == "discard"]
        if not discard_actions:
            return random.choice(possible_actions)
        
        # Calculate combined scores for each discard action
        combined_scores = {}
        for action in discard_actions:
            # Q-value component
            q_value = self.q_table.get((state, action), 0)
            
            # Strategic score component
            strategic_score = self._calculate_strategic_value(action, player, game)
            
            # Weight Q-values more as we learn
            q_weight = min(0.7, len(self.q_table) / 50000) 
            strategic_weight = 1.0 - q_weight
            
            # Weighted combination
            combined_scores[action] = (q_value * q_weight) + (strategic_score * strategic_weight)
        
        # Choose the action with the highest combined score
        best_action = max(combined_scores, key=combined_scores.get)
        self.last_action = best_action
        return best_action
    
    def _calculate_strategic_value(self, action, player, game):
        """Calculate the strategic value of a discard action"""
        # Only calculate for discard actions
        if action[0] != "discard":
            return 0
        
        tile = action[1]
        value = 0
        
        # CRITERION 1: Avoid discarding pairs
        if player.hand.count(tile) == 2:
            value -= 15
        
        # CRITERION 2: Avoid discarding tiles that form straights
        suit = tile[-1]
        num = int(tile[:-1])
        
        for start in range(max(1, num-2), min(8, num+1)):
            potential = [f"{start+i}{suit}" for i in range(3)]
            matching = sum(1 for t in potential if t in player.hand)
            
            if matching == 3:  # Complete straight
                value -= 20
            elif matching == 2 and tile in potential:  # Potential straight that includes this tile
                value -= 12
        
        # CRITERION 3: Consider tile position (terminals vs middle)
        if num == 1 or num == 9:  # Terminals
            value += 5  # Easier to discard
        elif num == 2 or num == 8:  # Near-terminals
            value += 3
        
        # CRITERION 4: Consider frequently seen tiles
        seen_count = sum(1 for t in self.tiles_seen if t == tile)
        value += seen_count * 2
        
        # CRITERION 5: Consider tile effectiveness based on hand composition
        # Calculate how well this tile fits with overall strategy
        
        # Count pairs
        pair_count = sum(1 for t in set(player.hand) if player.hand.count(t) == 2)
        
        # If going for seven pairs (5+ pairs already)
        if pair_count >= 5 and player.hand.count(tile) == 1:
            value += 10  # Good to discard singles when going for seven pairs
        
        # If going for regular hu (some triples/straights already)
        exposed_count = len(player.exposed_sets)
        if exposed_count >= 2:
            # Check if tile forms a pair with something
            if player.hand.count(tile) == 2:
                value -= 8  # Keep pairs when close to winning
        
        return value

    def calculate_reward(self, player, game, action, hu_achieved=False):
        """Calculate reward for an action with advanced optimization."""
        if hu_achieved:
            # Record the winning pattern
            pattern_key = self._get_pattern_key(player)
            self.winning_patterns[pattern_key] = self.winning_patterns.get(pattern_key, 0) + 1
            return 150.0  # Massive reward for winning
        
        if not action:
            return 0
        
        action_type, tile = action
        reward = 0
        
        if action_type == "discard":
            # Reward for discarding banned suit
            if tile.endswith(player.banned_suit):
                reward += 10.0  # Major reward for following this rule
            
            # Calculate how the discard affects our winning potential
            # We need to analyze without modifying the actual hand
            hand_copy = player.hand.copy()
            hand_copy.append(tile)  # Add tile back to analyze pre-discard state
            
            pre_pairs = sum(1 for t in set(hand_copy) if hand_copy.count(t) == 2)
            pre_triples = sum(1 for t in set(hand_copy) if hand_copy.count(t) == 3)
            
            # Calculate straight potential before
            pre_straight = 0
            for suit in ["W", "B", "T"]:
                if suit == player.banned_suit:
                    continue
                    
                nums = [int(t[:-1]) for t in hand_copy if t.endswith(suit)]
                for num in range(1, 8):
                    sequence = [num, num+1, num+2]
                    matching = sum(1 for n in sequence if n in nums)
                    if matching == 3:
                        pre_straight += 1
                    elif matching == 2:
                        pre_straight += 0.5
            
            # Remove the tile to simulate after state
            hand_copy.remove(tile)
            
            post_pairs = sum(1 for t in set(hand_copy) if hand_copy.count(t) == 2)
            post_triples = sum(1 for t in set(hand_copy) if hand_copy.count(t) == 3)
            
            # Calculate straight potential after
            post_straight = 0
            for suit in ["W", "B", "T"]:
                if suit == player.banned_suit:
                    continue
                    
                nums = [int(t[:-1]) for t in hand_copy if t.endswith(suit)]
                for num in range(1, 8):
                    sequence = [num, num+1, num+2]
                    matching = sum(1 for n in sequence if n in nums)
                    if matching == 3:
                        post_straight += 1
                    elif matching == 2:
                        post_straight += 0.5
            
            # Calculate change in hand value
            pair_change = post_pairs - pre_pairs
            triple_change = post_triples - pre_triples
            straight_change = post_straight - pre_straight
            
            # Reward for improvements
            reward += pair_change * 5.0
            reward += triple_change * 8.0
            reward += straight_change * 6.0
            
            # Extra reward for discarding tiles that have been seen frequently
            seen_count = sum(1 for t in self.tiles_seen if t == tile)
            reward += seen_count * 0.5
            
        elif action_type == "peng":
            reward += 15.0  # Major reward for forming a set
            
            # Extra reward based on progress to winning
            exposed_sets = len(player.exposed_sets)
            if exposed_sets >= 2:
                reward += 8.0 * exposed_sets  # Scales with progress
            
            # Extra reward for late game pengs
            if len(game.deck) < 40:  # Mid to late game
                reward += 5.0
        
        elif action_type == "gang":
            reward += 25.0  # Higher reward for gang
            
            # Extra reward based on progress
            exposed_sets = len(player.exposed_sets)
            if exposed_sets >= 2:
                reward += 12.0 * exposed_sets
            
            # Extra reward for late game gangs
            if len(game.deck) < 40:  # Mid to late game
                reward += 8.0
        
        return reward
    
    def _get_pattern_key(self, player):
        """Get a unique key representing the winning pattern"""
        # Count by suit
        suit_counts = {"W": 0, "B": 0, "T": 0}
        for tile in player.hand:
            suit = tile[-1]
            suit_counts[suit] += 1
        
        # Count pairs
        pair_count = sum(1 for t in set(player.hand) if player.hand.count(t) == 2)
        
        # Count exposed sets
        exposed_count = len(player.exposed_sets)
        
        return (suit_counts["W"], suit_counts["B"], suit_counts["T"], pair_count, exposed_count)

    def update_q_table(self, player, game, next_state, reward, hu_achieved=False):
        """Update Q-table using the Q-learning algorithm with enhanced learning."""
        if self.last_state is None or self.last_action is None:
            return
        
        # Get current Q-value
        current_q = self.q_table.get((self.last_state, self.last_action), 0)
        
        # For terminal states (game over or hu achieved)
        if hu_achieved or not game.deck:
            # Boost learning rate for winning states
            effective_alpha = self.alpha * 1.5 if hu_achieved else self.alpha
            new_q = current_q + effective_alpha * (reward - current_q)
        else:
            # Get next possible actions
            next_actions = self.get_possible_actions(player, game)
            
            if not next_actions:
                max_future_q = 0
            else:
                # Get maximum Q-value for next state
                max_future_q = max([self.q_table.get((next_state, a), 0) for a in next_actions])
            
            # Q-learning formula
            new_q = current_q + self.alpha * (reward + self.gamma * max_future_q - current_q)
        
        # Update Q-table
        self.q_table[(self.last_state, self.last_action)] = new_q
        
        # Reset for next action
        self.last_state = None
        self.last_action = None

    def save_q_table(self):
        """Save Q-table to file."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.q_table_file) if os.path.dirname(self.q_table_file) else '.', exist_ok=True)
        
        with open(self.q_table_file, "wb") as f:
            pickle.dump(self.q_table, f)
        print(f"Saved Q-table with {len(self.q_table)} entries")