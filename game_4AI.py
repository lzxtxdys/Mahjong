import random
from rl_agent import RLAgent

# defining tiles
def generate_deck():
    deck = [f"{num}{suit}" for suit in ["W", "T", "B"] for num in range(1, 10)] * 4
    random.shuffle(deck)
    return deck

# players
class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.hand = []
        self.is_hu = False
        self.dice_roll = random.randint(1, 6) + random.randint(1, 6)
        self.bannned_suit = None
        self.exposed_sets = [] # store exposed sets of tiles
        self.gang_count = 0
        self.is_ai = is_ai

        if self.is_ai:
            self.ai = RLAgent()
    
    def draw_tile(self, deck, count=1):
        for _ in range(count):
            if deck:
                self.hand.append(deck.pop())
        self.sort_hand()
        print(f"{self.name} hand after draw: {self.sorted_hand()}")

    def exchange_three(self, target_player):
        # choose the least but at least 3 tiles of a suit to exchange
        count = self.count_suits()

        # find suits that have more than 3 tiles and sort it by amount
        valid_suits = sorted([(suit, num) for suit, num in count.items() if num >= 3], key=lambda x: x[1])

        # choose the least but at least 3 tiles of a suit to exchange
        if valid_suits:
            chosen_suit = valid_suits[0][0]

        # 检查目标玩家是否有足够的 chosen_suit 进行交换
        target_suit_tiles = [tile for tile in target_player.hand if chosen_suit in tile]
        if len(target_suit_tiles) < 3:
            print(f"{self.name} 无法与 {target_player.name} 交换 {chosen_suit}，因为目标玩家该花色不足 3 张")
            return [], []  # 目标玩家不符合交换条件

        # choose 3 tiles to exchange
        chosen_tiles = random.sample([t for t in self.hand if chosen_suit in t], 3)
        received_tiles = random.sample(target_suit_tiles, 3)

        # exchange tiles
        for tile in chosen_tiles:
            self.hand.remove(tile)
        for tile in received_tiles:
            target_player.hand.remove(tile)

        self.hand.extend(received_tiles)
        target_player.hand.extend(chosen_tiles)

        return chosen_tiles, received_tiles
    
    def determine_banned_suit(self):
        # after exchange, determine the banned suit, it should be the least one. 
        # if there are multiple that have the same amount, then randomly choose one.
        count = self.count_suits()
        sorted_suits = sorted(count.items(), key=lambda x: x[1])

        self.banned_suit = sorted_suits[0][0]

        if len(sorted_suits) > 1 and sorted_suits[0][1] == sorted_suits[1][1]:
            self.banned_suit = random.choice([sorted_suits[0][0], sorted_suits[1][0]])

        print(f"{self.name} bans suit {self.banned_suit}")

    # def discard_tile(self):
    #     """
    #     if the player has tiles of banned suit, they must discard the tiles
    #     if there are no tiles of banned suit, then randomly discard a tile
    #     """
    #     if not self.hand:
    #         return None
        
    #     opponent_analysis = self.analyze_opponents(game)

    #     # if banned tile exist, discard it
    #     banned_tiles = [tile for tile in self.hand if self.banned_suit in tile]
    #     if banned_tiles:
    #         discarded_tile = self.choose_safest_tile(banned_tiles, game, opponent_analysis)
    #         print(f"{self.name} discarded {discarded_tile} (Banned Suit)")
    #         self.hand.remove(discarded_tile)
    #         return discarded_tile
        
    #     tile_scores = self.evaluate_tile_values(game, opponent_analysis)

    #     discarded_tile = min(tile_scores, key=tile_scores.get)
    #     self.hand.remove(discarded_tile)
    #     print(f"{self.name} discarded {discarded_tile} (safer tile)")
    #     return discarded_tile

    # def discard_tile(self, game):
    #     """ use decision tree to discard the tile """
    #     if not self.hand:
    #         return None  # avoid discarding when no tiles left
        
    #     if self.is_ai:
    #         action, tile = self.rl_agent.choose_action(self, game)
    #         if action == "discard":
    #             self.hand.remove(tile)
    #             print(f"{self.name} discarded {tile} (AI Choice)")
    #             return tile
        
    #     else:
    #         opponent_analysis = self.analyze_opponents(game)

    #         # discard banned suit tiles first
    #         banned_tiles = [tile for tile in self.hand if self.banned_suit in tile]
    #         if banned_tiles:
    #             discarded_tile = self.choose_safest_tile(banned_tiles, game, opponent_analysis)
    #             print(f"{self.name} discarded {discarded_tile}(banned suits)")
    #             self.hand.remove(discarded_tile)
    #             return discarded_tile

    #         # decision tree
    #         discard_candidates = self.hand.copy()

    #         # discard single tiles first
    #         single_tiles = [t for t in discard_candidates if self.hand.count(t) == 1]
    #         if single_tiles:
    #             discarded_tile = self.choose_safest_tile(single_tiles, game, opponent_analysis)
    #             print(f"{self.name} discarded {discarded_tile}(single)")
    #             self.hand.remove(discarded_tile)
    #             return discarded_tile

    #         # if there are pair tiles, keep them and check if seven pairs is possible
    #         pair_tiles = [t for t in discard_candidates if self.hand.count(t) == 2]
    #         if pair_tiles:
    #             if self.is_seven_pairs(self.hand):  # if seven pairs is possible, keep the pair
    #                 pass
    #             else:
    #                 discarded_tile = self.choose_safest_tile(pair_tiles, game, opponent_analysis)
    #                 print(f"{self.name} discarded {discarded_tile}(pairs)")
    #                 self.hand.remove(discarded_tile)
    #                 return discarded_tile

    #         # if opponents are likely to make same color, avoid discarding the same color
    #         for opponent_name, strategy in opponent_analysis.items():
    #             if strategy == "maybe same color":
    #                 discard_candidates = [t for t in discard_candidates if t[-1] != self.banned_suit]

    #         # if opponents are likely to make pengpenghu, avoid discarding pairs
    #         for opponent_name, strategy in opponent_analysis.items():
    #             if strategy == "maybe pengpenghu":
    #                 discard_candidates = [t for t in discard_candidates if self.hand.count(t) != 2]

    #         # discard safe tiles only if the rest deck is less than 20
    #         if len(game.deck) < 20:
    #             discard_candidates = sorted(discard_candidates, key=lambda x: game.get_discard_count(x), reverse=True)

    #         # finally choose the safest tile to discard
    #         discarded_tile = self.choose_safest_tile(discard_candidates, game, opponent_analysis)
    #         print(f"{self.name} discarded {discarded_tile}(safest tiles)")
    #         self.hand.remove(discarded_tile)
    #         return discarded_tile

    def discard_tile(self, game):
        """ Use decision tree to discard the tile, prioritizing banned suit tiles first. """
        if not self.hand:
            return None  # Avoid discarding when no tiles are left

        # always discard banend suit first
        banned_tiles = [tile for tile in self.hand if self.banned_suit in tile]
        if banned_tiles:
            discarded_tile = random.choice(banned_tiles)  # Choose any banned tile to discard
            print(f"{self.name} discarded {discarded_tile} (Banned Suit)")
            self.hand.remove(discarded_tile)
            return discarded_tile
        
        # use RL Agent to choose action
        if self.is_ai:
            action, tile = self.rl_agent.choose_action(self, game)
            if action == "discard":
                self.hand.remove(tile)
                print(f"{self.name} discarded {tile} (AI Choice)")
                return tile

        # analyze opponents' play style and guess their target combinations
        opponent_analysis = self.analyze_opponents(game)

        # decision tree logic
        discard_candidates = self.hand.copy()

        # discard single tiles first
        single_tiles = [t for t in discard_candidates if self.hand.count(t) == 1]
        if single_tiles:
            discarded_tile = self.choose_safest_tile(single_tiles, game, opponent_analysis)
            print(f"{self.name} discarded {discarded_tile} (Single)")
            self.hand.remove(discarded_tile)
            return discarded_tile
        
        # discard pairs if seven pairs is not viable
        pair_tiles = [t for t in discard_candidates if self.hand.count(t) == 2]
        if pair_tiles:
            # If seven pairs is viable, keep pairs
            if self.is_seven_pairs(self.hand):
                pass
            else:
                discarded_tile = self.choose_safest_tile(pair_tiles, game, opponent_analysis)
                print(f"{self.name} discarded {discarded_tile} (Pairs)")
                self.hand.remove(discarded_tile)
                return discarded_tile

        # avoid discarding the same color if opponents are likely to make same color
        # avoid discarding pairs if opponents are likely to make pengpenghu
        for opponent_name, strategy in opponent_analysis.items():
            if strategy == "maybe same color":
                discard_candidates = [t for t in discard_candidates if t[-1] != self.banned_suit]
            if strategy == "maybe pengpenghu":
                discard_candidates = [t for t in discard_candidates if self.hand.count(t) != 2]

        # discard safe tiles only if the remaining deck is less than 20
        if len(game.deck) < 20:
            discard_candidates = sorted(discard_candidates, key=lambda x: game.get_discard_count(x), reverse=True)

        # finally, choose the safest tile to discard
        discarded_tile = self.choose_safest_tile(discard_candidates, game, opponent_analysis)
        print(f"{self.name} discarded {discarded_tile} (Safest Tile)")
        self.hand.remove(discarded_tile)
        return discarded_tile

    def choose_safest_tile(self, candidates, game, opponent_analysis):
        safest_tile = candidates[0]
        min_risk = float('inf')

        for tile in candidates:
            risk = self.calculate_risk(tile, game, opponent_analysis)
            if risk < min_risk:
                min_risk = risk
                safest_tile = tile

        return safest_tile

    def evaluate_tile_values(self, game, opponent_analysis):
        tile_scores = {}

        for tile in self.hand:
            score = 0

            # keep pairs as priority
            if self.hand.count(tile) == 2:
                score += 5  # high value for pairs

            # keep straight
            suit = tile[-1]
            num = int(tile[:-1])

            if f"{num-1}{suit}" in self.hand and f"{num+1}{suit}" in self.hand:
                score += 5  # high value for straight
            elif f"{num-1}{suit}" in self.hand or f"{num+1}{suit}" in self.hand:
                score += 3  # medium value for half straight

            # 3 same
            if self.hand.count(tile) == 3:
                score += 7  # highest value for 3 same

            # check exposed and discarded tiles
            score -= game.get_discard_count(tile)  # the tile is safer if it has been discarded more times

            tile_scores[tile] = score

        return tile_scores
    
    def calculate_risk(self, tile, game, opponent_analysis):
        """
        calculate the risk of discarding a tile:
        - if another player needs this tile, they might win
        - refer to other players' discard habits to avoid giving away points
        """
        risk = 0

        for opponent_name, strategy in opponent_analysis.items():
            if strategy == "maybe same color":
                if tile[-1] in {t[-1] for t in self.hand}:  # tile for same color
                    risk += 5

            elif strategy == "maybe pengpenghu":
                if self.hand.count(tile) == 2:  # tile is pair
                    risk += 5

            elif strategy == "可能在做七对":
                if self.hand.count(tile) == 1:  # tile is single
                    risk += 5

        risk -= game.get_discard_count(tile)  # the tile is safer if it has been discarded more times
        return risk

    def check_hu_with_tile(self, tile):
        """ Check if the player can win with the given tile. """
        temp_hand = self.hand.copy()
        temp_hand.append(tile)
        return self.is_seven_pairs(temp_hand) or self.is_regular_hu(temp_hand)

    def analyze_opponents(self, game):
        """ 
        analyze opponents' play style and guess their target combinations:
        - If a player only discards 1~2 suits, they may be going for same color
        - If a player frequently pengs/gangs, they may be going for pengpenghu
        - If a player rarely pengs, they may be going for seven pairs
        """
        player_analysis = {}

        for opponent in game.players:
            if opponent == self:
                continue  # not analyze self

            # check the suits of the opponent's hand
            discard_suits = {tile[-1] for tile in opponent.hand}
            exposed_suits = {tile[-1] for peng in opponent.exposed_sets for tile in peng}

            # check the strategy of the opponent
            strategy = "Unknown"

            if len(discard_suits) == 1 and len(exposed_suits) <= 1:
                strategy = "maybe same color"

            elif len(opponent.exposed_sets) >= 2:
                strategy = "maybe pengpenghu"

            elif all(opponent.hand.count(tile) == 2 for tile in opponent.hand):
                strategy = "maybe seven pairs"

            player_analysis[opponent.name] = strategy

        return player_analysis

    def peng(self, tile):
        """ AI decides whether to Peng a tile. If it's from the banned suit, Peng is not allowed. """
        if self.hand.count(tile) >= 2:
            if tile.endswith(self.banned_suit):  # ✅ Prevent Peng if tile is in banned suit
                print(f"{self.name} chose NOT to Peng {tile} (Banned Suit)")
                return False  # Do not Peng
            
            # If tile is not in banned suit, Peng is allowed
            self.hand.remove(tile)
            self.hand.remove(tile)
            self.exposed_sets.append([tile, tile, tile])  # Add Peng to exposed sets
            print(f"{self.name} Peng {tile}")
            return True  # Peng success
        
        return False  # No Peng

    
    def is_seven_pairs(self, hand):
        if len(hand) != 14:
            return False
        
        counts = {}
        for tile in hand:
            counts[tile] = counts.get(tile, 0) + 1

        return all(count == 2 for count in counts.values())
    
    def is_regular_hu(self, hand):
        if len(hand) != 14:
            return False
        
        counts = {}
        for tile in hand:
            counts[tile] = counts.get(tile, 0) + 1

        pairs = [tile for tile, count in counts.items() if count >= 2]

        for pair in pairs:
            temp_counts = counts.copy()
            temp_counts[pair] -= 2

            if self.can_form_melds(temp_counts):
                return True
        
        return False
    
    def is_pengpenghu(self):
        counts = {}
        for tile in self.hand:
            counts[tile] = counts.get(tile, 0) + 1

        triplet_count = sum(1 for count in counts.values() if count == 3)
        pair_count = sum(1 for count in counts.values() if count == 2)

        return triplet_count == 4 and pair_count == 1
    
    def is_same_color(self):
        suits = {tile[-1] for tile in self.hand}
        return len(suits) == 1
    
    def can_form_melds(self, counts):
        remaining_tiles = [tile for tile, count in counts.items() if count > 0]

        if not remaining_tiles:
            return True

        first_tile = remaining_tiles[0]

        # Try to form AAA
        if counts[first_tile] >= 3:
            counts[first_tile] -= 3
            if self.can_form_melds(counts):
                return True
            counts[first_tile] += 3

        # ABC
        suit = first_tile[-1]
        if all(f"{int(first_tile[0]) + i}{suit}" in counts and counts[f"{int(first_tile[0]) + i}{suit}"] > 0 for i in range(3)):
            for i in range(3):
                counts[f"{int(first_tile[0]) + i}{suit}"] -= 1
            if self.can_form_melds(counts):
                return True
            for i in range(3):
                counts[f"{int(first_tile[0]) + i}{suit}"] += 1

        return False

    def sort_hand(self):
        self.hand.sort()
    
    def sorted_hand(self):
        tiles_wan = sorted([t for t in self.hand if "W" in t])
        tiles_bing = sorted([t for t in self.hand if "B" in t])
        tiles_tiao = sorted([t for t in self.hand if "T" in t])

        peng_str = f" | PENG: {self.exposed_sets}" if self.exposed_sets else ""
        return f"({tiles_wan}) ({tiles_bing}) ({tiles_tiao}){peng_str}"
    
    def count_suits(self):
        count = {"W": 0, "B": 0, "T": 0}
        for tile in self.hand:
            suit = tile[-1]
            count[suit] += 1
        return count
    
    def check_hu(self):
        if self.bannned_suit and any(self.bannned_suit in tile for tile in self.hand):
            print(f"{self.name} has banned suit {self.bannned_suit}, cannot Hu!")
            return False
        
        sorted_hand = sorted(self.hand)

        if self.is_seven_pairs(sorted_hand):
            print(f"{self.name} has seven pairs!")
            self.is_hu = True
            return True
        
        if self.is_regular_hu(sorted_hand):
            print(f"{self.name} has a regular Hu!")
            self.is_hu = True
            return True
        
        return False
    
    def calculate_score(self, is_zimo=False):
        # calculate score
        # function: 1 * 2^(fan_count)
        # basic hu = 1 score
        # pengpenghu = 1 fan
        # same_color = 2 fan
        # 7 pairs = 2 fan
        # zimo = 1 fan
        # every gang = 1 fan
        base_score = 1
        fan_count = 0

        # pengpenghu 1 fan
        if self.is_pengpenghu():
            fan_count += 1
        
        # same color 2 fan
        if self.is_same_color():
            fan_count += 2
        
        # 7 pairs 2 fan
        if self.is_seven_pairs(self.hand):
            fan_count += 2
        
        # every gang 1 fan
        fan_count += self.gang_count

        # zimo 1 fan
        if is_zimo:
            fan_count += 1

        final_score = base_score * (2 ** fan_count)

        print(f"!!!!!!!!!!!!!!!{self.name} hu! final score: {final_score}!!!!!!!!!!!!!!")
        return final_score


