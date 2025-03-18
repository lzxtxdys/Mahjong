from game_1AI import MahjongGame
import sys

log_filename = "1AI_log.txt"
sys.stdout = open(log_filename, "w")

num_games = 10000
wins = {f"Player {i+1}": 0 for i in range(4)}

for episode in range(num_games):
    game = MahjongGame()
    game.play_game()

    # Check which player won
    for player in game.players:
        if player.is_hu:
            wins[player.name] += 1
            break

    if episode % 100 == 0:
        print(f"Game {episode} completed...")

print("\nFinal Win Count After", num_games, "Games:")
for player, count in wins.items():
    print(f"{player} Wins: {count}")

with open("ai_win_rate.txt", "w") as f:
    f.write(f"Final Win Count After {num_games} Games:\n")
    for player, count in wins.items():
        f.write(f"{player} Wins: {count}\n")

sys.stdout.close()
sys.stdout = sys.__stdout__

print("Results saved to ai_win_rate.txt")
print("Log saved to", log_filename)
