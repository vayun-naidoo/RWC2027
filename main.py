import time
from collections import defaultdict
from multiprocessing import Pool, cpu_count
import os
from src.models import Tournament 

# ==========================================
# CONFIGURATION
# ==========================================
TOTAL_SIMULATIONS = 100000

# ==========================================
# 1. THE WORKER FUNCTION
# ==========================================
def run_batch_simulation(num_runs):
    """
    This function runs on a separate CPU core.
    It runs 'num_runs' tournaments and returns a local dictionary of results.
    """
    # Create a local dictionary for this specific core
    local_stats = defaultdict(lambda: defaultdict(int))
    
    for _ in range(num_runs):
        tourney = Tournament('data/teams.json')
        result_dict = tourney.play() 
        
        for team_name, exit_stage in result_dict.items():
            local_stats[team_name][exit_stage] += 1
            
    # We convert to a regular dict to ensure it can be sent back to the main process safely
    return dict(local_stats)

# ==========================================
# 2. THE MAIN EXECUTION BLOCK
# ==========================================
if __name__ == '__main__':
    print(f"--- Starting Parallel Monte Carlo Simulation ({TOTAL_SIMULATIONS} runs) ---")
    
    # 1. Determine capabilities
    cores = cpu_count()
    print(f"Simulating...")
    
    start_time = time.time()
    
    # 2. Split the work
    # If we want 100,000 runs on 10 cores, we make a list: [10000, 10000, 10000, ...]
    batch_size = TOTAL_SIMULATIONS // cores
    work_load = [batch_size] * cores
    
    # Add any remainder to the first batch (e.g. if 100 / 3 cores)
    work_load[0] += TOTAL_SIMULATIONS % cores
    
    # 3. dispatch the work
    with Pool(processes=cores) as pool:
        # pool.map runs 'run_batch_simulation' for every item in 'work_load'
        # It returns a list of dictionaries (one from each core)
        batch_results = pool.map(run_batch_simulation, work_load)

    # 4. Aggregation (The Merge)
    # We now have a list of separate dictionaries. We must combine them.
    print("Simulations complete. Aggregating data...")
    final_stats = defaultdict(lambda: defaultdict(int))
    
    for batch in batch_results:
        for team, stages in batch.items():
            for stage, count in stages.items():
                final_stats[team][stage] += count

    duration = time.time() - start_time
    print(f"--- Finished in {duration:.2f} seconds ---")
    print(f"--- Speed: {TOTAL_SIMULATIONS/duration:.0f} games per second ---")

    # ==========================================
    # 3. DATA PROCESSING (CUMULATIVE LOGIC)
    # ==========================================
    # (This part remains exactly the same, but uses 'final_stats')
    results_table = []

    for team, stages in final_stats.items():
        # Raw Percentages
        raw_win  = (stages.get('C', 0) / TOTAL_SIMULATIONS) * 100
        raw_2nd  = (stages.get('2nd', 0) / TOTAL_SIMULATIONS) * 100
        raw_3rd  = (stages.get('3rd', 0) / TOTAL_SIMULATIONS) * 100
        raw_4th  = (stages.get('4th', 0) / TOTAL_SIMULATIONS) * 100
        raw_qf   = (stages.get('QF', 0) / TOTAL_SIMULATIONS) * 100
        raw_r16  = (stages.get('R16', 0) / TOTAL_SIMULATIONS) * 100
        raw_pool = (stages.get('Pool Stage', 0) / TOTAL_SIMULATIONS) * 100

        # Cumulative Percentages
        reach_final = raw_win + raw_2nd
        reach_sf    = reach_final + raw_3rd + raw_4th
        reach_qf    = reach_sf + raw_qf
        reach_r16   = reach_qf + raw_r16
        
        row = {
            'Name': team,
            'Win': raw_win,
            'Reach_Final': reach_final,
            'Reach_SF': reach_sf,
            'Reach_QF': reach_qf,
            'Reach_R16': reach_r16,
            'Exit_Pool': raw_pool
        }
        results_table.append(row)

    # Sort
    results_table.sort(key=lambda x: (x['Win'], x['Reach_Final']), reverse=True)

    # Display
    print(f"\n{'TEAM':<20} {'WIN (C)':<8} {'FINAL':<8} {'SF':<8} {'QF':<8} {'R16':<8} {'POOL OUT':<8}")
    print("-" * 80)

    for row in results_table:
        if row['Reach_R16'] > 0.1: 
            print(f"{row['Name']:<20} "
                  f"{row['Win']:>5.1f}%  "
                  f"{row['Reach_Final']:>5.1f}%  "
                  f"{row['Reach_SF']:>5.1f}%  "
                  f"{row['Reach_QF']:>5.1f}%  "
                  f"{row['Reach_R16']:>5.1f}%  "
                  f"{row['Exit_Pool']:>6.1f}%")