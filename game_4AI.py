import random
import os
from rl_agent import RLAgent

# Mahjong tiles definition
def generate_deck():
    deck = [f"{num}{suit}" for suit in ["W", "T", "B"] for num in range(1, 10)] * 4
    random.shuffle(deck)
    return deck

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.hand = []
        self.is_hu = False
        self.dice_roll = random.randint(1, 6) + random.randint(1, 6)
        self.banned_suit = None
        self.exposed_sets = []  # Store exposed sets of tiles
        self.gang_count = 0
        self.is_ai = is_ai
        self.rl_agent = None
        self.total_reward = 0  # Track total reward for this player during a game
    
    def draw_tile(self, deck, count=1):
        drawn_tiles = []
        for _ in range(count):
            if deck:
                tile = deck.pop()
                self.hand.append(tile)
                drawn_tiles.append(tile)
        self.sort_hand()
        return drawn_tiles
    
    def exchange_three(self, target_player):
        # Choose the least but at least 3 tiles of a suit to exchange
        count = self.count_suits()

        # Find suits that have more than 3 tiles and sort by amount
        valid_suits = sorted([(suit, num) for suit, num in count.items() if num >= 3], key=lambda x: x[1])

        # Choose the least but at least 3 tiles of a suit to exchange
        if not valid_suits:
            return [], []  # No valid suits for exchange
        
        chosen_suit = valid_suits[0][0]

        # Check if target player has enough tiles of the chosen suit
        target_suit_tiles = [tile for tile in target_player.hand if chosen_suit in tile]
        if len(target_suit_tiles) < 3:
            return [], []  # Target player doesn't have enough tiles
        
        # Choose 3 tiles to exchange
        chosen_tiles = random.sample([t for t in self.hand if chosen_suit in t], 3)
        received_tiles = random.sample(target_suit_tiles, 3)

        # Exchange tiles
        for tile in chosen_tiles:
            self.hand.remove(tile)
        for tile in received_tiles:
            target_player.hand.remove(tile)

        self.hand.extend(received_tiles)
        target_player.hand.extend(chosen_tiles)

        return chosen_tiles, received_tiles
    
    def determine_banned_suit(self):
        # After exchange, determine the banned suit (the least common suit)
        count = self.count_suits()
        sorted_suits = sorted(count.items(), key=lambda x: x[1])

        self.banned_suit = sorted_suits[0][0]

        # If multiple suits have the same minimum count, choose randomly
        if len(sorted_suits) > 1 and sorted_suits[0][1] == sorted_suits[1][1]:
            self.banned_suit = random.choice([s[0] for s in sorted_suits if s[1] == sorted_suits[0][1]])

        return self.banned_suit
    
    def discard_tile(self, game):
        """
        Discard a tile using AI strategy
        """
        if not self.hand:
            return None

        # Always discard banned suit tiles first
        banned_tiles = [tile for tile in self.hand if self.banned_suit in tile]
        if banned_tiles:
            if self.rl_agent:
                # Let the RL agent choose which banned tile to discard
                action, tile = self.rl_agent.choose_action(self, game)
                if action == "discard" and tile in banned_tiles:
                    self.hand.remove(tile)
                    return tile
                else:
                    # If RL agent chose something else, still discard a banned tile
                    discarded_tile = random.choice(banned_tiles)
                    self.hand.remove(discarded_tile)
                    return discarded_tile
            else:
                # Fallback - choose randomly
                discarded_tile = random.choice(banned_tiles)
                self.hand.remove(discarded_tile)
                return discarded_tile
        
        # Use the RL agent if available
        if self.rl_agent:
            action, tile = self.rl_agent.choose_action(self, game)
            if action == "discard":
                self.hand.remove(tile)
                return tile
            else:
                # Fallback - simple strategy
                worst_tile = self._find_worst_tile()
                self.hand.remove(worst_tile)
                return worst_tile
        
        # Fallback to random discard
        discarded_tile = random.choice(self.hand)
        self.hand.remove(discarded_tile)
        return discarded_tile
    
    def _find_worst_tile(self):
        """Find the worst tile to discard based on hand evaluation"""
        # This is a simplified version that prioritizes keeping pairs and straights
        
        # Calculate value for each tile
        tile_values = {}
        for tile in self.hand:
            value = 0
            
            # Pairs are valuable
            if self.hand.count(tile) >= 2:
                value += 5
            
            # Check if part of potential straight
            suit = tile[-1]
            num = int(tile[:-1])
            for start in range(max(1, num-2), min(8, num+1)):
                potential = [f"{start+i}{suit}" for i in range(3)]
                existing = sum(1 for t in potential if t in self.hand)
                if existing >= 2:  # At least 2 of 3 tiles for a straight
                    value += 3
            
            tile_values[tile] = value
        
        # Return the tile with lowest value
        return min(self.hand, key=lambda t: tile_values.get(t, 0))
    
    def peng(self, tile):
        """
        Decide whether to Peng (claim a discarded tile to form a triplet)
        """
        if self.hand.count(tile) >= 2:
            # Cannot Peng if tile is in banned suit
            if tile.endswith(self.banned_suit):
                return False
            
            # For AI players with an agent, use strategy
            if self.rl_agent:
                # Use agent to decide, but with high probability of Peng
                if random.random() < 0.8:  # 80% chance to Peng
                    self.hand.remove(tile)
                    self.hand.remove(tile)
                    self.exposed_sets.append([tile, tile, tile])
                    return True
                return False
            else:
                # Simple 50% chance strategy
                if random.random() < 0.5:
                    self.hand.remove(tile)
                    self.hand.remove(tile)
                    self.exposed_sets.append([tile, tile, tile])
                    return True
                return False
        
        return False
    
    def gang(self, tile):
        """
        Form a Gang (declare a quad) if possible
        """
        if self.hand.count(tile) == 4:
            # Cannot Gang if tile is in banned suit
            if tile.endswith(self.banned_suit):
                return False
            
            # Remove tiles and add to exposed sets
            for _ in range(4):
                self.hand.remove(tile)
            
            self.exposed_sets.append([tile, tile, tile, tile])
            self.gang_count += 1
            return True
        
        return False
    
    def check_hu_with_tile(self, tile):
        """
        Check if adding a specific tile to hand would complete a winning hand
        """
        if self.banned_suit and tile.endswith(self.banned_suit):
            return False  # Cannot win with a banned suit tile
            
        temp_hand = self.hand.copy()
        temp_hand.append(tile)
        return self.is_seven_pairs(temp_hand) or self.is_regular_hu(temp_hand)
    
    def is_seven_pairs(self, hand):
        """
        Check if the hand forms seven pairs (a winning hand type)
        """
        if len(hand) != 14:
            return False
        
        # Count occurrences of each tile
        counts = {}
        for tile in hand:
            counts[tile] = counts.get(tile, 0) + 1
        
        # Check if all tiles form pairs
        return all(count == 2 for count in counts.values()) and len(counts) == 7
    
    def is_regular_hu(self, hand):
        """
        Check if the hand forms a regular winning hand (4 sets + 1 pair)
        """
        if len(hand) != 14:
            return False
        
        # Check if any banned suit tiles are present
        if self.banned_suit and any(tile.endswith(self.banned_suit) for tile in hand):
            return False
        
        # Count occurrences of each tile
        counts = {}
        for tile in hand:
            counts[tile] = counts.get(tile, 0) + 1
        
        # Try each possible pair
        pairs = [tile for tile, count in counts.items() if count >= 2]
        for pair in pairs:
            temp_counts = counts.copy()
            temp_counts[pair] -= 2
            
            # Try to form sets with the remaining tiles
            if self.can_form_melds(temp_counts):
                return True
        
        return False
    
    def can_form_melds(self, counts):
        """
        Check if the remaining tiles can form valid melds (triplets or straights)
        """
        # If no tiles remain, we've successfully formed all melds
        if not any(counts.values()):
            return True
        
        # Find the first tile with count > 0
        first_tile = next((tile for tile, count in counts.items() if count > 0), None)
        if not first_tile:
            return True
        
        # Try to form a triplet
        if counts[first_tile] >= 3:
            counts[first_tile] -= 3
            if self.can_form_melds(counts):
                return True
            counts[first_tile] += 3  # Backtrack
        
        # Try to form a straight
        suit = first_tile[-1]
        num = int(first_tile[:-1])
        
        # Check if we can form a straight starting with this tile
        if num <= 7:  # Straights can only start from 1-7
            straight_possible = True
            for i in range(3):
                straight_tile = f"{num+i}{suit}"
                if straight_tile not in counts or counts[straight_tile] == 0:
                    straight_possible = False
                    break
            
            if straight_possible:
                # Remove the straight tiles
                for i in range(3):
                    counts[f"{num+i}{suit}"] -= 1
                
                if self.can_form_melds(counts):
                    return True
                
                # Backtrack
                for i in range(3):
                    counts[f"{num+i}{suit}"] += 1
        
        return False
    
    def check_hu(self):
        """
        Check if the current hand is a winning hand
        """
        # Cannot win if hand contains banned suit tiles
        if self.banned_suit and any(tile.endswith(self.banned_suit) for tile in self.hand):
            return False
        
        return self.is_seven_pairs(self.hand) or self.is_regular_hu(self.hand)
    
    def sort_hand(self):
        """
        Sort the hand for better readability
        """
        self.hand.sort(key=lambda x: (x[-1], int(x[:-1])))
    
    def sorted_hand(self):
        """
        Return a string representation of the sorted hand
        """
        tiles_wan = sorted([t for t in self.hand if "W" in t])
        tiles_bing = sorted([t for t in self.hand if "B" in t])
        tiles_tiao = sorted([t for t in self.hand if "T" in t])
        
        return f"W: {tiles_wan}, B: {tiles_bing}, T: {tiles_tiao} | Exposed: {self.exposed_sets}"
    
    def count_suits(self):
        """
        Count tiles by suit in the hand
        """
        count = {"W": 0, "B": 0, "T": 0}
        for tile in self.hand:
            suit = tile[-1]
            count[suit] += 1
        return count
    
    def calculate_score(self, is_zimo=False):
        """
        Calculate the score for a winning hand
        """
        base_score = 1
        fan_count = 0
        
        # Pengpenghu (all triplets) = 1 fan
        if self.is_pengpenghu():
            fan_count += 1
        
        # Same color = 2 fan
        if self.is_same_color():
            fan_count += 2
        
        # 7 pairs = 2 fan
        if self.is_seven_pairs(self.hand):
            fan_count += 2
        
        # Every gang = 1 fan
        fan_count += self.gang_count
        
        # Zimo (self-draw) = 1 fan
        if is_zimo:
            fan_count += 1
        
        final_score = base_score * (2 ** fan_count)
        return final_score
    
    def is_pengpenghu(self):
        """
        Check if the hand is all triplets (pengpenghu)
        """
        # Need exactly 4 sets of triplets and 1 pair
        triplet_count = 0
        pair_count = 0
        
        # Count triplets in exposed sets
        triplet_count += len(self.exposed_sets)
        
        # Count triplets and pairs in hand
        counts = {}
        for tile in self.hand:
            counts[tile] = counts.get(tile, 0) + 1
        
        for count in counts.values():
            if count == 2:
                pair_count += 1
            elif count == 3:
                triplet_count += 1
        
        return triplet_count == 4 and pair_count == 1
    
    def is_same_color(self):
        """
        Check if all tiles are of the same suit
        """
        all_tiles = self.hand.copy()
        for sets in self.exposed_sets:
            all_tiles.extend(sets)
        
        suits = {tile[-1] for tile in all_tiles}
        return len(suits) == 1

