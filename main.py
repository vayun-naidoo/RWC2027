import time
import json
import pandas as pd
from collections import defaultdict, Counter
from multiprocessing import Pool, cpu_count
from src.models import Tournament 

# ==========================================
# CONFIGURATION
# ==========================================
TOTAL_SIMULATIONS = 5000
DATA_FILE = 'data/teams.json'

def run_batch_simulation(num_runs):
    """
    Returns a Dictionary where Key = TeamName, Value = Counter of Paths
    """
    local_path_counts = defaultdict(Counter)
    
    for _ in range(num_runs):
        tourney = Tournament(DATA_FILE)
        results = tourney.play() # Returns {Team: (PathTuple)}
        
        for team, path in results.items():
            local_path_counts[team][path] += 1
            
    return dict(local_path_counts)

def derive_stage_counts(final_data):
    """
    Converts path data back into simple stage counts for the table.
    """
    stage_counts = defaultdict(lambda: defaultdict(int))
    
    for team, paths in final_data.items():
        for path, count in paths.items():
            # Check what's in the path to determine stage reached
            path_str = str(path)
            
            # Start from bottom (Pool) up to Winner to capture all stages reached
            stage_counts[team]['Pool Stage'] += count # Everyone plays pool
            
            if "Qualified Best 3rd" in path_str or "Runner-Up" in path_str or "Winner" in path_str:
                 # Note: This is loose matching, strictly we rely on R16 match logs
                 pass

            # Precise matching based on logs
            if any("R16" in s for s in path) or "Qualified Best 3rd" in path_str or "Pool" in str(path[-1]) and "Winner" in str(path[-1]):
                 # Note: Ideally we check if they PLAYED an R16 match. 
                 # Easier way: check if they didn't exit at pool
                 if "Pool Exit" not in str(path):
                     stage_counts[team]['R16'] += count

            if any("QF" in s for s in path):
                stage_counts[team]['QF'] += count
            
            if any("SF" in s for s in path):
                stage_counts[team]['SF'] += count
                
            if any("Final" in s for s in path) and "Bronze" not in str(path[-1]):
                stage_counts[team]['Final'] += count
                
            if "Champion" in path:
                stage_counts[team]['Champion'] += count
                
    return stage_counts

if __name__ == '__main__':
    print(f"--- Starting Parallel Monte Carlo Simulation ({TOTAL_SIMULATIONS} runs) ---")
    
    cores = cpu_count()
    batch_size = TOTAL_SIMULATIONS // cores
    work_load = [batch_size] * cores
    work_load[0] += TOTAL_SIMULATIONS % cores
    
    start_time = time.time()
    
    with Pool(processes=cores) as pool:
        batch_results = pool.map(run_batch_simulation, work_load)

    print("Simulations complete. Aggregating data...")
    
    # Aggregate Paths
    final_data = defaultdict(Counter)
    for batch in batch_results:
        for team, paths in batch.items():
            final_data[team].update(paths)

    # Save Paths for Visualization
    export_data = {}
    for team, paths in final_data.items():
        # Keep top 100 paths per team to save space
        common_paths = paths.most_common(100)
        export_data[team] = [{"path": list(p), "count": c} for p, c in common_paths]

    with open("data/simulation_paths.json", "w") as f:
        json.dump(export_data, f, indent=4)

    duration = time.time() - start_time
    print(f"--- Finished in {duration:.2f} seconds ---")

    # ==========================================
    # GENERATE SUMMARY TABLE
    # ==========================================
    stage_stats = derive_stage_counts(final_data)
    results_table = []

    for team, stats in stage_stats.items():
        row = {
            'Name': team,
            'Win': (stats['Champion'] / TOTAL_SIMULATIONS) * 100,
            'Final': (stats['Final'] / TOTAL_SIMULATIONS) * 100,
            'SF': (stats['SF'] / TOTAL_SIMULATIONS) * 100,
            'QF': (stats['QF'] / TOTAL_SIMULATIONS) * 100,
            'R16': (stats['R16'] / TOTAL_SIMULATIONS) * 100,
        }
        results_table.append(row)

    # Sort by Win % then Final %
    results_table.sort(key=lambda x: (x['Win'], x['Final']), reverse=True)

    print(f"\n{'TEAM':<20} {'WIN %':<8} {'FINAL %':<8} {'SF %':<8} {'QF %':<8} {'R16 %':<8}")
    print("-" * 75)
    for row in results_table:
        if row['R16'] > 0.1: # Only show teams with >0.1% chance of making knockouts
            print(f"{row['Name']:<20} {row['Win']:>6.1f}   {row['Final']:>6.1f}   {row['SF']:>6.1f}   {row['QF']:>6.1f}   {row['R16']:>6.1f}")

    print("\nDetailed path data saved to data/simulation_paths.json")
    print("Run 'python visualise_text.py' to see team paths.")