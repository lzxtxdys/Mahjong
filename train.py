import sys
from game_4AI import MahjongGame
from rl_agent import RLAgent


log_filename = "train_log.txt"
sys.stdout = open(log_filename, "w")

rl_agent = RLAgent()

num_episodes = 10000

wins = {f"Player {i+1}": 0 for i in range(4)}

for episode in range(num_episodes):
    game = MahjongGame()
    
    # Make all players AI-controlled
    for player in game.players:
        player.is_ai = True
        player.rl_agent = rl_agent
    game.play_game()

    for player in game.players:
        if player.is_hu:
            wins[player.name] += 1
            break

    # Save the AI's learned strategy
    rl_agent.save_q_table()

    if episode % 100 == 0:
        print(f"Training Episode {episode} completed")

sys.stdout.close()
sys.stdout = sys.__stdout__

win_results_filename = "train_win_results.txt"
with open(win_results_filename, "w") as f:
    f.write(f"Final Win Count After {num_episodes} Training Games:\n")
    for player, count in wins.items():
        f.write(f"{player} Wins: {count}\n")

print(f"Training completed! Log saved to {log_filename}")
print(f"Win results saved to {win_results_filename}")
