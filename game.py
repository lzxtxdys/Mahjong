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
    
    def draw_tile(self, deck, count=1):
        for _ in range(count):
            if deck:
                self.hand.append(deck.pop())
        self.sort_hand()
        print(f"{self.name} hand after draw: {self.sorted_hand()}")
    
    def discard_tile(self):
        if not self.hand:
            return None  # avoid using pop while hand is empty
        return self.hand.pop(random.randint(0, len(self.hand) - 1))
    
    def check_hu(self):
        if random.random() < 0.1:
            self.is_hu = True
        return self.is_hu
    
    def sort_hand(self):
        self.hand.sort()
    
    def sorted_hand(self):
        tiles_wan = sorted([t for t in self.hand if "W" in t])
        tiles_bing = sorted([t for t in self.hand if "B" in t])
        tiles_tiao = sorted([t for t in self.hand if "T" in t])
        return f"({tiles_wan}) ({tiles_bing}) ({tiles_tiao})"
    
    def exchange_three(self, target_player):
        suits = ["W", "B", "T"]
        chosen_suit = None

        for suit in suits:
            same_suit_tiles = [tile for tile in self.hand if suit in tile]
            target_suit_tiles = [tile for tile in target_player.hand if suit in tile]
            if len(same_suit_tiles) >= 3 and len(target_suit_tiles) >= 3:
                chosen_suit = suit
                break

        if chosen_suit is None:
            return [], []  # If no valid suit found, no exchange happens

        chosen_tiles = random.sample([tile for tile in self.hand if chosen_suit in tile], 3)
        received_tiles = random.sample([tile for tile in target_player.hand if chosen_suit in tile], 3)

        # Remove exchanged tiles from both players
        for tile in chosen_tiles:
            self.hand.remove(tile)
        for tile in received_tiles:
            target_player.hand.remove(tile)

        # Add exchanged tiles to both players
        self.hand.extend(received_tiles)
        target_player.hand.extend(chosen_tiles)

        return chosen_tiles, received_tiles

    
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

        # **New: Players exchange three tiles**
        print("\nStarting tile exchange process...")
        for i in range(4):
            giver = self.players[i]
            receiver = self.players[(i + 1) % 4]  # Circular exchange

            given, received = giver.exchange_three(receiver)

            if len(given) == 3 and len(received) == 3:
                print(f"{giver.name} gives {given} to {receiver.name} and receives {received}")
            else:
                print(f"Exchange failed between {giver.name} and {receiver.name}, retrying...")

                # Retry until exchange succeeds
                while len(given) != 3 or len(received) != 3:
                    given, received = giver.exchange_three(receiver)
                    if len(given) == 3 and len(received) == 3:
                        print(f"Retry successful: {giver.name} gives {given} to {receiver.name} and receives {received}")
                        break

        print("\nHands after exchange:")
        for player in self.players:
            print(f"{player.name}: {player.sorted_hand()} (Total: {len(player.hand)})")

        # **Final check: Dealer must have 14 tiles, others 13**
        for player in self.players:
            expected_tiles = 14 if player == dealer else 13
            assert len(player.hand) == expected_tiles, f"ERROR: {player.name} has {len(player.hand)} tiles instead of {expected_tiles}!"



    
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
            
            print(f"{player.name} drawing tile, tile is {self.deck[-1]}")
            player.draw_tile(self.deck)
            
            if player.check_hu():
                print(f"{player.name} Hu! 🀄")
                player.is_hu = True
                if sum(p.is_hu for p in self.players) == 3:
                    game_over = True
                continue
            
            discarded = player.discard_tile()
            if discarded:
                print(f"{player.name} discarded {discarded}")
                self.discards.append(discarded)
            
            current_player_index = (current_player_index + 1) % 4
        
        print("Game Over!")
        print("Final Results:")
        for player in self.players:
            status = "Hu! 🀄" if player.is_hu else "Did not Hu"
            print(f"{player.name}: {status}")
        
if __name__ == "__main__":
    game = MahjongGame()
    game.play_game()