# game
class MahjongGame:
    def __init__(self):
        self.deck = generate_deck()
        self.players = [Player(f"Player {i+1}") for i in range(4)]
        self.discards = []
    
    def determine_dealer(self):
        self.players.sort(key=lambda x: x.dice_roll, reverse=True)
        return self.players[0]
    
    def deal_tiles(self):
        print("Rolling dice to determine dealer...")
        for player in self.players:
            print(f"{player.name} rolled {player.dice_roll}")

        dealer = self.determine_dealer()
        print(f"Dealer is {dealer.name} since they rolled the highest")

        # Initial dealing (4-4-4-1 structure)
        for _ in range(3):
            for player in self.players:
                player.draw_tile(self.deck, 4)

        for player in self.players:
            if player == dealer:
                player.draw_tile(self.deck, 2)  # Dealer gets 14 tiles
            else:
                player.draw_tile(self.deck, 1)  # Others get 13 tiles

        print("\nInitial hands:")
        for player in self.players:
            print(f"{player.name}: {player.sorted_hand()} (Total: {len(player.hand)})")

        # Players exchange three tiles
        print("\nStarting tile exchange process...")
        for i in range(4):
            giver = self.players[i]
            receiver = self.players[(i + 1) % 4]  # Circular exchange

            given, received = giver.exchange_three(receiver)

            if len(given) == 3 and len(received) == 3:
                print(f"{giver.name} gives {given} to {receiver.name}")
                print(f"{giver.name} receives {received}")
            else:
                print(f"Exchange failed between {giver.name} and {receiver.name}, retrying...")

                # Retry until exchange succeeds
                while len(given) != 3 or len(received) != 3:
                    given, received = giver.exchange_three(receiver)
                    break
                    if len(given) == 3 and len(received) == 3:
                        print(f"Retry successful: {giver.name} gives {given} to {receiver.name} and receives {received}")
                        break

        print("\nHands after exchange:")
        for player in self.players:
            print(f"{player.name}: {player.sorted_hand()} (Total: {len(player.hand)})")

        print("\nChoosing banned suits...")
        for player in self.players:
            player.determine_banned_suit()

        # Final check: Dealer must have 14 tiles, others 13
        for player in self.players:
            expected_tiles = 14 if player == dealer else 13
            assert len(player.hand) == expected_tiles, f"ERROR: {player.name} has {len(player.hand)} tiles instead of {expected_tiles}!"

    def print_exposed_and_discarded_tiles(self):
        """ Print all exposed (peng) and discarded tiles, categorized by suit and sorted numerically. """

        # Helper function to sort tiles within each suit
        def categorize_and_sort(tile_dict):
            categorized = {"W": [], "B": [], "T": []}
            for tile, count in tile_dict.items():
                suit = tile[-1]
                categorized[suit].extend([tile] * count)

            # Sort numerically within each suit
            for suit in categorized:
                categorized[suit].sort(key=lambda x: int(x[:-1]))  # Sort by number

            return categorized

        # Count all exposed tiles (peng sets)
        exposed_counts = {}
        for player in self.players:
            for peng_set in player.exposed_sets:
                for tile in peng_set:
                    exposed_counts[tile] = exposed_counts.get(tile, 0) + 1

        # Count all discarded tiles
        discard_counts = {}
        for tile in self.discards:
            discard_counts[tile] = discard_counts.get(tile, 0) + 1

        # Categorize and sort
        sorted_exposed = categorize_and_sort(exposed_counts)
        sorted_discarded = categorize_and_sort(discard_counts)

        print(f"Exposed Tiles: {sorted_exposed}")
        print(f"Discarded Tiles: {sorted_discarded}")

    def get_discard_count(self, tile):
        """ Return how many times a tile has been discarded """
        return self.discards.count(tile)
    
    def play_game(self):
        print("                                  ")
        print("Game Start: Dealing tiles...")
        self.deal_tiles()
        
        print("Starting Mahjong Game...")
        game_over = False
        current_player_index = 0
        
        while not game_over:
            player = self.players[current_player_index]
            
            if player.is_hu:
                current_player_index = (current_player_index + 1) % 4
                continue

            if not self.deck:
                print("No more tiles in deck, game over!")
                break
            
            print(f"{player.name} drawing tile, tile is {self.deck[-1]} (Remaining: {len(self.deck)-1})")
            player.draw_tile(self.deck)
            
            if player.check_hu():
                score = player.calculate_score(is_zimo=True)
                print(f"{player.name} Hu! 🀄 Final Score: {score}")
                player.is_hu = True
                if sum(p.is_hu for p in self.players) == 3:
                    game_over = True
                continue
            
            discarded = player.discard_tile(self)
            if discarded:
                print(f"{player.name} hand after discard: {player.sorted_hand()}")
                self.print_exposed_and_discarded_tiles()
                print("                           ")
                self.discards.append(discarded)

                hu_player = None
                for next_player in self.players:
                    if next_player != player and next_player.check_hu_with_tile(discarded):
                        hu_player = next_player
                        break

                if hu_player:
                    score = hu_player.calculate_score(is_zimo=False)
                    print(f"{hu_player.name} Hu! 🀄 Final Score: {score}")
                    hu_player.is_hu = True
                    if sum(p.is_hu for p in self.players) == 3:
                        game_over = True
                    continue

                peng_player = None
                for i in range(1, 4):
                    next_player = self.players[(current_player_index + i) % 4]
                    if next_player.peng(discarded):
                        peng_player = next_player
                        break

                if peng_player:
                    discarded_after_peng = peng_player.discard_tile(self)
                    if discarded_after_peng:
                        print(f"{peng_player.name} hand after discard: {peng_player.sorted_hand()}")
                        self.print_exposed_and_discarded_tiles()
                        print("                           ")
                        self.discards.append(discarded_after_peng)

                    # current_player_index = self.players.index(peng_player)
                    continue
            
            if not self.deck:
                print("No more tiles in deck, game over!")
                break
            
            current_player_index = (current_player_index + 1) % 4
        
        print("Game Over!")
        print("Final Results:")
        for player in self.players:
            status = "Hu! 🀄" if player.is_hu else "Did not Hu"
            print(f"{player.name}: {status}")
        
if __name__ == "__main__":
    game = MahjongGame()
    game.play_game()
