from game_4AI import MahjongGame
from rl_agent import RLAgent
import os

# Ensure models directory exists
os.makedirs("models", exist_ok=True)

# Load the trained agent
rl_agent = RLAgent(q_table_file="models/q_table.pkl", epsilon=0.05)

# Create a new game
game = MahjongGame()

# Set all players as AI with the same RL agent
for player in game.players:
    player.is_ai = True
    player.rl_agent = rl_agent

# Reset agent's tracking data for a new game
rl_agent.reset_for_new_game()

# Play the game
print("Starting a game with all AI players...")
game.play_game(quiet=False)  # Set to False to see detailed output

# Print results
print("\nGame Results:")
for player in game.players:
    status = "Hu! (Won)" if player.is_hu else "Did not Hu"
    print(f"{player.name}: {status}")

# If you want to see AI player's hand at the end
print("\nAI Player's final hand:")
ai_player = game.players[0]
print(ai_player.sorted_hand())
