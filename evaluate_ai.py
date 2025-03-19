import sys
import os
import time
from rl_agent import RLAgent
try:
    from game_1AI import MahjongGame
except ImportError:
    from game_1AI import MahjongGame

# Create directory for logs
os.makedirs("logs", exist_ok=True)

# Set up logging
log_filename = "logs/eval_enhanced_log.txt"
sys.stdout = open(log_filename, "w")

# Load the trained RL agent
rl_agent = RLAgent(
    q_table_file="models/q_table.pkl",  # Use default name for compatibility
    epsilon=0.05  # Low exploration rate for evaluation
)

# Evaluation parameters
num_games = 10000
checkpoint_interval = 1000

# Statistics tracking
wins = {f"Player {i+1}": 0 for i in range(4)}
game_lengths = []
total_rounds = 0
draws = 0  # Games with no winner

print(f"Starting evaluation of Enhanced AI with {num_games} games")
print(f"Using RL agent with epsilon={rl_agent.epsilon}")

start_time = time.time()

for game_num in range(num_games):
    game = MahjongGame()
    
    # Player 1 is our enhanced AI
    game.players[0].is_ai = True
    game.players[0].rl_agent = rl_agent
    
    # Reset agent's tracking for the new game
    rl_agent.reset_for_new_game()
    
    try:
        # Play the game
        game.play_game(quiet=True)
        
        # Track game statistics
        total_rounds += game.current_round
        game_lengths.append(game.current_round)
        
        # Track wins
        winner_found = False
        for player in game.players:
            if player.is_hu:
                wins[player.name] += 1
                winner_found = True
        
        if not winner_found:
            draws += 1
            
    except Exception as e:
        print(f"Error in game {game_num+1}: {str(e)}")
        continue
    
    # Log progress at intervals
    if (game_num + 1) % checkpoint_interval == 0:
        elapsed_time = time.time() - start_time
        games_completed = game_num + 1
        
        # Calculate win rates
        win_rate_ai = (wins["Player 1"] / games_completed) * 100
        random_win_rates = [(wins[f"Player {i+1}"] / games_completed) * 100 for i in range(1, 4)]
        avg_random_win_rate = sum(random_win_rates) / 3
        
        # Calculate other statistics
        average_game_length = sum(game_lengths) / len(game_lengths) if game_lengths else 0
        completion_rate = 100 - (draws / games_completed * 100)
        
        print(f"Game {games_completed}/{num_games} ({games_completed/num_games*100:.1f}%)")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        print(f"AI win rate: {win_rate_ai:.2f}%")
        print(f"Random players avg win rate: {avg_random_win_rate:.2f}%")
        print(f"AI advantage: {win_rate_ai - avg_random_win_rate:.2f}%")
        print(f"Average game length: {average_game_length:.1f} rounds")
        print(f"Game completion rate: {completion_rate:.2f}%")
        print(f"Win distribution: {wins}")
        print("-" * 50)

total_time = time.time() - start_time
games_completed = num_games

# Calculate final statistics
win_rate_ai = (wins["Player 1"] / games_completed) * 100
random_win_rates = [(wins[f"Player {i+1}"] / games_completed) * 100 for i in range(1, 4)]
avg_random_win_rate = sum(random_win_rates) / 3
advantage = win_rate_ai - avg_random_win_rate
average_game_length = sum(game_lengths) / len(game_lengths) if game_lengths else 0
completion_rate = 100 - (draws / games_completed * 100)

print(f"\nEvaluation completed in {total_time:.2f} seconds!")

# Detailed statistics report
print("\nFinal Statistics:")
print(f"Games played: {games_completed}")
print(f"Games with winner: {games_completed - draws} ({completion_rate:.2f}%)")
print(f"Total rounds: {total_rounds}")
print(f"Average game length: {average_game_length:.1f} rounds")
print(f"AI win rate: {win_rate_ai:.2f}%")
print(f"Random players average win rate: {avg_random_win_rate:.2f}%")
print(f"AI advantage: {advantage:.2f}%")
print(f"Full win distribution: {wins}")

# Save results to file
with open("ai_win_rate.txt", "w") as f:
    f.write(f"Final Win Count After {games_completed} Games:\n")
    for player, count in wins.items():
        win_percentage = (count / games_completed) * 100
        f.write(f"{player} Wins: {count} ({win_percentage:.2f}%)\n")
    
    f.write(f"\nPerformance Analysis:\n")
    f.write(f"AI win rate: {win_rate_ai:.2f}%\n")
    f.write(f"Random players avg win rate: {avg_random_win_rate:.2f}%\n")
    f.write(f"AI advantage: {advantage:.2f}%\n")
    f.write(f"Average game length: {average_game_length:.1f} rounds\n")
    f.write(f"Game completion rate: {completion_rate:.2f}%\n")

sys.stdout.close()
sys.stdout = sys.__stdout__

print("Evaluation of Enhanced AI completed!")
print(f"Log saved to {log_filename}")
print(f"Results saved to ai_win_rate.txt")
