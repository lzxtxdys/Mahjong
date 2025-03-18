from game_4AI import MahjongGame
from rl_agent import RLAgent

game = MahjongGame()

for i, player in enumerate(game.players):
    if i < 3:
        player.is_ai = True
        player.rl_agent = RLAgent()

game.play_game()
