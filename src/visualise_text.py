import json
import sys

def print_tree(team_name):
    try:
        with open('data/simulation_paths.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: data/simulation_paths.json not found. Run main.py first.")
        return

    if team_name not in data:
        print(f"Team '{team_name}' not found.")
        return

    paths = data[team_name]
    total_runs = sum(p['count'] for p in paths)
    
    print(f"\n=== MOST COMMON PATHS FOR {team_name.upper()} ({total_runs} simulations) ===")
    print("Format: Count | Probability | Path Journey\n")

    # Sort by most common
    sorted_paths = sorted(paths, key=lambda x: x['count'], reverse=True)

    # Print all paths
    for entry in sorted_paths:
        count = entry['count']
        prob = (count / total_runs) * 100
        path = entry['path']
        
        # Format the path nicely
        # Remove "Start" if present
        if "Start" in path: path.remove("Start")
        
        path_str = " -> ".join(path)
        
        # Color code the output if possible (basic ANSI)
        # Green for Winner, Yellow for Final, Red for Exit
        prefix = "\033[91m" # Red
        if "Champion" in path:
            prefix = "\033[92m" # Green
        elif "Final" in path_str and "Lost" in path[-1]:
            prefix = "\033[93m" # Yellow
        
        reset = "\033[0m"
        
        print(f"{count:>5} | {prob:>5.1f}% | {prefix}{path_str}{reset}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        team = sys.argv[1]
    else:
        team = input("Enter Team Name (e.g. South Africa): ")
    
    print_tree(team)