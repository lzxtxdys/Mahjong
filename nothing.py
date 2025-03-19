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

    # def discard_tile(self, game):
    #     """ Use decision tree to discard the tile, prioritizing banned suit tiles first. """
    #     if not self.hand:
    #         return None  # Avoid discarding when no tiles are left

    #     # **2️⃣ Always Discard Banned Suit First**
    #     banned_tiles = [tile for tile in self.hand if self.banned_suit in tile]
    #     if banned_tiles:
    #         discarded_tile = random.choice(banned_tiles)  # Choose any banned tile to discard
    #         print(f"{self.name} discarded {discarded_tile} (Banned Suit)")
    #         self.hand.remove(discarded_tile)
    #         return discarded_tile
        
    #     # **1️⃣ AI Uses RL Agent for Decision Making**
    #     if self.is_ai:
    #         action, tile = self.rl_agent.choose_action(self, game)
    #         if action == "discard":
    #             self.hand.remove(tile)
    #             print(f"{self.name} discarded {tile} (AI Choice)")
    #             return tile

    #     # **3️⃣ Analyze Opponent Strategies for Smarter Discarding**
    #     opponent_analysis = self.analyze_opponents(game)

    #     # **4️⃣ Decision Tree Logic:**
    #     discard_candidates = self.hand.copy()

    #     # **4.1. Discard Single Tiles First**
    #     single_tiles = [t for t in discard_candidates if self.hand.count(t) == 1]
    #     if single_tiles:
    #         discarded_tile = self.choose_safest_tile(single_tiles, game, opponent_analysis)
    #         print(f"{self.name} discarded {discarded_tile} (Single)")
    #         self.hand.remove(discarded_tile)
    #         return discarded_tile

    #     # **4.2. Discard Pairs If Seven Pairs Is Not Viable**
    #     pair_tiles = [t for t in discard_candidates if self.hand.count(t) == 2]
    #     if pair_tiles:
    #         if self.is_seven_pairs(self.hand):  # If seven pairs is viable, keep pairs
    #             pass
    #         else:
    #             discarded_tile = self.choose_safest_tile(pair_tiles, game, opponent_analysis)
    #             print(f"{self.name} discarded {discarded_tile} (Pairs)")
    #             self.hand.remove(discarded_tile)
    #             return discarded_tile

    #     # **4.3. Avoid Giving Opponents Good Tiles**
    #     for opponent_name, strategy in opponent_analysis.items():
    #         if strategy == "maybe same color":
    #             discard_candidates = [t for t in discard_candidates if t[-1] != self.banned_suit]
    #         if strategy == "maybe pengpenghu":
    #             discard_candidates = [t for t in discard_candidates if self.hand.count(t) != 2]

    #     # **4.4. Prioritize Safe Discards If Deck Is Running Low**
    #     if len(game.deck) < 20:
    #         discard_candidates = sorted(discard_candidates, key=lambda x: game.get_discard_count(x), reverse=True)

    #     # **5️⃣ Choose the Safest Tile to Discard**
    #     discarded_tile = self.choose_safest_tile(discard_candidates, game, opponent_analysis)
    #     print(f"{self.name} discarded {discarded_tile} (Safest Tile)")
    #     self.hand.remove(discarded_tile)
    #     return discarded_tile