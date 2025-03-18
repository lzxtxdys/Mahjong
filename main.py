from game_4AI import MahjongGame
from rl_agent import RLAgent

# Play a game
game = MahjongGame()

# Mark some players as AI
for i, player in enumerate(game.players):
    if i < 3:  # Make first 3 players AI
        player.is_ai = True
        player.rl_agent = RLAgent()

game.play_game()  # Play one game
