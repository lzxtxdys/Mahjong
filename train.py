import sys
import os
import time
import random
from rl_agent import RLAgent

# Try to import the 4AI game, fallback to regular if needed
try:
    from game_4AI import MahjongGame
except ImportError:
    print("Warning: game_4AI.py not found, using modified version of game_1AI.py")
    from game_1AI import MahjongGame

# Create directory for logs and models
os.makedirs("logs", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Set up logging
log_filename = "logs/train_enhanced_log.txt"
sys.stdout = open(log_filename, "w")

# Initialize the RL agent with advanced settings
rl_agent = RLAgent(
    alpha=0.15,     # Higher learning rate for faster convergence
    gamma=0.9,      # Discount factor
    epsilon=0.25,   # Balanced exploration/exploitation
    q_table_file="models/q_table.pkl"   # Use default name for compatibility
)

# Training parameters
num_episodes = 50000  # Train for 50k episodes
checkpoint_interval = 5000
log_interval = 1000

# Statistics tracking
wins = {f"Player {i+1}": 0 for i in range(4)}

print(f"Starting enhanced AI training with {num_episodes} episodes")
print(f"Hyperparameters: alpha={rl_agent.alpha}, gamma={rl_agent.gamma}, epsilon={rl_agent.epsilon}")

start_time = time.time()

for episode in range(num_episodes):
    # Initialize game with all AI players
    game = MahjongGame()
    
    # Make all players AI-controlled with the same agent
    for player in game.players:
        player.is_ai = True
        player.rl_agent = rl_agent
    
    # Reset agent for new game
    rl_agent.reset_for_new_game()
    
    try:
        # Play the game
        game.play_game(quiet=True)
        
        # Track wins
        for player in game.players:
            if player.is_hu:
                wins[player.name] += 1
                
    except Exception as e:
        print(f"Error in episode {episode}: {str(e)}")
        continue
    
    # Save checkpoint
    if (episode + 1) % checkpoint_interval == 0:
        checkpoint_file = f"models/q_table_ep{episode+1}.pkl"
        rl_agent.q_table_file = checkpoint_file
        rl_agent.save_q_table()
        rl_agent.q_table_file = "models/q_table_enhanced.pkl"  # Reset to default
    
    # Regular save
    if (episode + 1) % 1000 == 0:
        rl_agent.save_q_table()
    
    # Log progress
    if (episode + 1) % log_interval == 0:
        elapsed_time = time.time() - start_time
        win_rate = sum(wins.values()) / (episode + 1)
        
        print(f"Episode {episode+1}/{num_episodes} ({(episode+1)/num_episodes*100:.1f}%)")
        print(f"Time elapsed: {elapsed_time:.2f} seconds")
        print(f"Current exploration rate (epsilon): {rl_agent.epsilon:.4f}")
        print(f"Win rate: {win_rate:.4f}")
        print(f"Win distribution: {wins}")
        print(f"Q-table entries: {len(rl_agent.q_table)}")
        print("-" * 50)

# Save the final model
rl_agent.save_q_table()

total_time = time.time() - start_time
print(f"\nTraining completed in {total_time:.2f} seconds!")

# Save training results
with open("train_win_results.txt", "w") as f:
    f.write(f"Training Results (Enhanced AI) - {num_episodes} Episodes:\n")
    f.write(f"Total training time: {total_time:.2f} seconds\n")
    f.write(f"Final epsilon: {rl_agent.epsilon:.4f}\n")
    f.write(f"Q-table entries: {len(rl_agent.q_table)}\n\n")
    
    total_wins = sum(wins.values())
    for player, count in wins.items():
        win_percentage = (count / num_episodes) * 100
        f.write(f"{player} wins: {count} ({win_percentage:.2f}%)\n")

sys.stdout.close()
sys.stdout = sys.__stdout__

print(f"Enhanced AI training completed in {total_time:.2f} seconds!")
print(f"Log saved to {log_filename}")
print(f"Results saved to train_win_results.txt")
print(f"Model saved to models/q_table_enhanced.pkl")