class MahjongGame:
    def __init__(self):
        self.deck = generate_deck()
        self.players = [Player(f"Player {i+1}", is_ai=True) for i in range(4)]
        self.discards = []
        self.current_round = 0
    
    def determine_dealer(self):
        """
        Determine the dealer based on dice rolls
        """
        self.players.sort(key=lambda x: x.dice_roll, reverse=True)
        return self.players[0]
    
    def deal_tiles(self):
        """
        Initial dealing of tiles
        """
        dealer = self.determine_dealer()
        
        # Initial dealing (4-4-4-1 structure)
        for _ in range(3):
            for player in self.players:
                player.draw_tile(self.deck, 4)
        
        # Last tile for each player
        for player in self.players:
            if player == dealer:
                player.draw_tile(self.deck, 2)  # Dealer gets 14 tiles
            else:
                player.draw_tile(self.deck, 1)  # Others get 13 tiles
        
        # Exchange tiles
        for i in range(4):
            giver = self.players[i]
            receiver = self.players[(i + 1) % 4]
            
            attempts = 0
            success = False
            while attempts < 3 and not success:  # Try up to 3 times
                given, received = giver.exchange_three(receiver)
                if len(given) == 3 and len(received) == 3:
                    success = True
                attempts += 1
        
        # Determine banned suits for each player
        for player in self.players:
            player.determine_banned_suit()
    
    def get_discard_count(self, tile):
        """
        Return how many times a tile has been discarded
        """
        return self.discards.count(tile)
    
    def play_game(self, quiet=False):
        """
        Play a complete game
        Returns the total reward accumulated during the game
        """
        if not quiet:
            print("Game Start: Dealing tiles...")
        
        self.deal_tiles()
        
        if not quiet:
            print("Starting Mahjong Game...")
        
        game_over = False
        current_player_index = 0
        total_game_reward = 0
        
        # Reset player rewards
        for player in self.players:
            player.total_reward = 0
        
        # Maximum number of rounds before game ends
        max_rounds = 250  # This prevents infinite games
        
        while not game_over and self.current_round < max_rounds:
            player = self.players[current_player_index]
            
            if player.is_hu:
                current_player_index = (current_player_index + 1) % 4
                continue
            
            if not self.deck:
                if not quiet:
                    print("No more tiles in deck, game over!")
                break
            
            # Draw tile
            player.draw_tile(self.deck)
            
            # Check for Hu (winning)
            if player.check_hu():
                score = player.calculate_score(is_zimo=True)
                if not quiet:
                    print(f"{player.name} Hu! Final Score: {score}")
                
                player.is_hu = True
                
                # Reward for winning
                if player.rl_agent:
                    reward = player.rl_agent.calculate_reward(player, self, None, hu_achieved=True)
                    player.total_reward += reward
                    total_game_reward += reward
                    
                    # Update Q-table for winning
                    next_state = player.rl_agent.get_state(player, self)
                    player.rl_agent.update_q_table(player, self, next_state, reward, hu_achieved=True)
                
                game_over = True  # Game ends as soon as someone wins
                continue
            
            # Discard tile
            discarded = player.discard_tile(self)
            if discarded:
                self.discards.append(discarded)
                
                # Calculate reward for discard action
                if player.rl_agent:
                    reward = player.rl_agent.calculate_reward(player, self, ("discard", discarded))
                    player.total_reward += reward
                    total_game_reward += reward
                
                # Check if any player can Hu with the discarded tile
                hu_player = None
                for next_player in self.players:
                    if next_player != player and next_player.check_hu_with_tile(discarded):
                        hu_player = next_player
                        break
                
                if hu_player:
                    score = hu_player.calculate_score(is_zimo=False)
                    if not quiet:
                        print(f"{hu_player.name} Hu! Final Score: {score}")
                    
                    hu_player.is_hu = True
                    
                    # Reward for winning
                    if hu_player.rl_agent:
                        reward = hu_player.rl_agent.calculate_reward(hu_player, self, None, hu_achieved=True)
                        hu_player.total_reward += reward
                        total_game_reward += reward
                        
                        # Update Q-table for winning
                        next_state = hu_player.rl_agent.get_state(hu_player, self)
                        hu_player.rl_agent.update_q_table(hu_player, self, next_state, reward, hu_achieved=True)
                    
                    game_over = True  # Game ends as soon as someone wins
                    continue
                
                # Check if any player can Peng
                peng_player = None
                for i in range(1, 4):
                    next_player = self.players[(current_player_index + i) % 4]
                    if next_player.peng(discarded):
                        peng_player = next_player
                        
                        # Reward for peng
                        if next_player.rl_agent:
                            reward = next_player.rl_agent.calculate_reward(next_player, self, ("peng", discarded))
                            next_player.total_reward += reward
                            total_game_reward += reward
                        
                        break
                
                if peng_player:
                    # After Peng, player must discard a tile
                    discarded_after_peng = peng_player.discard_tile(self)
                    if discarded_after_peng:
                        self.discards.append(discarded_after_peng)
                        
                        # Calculate reward for discard after peng
                        if peng_player.rl_agent:
                            reward = peng_player.rl_agent.calculate_reward(peng_player, self, ("discard", discarded_after_peng))
                            peng_player.total_reward += reward
                            total_game_reward += reward
                    
                    continue
            
            # Update RL agent if applicable
            if player.rl_agent:
                next_state = player.rl_agent.get_state(player, self)
                player.rl_agent.update_q_table(player, self, next_state, player.total_reward)
            
            current_player_index = (current_player_index + 1) % 4
            self.current_round += 1
        
        if not quiet:
            print("Game Over!")
            print("Final Results:")
            for player in self.players:
                status = "Hu!" if player.is_hu else "Did not Hu"
                print(f"{player.name}: {status}")
        
        return total_game_reward
    
if __name__ == "__main__":
    game = MahjongGame()
    game.play_game()
