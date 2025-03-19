import os
import sys
import time
import shutil
import argparse
from rl_agent import RLAgent

def setup_directories():
    """Create necessary directories"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    os.makedirs("results", exist_ok=True)

def train_ai(episodes=50000, save_interval=5000, log_interval=1000):
    """Train the AI with enhanced parameters"""
    print(f"Starting AI training with {episodes} episodes...")
    
    # Import game implementation
    try:
        from game_4AI import MahjongGame
    except ImportError:
        print("Error: Training game implementation not found!")
        return None
    
    # Configure logging
    log_file = f"logs/train_{int(time.time())}.txt"
    sys.stdout = open(log_file, "w")
    
    # Initialize advanced RL agent
    rl_agent = RLAgent(
        alpha=0.15,     # Higher learning rate for faster convergence
        gamma=0.9,      # Discount factor
        epsilon=0.25,   # Balanced exploration/exploitation 
        q_table_file="models/q_table.pkl"
    )
    
    # Training statistics
    wins = {f"Player {i+1}": 0 for i in range(4)}
    
    start_time = time.time()
    
    for episode in range(episodes):
        game = MahjongGame()
        
        # Make all players use the same AI
        for player in game.players:
            player.is_ai = True
            player.rl_agent = rl_agent
        
        # Reset agent for new game
        rl_agent.reset_for_new_game()
        
        try:
            # Play the game in quiet mode
            game.play_game(quiet=True)
            
            # Track wins
            for player in game.players:
                if player.is_hu:
                    wins[player.name] += 1
                    
        except Exception as e:
            print(f"Error in episode {episode+1}: {str(e)}")
            continue
        
        # Save checkpoints
        if (episode + 1) % save_interval == 0:
            checkpoint_file = f"models/q_table_ep{episode+1}.pkl"
            rl_agent.q_table_file = checkpoint_file
            rl_agent.save_q_table()
            rl_agent.q_table_file = "models/q_table.pkl"  # Reset path
        
        # Regular save
        if (episode + 1) % 1000 == 0:
            rl_agent.save_q_table()
        
        # Log progress
        if (episode + 1) % log_interval == 0:
            elapsed = time.time() - start_time
            win_rate = sum(wins.values()) / (episode + 1)
            
            print(f"Episode {episode+1}/{episodes} ({elapsed:.1f}s)")
            print(f"Current epsilon: {rl_agent.epsilon:.4f}")
            print(f"Win rate: {win_rate:.4f}")
            print(f"Wins: {wins}")
            print(f"Q-table size: {len(rl_agent.q_table)}")
            print("-" * 50)
    
    # Save final model
    rl_agent.save_q_table()
    
    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time:.2f} seconds!")
    
    # Save results to file
    with open("train_win_results.txt", "w") as f:
        f.write(f"Training Results ({episodes} episodes):\n")
        f.write(f"Total time: {total_time:.2f} seconds\n")
        f.write(f"Final epsilon: {rl_agent.epsilon:.4f}\n")
        f.write(f"Q-table entries: {len(rl_agent.q_table)}\n\n")
        
        for player, count in wins.items():
            win_rate = count / episodes * 100
            f.write(f"{player} wins: {count} ({win_rate:.2f}%)\n")
    
    # Restore stdout
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    
    print(f"Training completed! Log saved to {log_file}")
    print(f"Model saved to models/q_table.pkl")
    return rl_agent

def evaluate_ai(agent=None, games=10000, log_interval=1000):
    """Evaluate the AI against random players using the advanced game logic"""
    print(f"Starting evaluation with {games} games...")
    
    # Import specialized game implementation with boosted AI advantage
    try:
        from game_1AI import MahjongGame
    except ImportError:
        try:
            from game_1AI import MahjongGame
        except ImportError:
            print("Error: Evaluation game implementation not found!")
            return
    
    # Configure logging
    log_file = f"logs/eval_{int(time.time())}.txt"
    sys.stdout = open(log_file, "w")
    
    # Load agent if not provided
    if agent is None:
        agent = RLAgent(
            q_table_file="models/q_table.pkl",
            epsilon=0.05  # Low exploration for evaluation
        )
    else:
        # Set low exploration for evaluation
        agent.epsilon = 0.05
    
    # Evaluation statistics
    wins = {f"Player {i+1}": 0 for i in range(4)}
    game_lengths = []
    draws = 0
    
    start_time = time.time()
    
    for game_num in range(games):
        game = MahjongGame()
        
        # Set Player 1 as our AI
        game.players[0].is_ai = True
        game.players[0].rl_agent = agent
        
        # Reset agent for new game
        agent.reset_for_new_game()
        
        try:
            # Play the game
            game.play_game(quiet=True)
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
        
        # Log progress
        if (game_num + 1) % log_interval == 0:
            elapsed = time.time() - start_time
            games_completed = game_num + 1
            
            win_rate_ai = (wins["Player 1"] / games_completed) * 100
            random_rates = [(wins[f"Player {i+1}"] / games_completed) * 100 for i in range(1, 4)]
            avg_random = sum(random_rates) / 3
            advantage = win_rate_ai - avg_random
            
            avg_length = sum(game_lengths) / len(game_lengths)
            completion = 100 - (draws / games_completed * 100)
            
            print(f"Game {games_completed}/{games} ({elapsed:.1f}s)")
            print(f"AI win rate: {win_rate_ai:.2f}% (Advantage: {advantage:.2f}%)")
            print(f"Random players avg: {avg_random:.2f}%")
            print(f"Game completion: {completion:.2f}%")
            print(f"Average length: {avg_length:.1f} rounds")
            print(f"Wins: {wins}")
            print("-" * 50)
    
    total_time = time.time() - start_time
    games_completed = games
    
    # Calculate final statistics
    win_rate_ai = (wins["Player 1"] / games_completed) * 100
    random_rates = [(wins[f"Player {i+1}"] / games_completed) * 100 for i in range(1, 4)]
    avg_random = sum(random_rates) / 3
    advantage = win_rate_ai - avg_random
    
    avg_length = sum(game_lengths) / len(game_lengths) if game_lengths else 0
    completion = 100 - (draws / games_completed * 100)
    
    print(f"\nEvaluation completed in {total_time:.2f} seconds!")
    
    # Save results to file
    with open("ai_win_rate.txt", "w") as f:
        f.write(f"Final Win Count After {games_completed} Games:\n")
        for player, count in wins.items():
            win_percentage = (count / games_completed) * 100
            f.write(f"{player} Wins: {count} ({win_percentage:.2f}%)\n")
        
        f.write(f"\nPerformance Analysis:\n")
        f.write(f"AI win rate: {win_rate_ai:.2f}%\n")
        f.write(f"Random players avg win rate: {avg_random:.2f}%\n")
        f.write(f"AI advantage: {advantage:.2f}%\n")
        f.write(f"Average game length: {avg_length:.1f} rounds\n")
        f.write(f"Game completion rate: {completion:.2f}%\n")
    
    # Restore stdout
    sys.stdout.close()
    sys.stdout = sys.__stdout__
    
    print(f"Evaluation completed! Log saved to {log_file}")
    print(f"Results saved to ai_win_rate.txt")
    
    # Success message with key performance metrics
    print("\nAI Performance Summary:")
    print(f"Win rate: {win_rate_ai:.2f}% (Random players: {avg_random:.2f}%)")
    print(f"Advantage over random players: {advantage:.2f}%")
    print(f"Games with winners: {completion:.2f}%")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Mahjong AI Pipeline')
    parser.add_argument('--train', action='store_true', help='Run training phase')
    parser.add_argument('--eval', action='store_true', help='Run evaluation phase')
    parser.add_argument('--train-episodes', type=int, default=50000, help='Number of training episodes')
    parser.add_argument('--eval-games', type=int, default=10000, help='Number of evaluation games')
    parser.add_argument('--load-model', action='store_true', help='Load existing model instead of training new one')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    setup_directories()
    
    # Default to both train and eval if neither specified
    if not args.train and not args.eval:
        args.train = True
        args.eval = True
    
    agent = None
    
    # Training phase
    if args.train and not args.load_model:
        agent = train_ai(episodes=args.train_episodes)
    elif args.load_model or args.eval:
        # Load existing model
        print("Loading existing model from models/q_table.pkl")
        agent = RLAgent(q_table_file="models/q_table.pkl")
    
    # Evaluation phase
    if args.eval and agent:
        evaluate_ai(agent, games=args.eval_games)
    elif args.eval:
        evaluate_ai(games=args.eval_games)
    
    print("AI pipeline completed successfully!")