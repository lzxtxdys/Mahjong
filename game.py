import random

# defining tiles
def generate_deck():
    deck = [f"{num}{suit}" for suit in ["W", "T", "B"] for num in range(1, 10)] * 4
    random.shuffle(deck)
    return deck

# players
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.is_hu = False
        self.dice_roll = random.randint(1, 6) + random.randint(1, 6)
        self.bannned_suit = None
        self.exposed_sets = [] # store exposed sets of tiles
        self.gang_count = 0
    
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

    def discard_tile(self):
        """
        if the player has tiles of banned suit, they must discard the tiles
        if there are no tiles of banned suit, then randomly discard a tile
        """
        if not self.hand:
            return None

        # if banned tile exist, discard it**
        banned_tiles = [tile for tile in self.hand if self.banned_suit in tile]
        if banned_tiles:
            discarded_tile = random.choice(banned_tiles)
        else:
            # if no banned tile, discard randomly
            discarded_tile = random.choice(self.hand)

        self.hand.remove(discarded_tile)
        print(f"{self.name} discarded {discarded_tile}")
        return discarded_tile

    def peng(self, tile):
        if self.hand.count(tile) >= 2:
            self.hand.remove(tile)
            self.hand.remove(tile)
            self.exposed_sets.append([tile, tile, tile])
            print(f"{self.name} Peng {tile}")
            return True
        return False
    
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
        if self.is_seven_pairs():
            fan_count += 2
        
        # every gang 1 fan
        fan_count += self.gang_count

        # zimo 1 fan
        if is_zimo:
            fan_count += 1

        final_score = base_score * (2 ** fan_count)

        print(f"{self.name} hu! final score: {final_score}")
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

        # Players exchange three tiles**
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

        #Final check: Dealer must have 14 tiles, others 13**
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

    def play_game(self):
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
            
            print(f"{player.name} drawing tile, tile is {self.deck[-1]} (Remaining: {len(self.deck)-1})")
            player.draw_tile(self.deck)
            
            if player.check_hu():
                score = player.calculate_score(is_zimo=True)
                print(f"{player.name} Hu! 🀄 Final Score: {score}")
                player.is_hu = True
                if sum(p.is_hu for p in self.players) == 3:
                    game_over = True
                continue
            
            discarded = player.discard_tile()
            if discarded:
                print(f"{player.name} hand after discard: {player.sorted_hand()}")
                self.print_exposed_and_discarded_tiles()
                print("                           ")
                self.discards.append(discarded)

                peng_player = None
                for i in range(1, 4):
                    next_player = self.players[(current_player_index + i) % 4]
                    if next_player.peng(discarded):
                        peng_player = next_player
                        break

                if peng_player:
                    discarded_after_peng = peng_player.discard_tile()
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
