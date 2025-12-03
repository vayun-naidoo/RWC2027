import json
import numpy as np
import random

CONST_TRY_AVE = 3.0

# JSON decoder
def import_teams(json_file):
    team_list = []
    try:
        with open(json_file, 'r') as f:
            import_teams = json.load(f)
        for team in import_teams['teams']:
            team_obj = Team(name=team['team_name'], wr_ranking=team['wr_points'], pool=team['pool'])
            team_list.append(team_obj)
            
    except FileNotFoundError:
        print(f"File {json_file} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {json_file}.")
    
    return team_list

# Consider the team as read from pool stage with additional stats
class Team:
    def __init__(self, name = '', wr_ranking = 30.00, pool = None, pool_points = None, points_for = None, points_against = None, tries_for = None, tries_against = None):
        self.name = name
        self.wr_ranking = wr_ranking
        self.pool = pool
        self.pool_points = pool_points # This is the actual points value for the pool stage
        self.points_for = points_for
        self.points_against = points_against
        self.tries_for = tries_for
        self.tries_against = tries_against
    
    def __str__(self):
        return f"{self.name}:\n- WR: {self.wr_ranking} points\n- Pool: {self.pool}\n- Pool Points: {self.pool_points}\n- Points For: {self.points_for}\n- Points Against: {self.points_against}\n- Tries For: {self.tries_for}\n- Tries Against: {self.tries_against}"

    
# Match object to hold match information
class Match:
    def __init__(self, team1: Team, team2: Team):
        self.team1 = team1
        self.team2 = team2

    def play_match(self):
        # ==============================================================
        # STEP 1: CALCUATE EXPECTED TRIES BASED ON RANKING DIFFERENCE
        # ==============================================================

        rating_diff = self.team1.wr_ranking - self.team2.wr_ranking

        # From here, the 'A' team is the team with the higher ranking while the 'B' team is the lower ranked team
        lambda_a = CONST_TRY_AVE + (rating_diff / 10)
        lambda_b = CONST_TRY_AVE - (rating_diff / 10)

        if lambda_a < 0.2: # Clamping statement for large differentials
            lambda_a = 0.2
        if lambda_b < 0.2:  
            lambda_b = 0.2

        if rating_diff > 0: # Team 1 better than Team 2, hence 1 is assigned A and 2 is assigned B
            team1_tries = np.random.poisson(lambda_a)
            team2_tries = np.random.poisson(lambda_b)
        elif rating_diff < 0: # Team 2 better than Team 1, hence 2 is assigned A and 1 is assigned B
            team1_tries = np.random.poisson(lambda_b)
            team2_tries = np.random.poisson(lambda_a)
        else: # Rankings must be equal - unlikely but possible. This in essense just sets both to the average value
            team1_tries = np.random.poisson(CONST_TRY_AVE)
            team2_tries = np.random.poisson(CONST_TRY_AVE)
        
        print(f"Expected tries: {self.team1.name}: {team1_tries}, {self.team2.name}: {team2_tries}")
        
        # ==============================================================
        # STEP 2: CALCUATE EXPECTED CONVERSTIONS BASED ON TRIES
        # ==============================================================
        team1_conversions = 0
        team2_conversions = 0

        # Could make provision for higher rated teams having better kickers but for now assume all teams have equal chance of conversion

        for i in range(team1_tries): 
            if random.random() < 0.78: team1_conversions += 1
        for i in range(team2_tries): 
            if random.random() < 0.78: team2_conversions += 1

        print(f"Expected conversions: {self.team1.name}: {team1_conversions}, {self.team2.name}: {team2_conversions}")

        # ==============================================================
        # STEP 3: CALCUATE PENALTIES
        # ==============================================================

        # In this tentative example, we will just assign a flat rate of penalties per team. This can be improved later to reflect team discipline and style of play
        team1_penalties = np.random.poisson(1.5)
        team2_penalties = np.random.poisson(1.5)

        print(f"Expected penalties: {self.team1.name}: {team1_penalties}, {self.team2.name}: {team2_penalties}")

        # ==============================================================
        # STEP 4: CALCUATE FINAL SCORES
        # ==============================================================
        team1_score = (team1_tries * 5) + (team1_conversions * 2) + (team1_penalties * 3)
        team2_score = (team2_tries * 5) + (team2_conversions * 2) + (team2_penalties * 3)

        print(f"Final Score: {self.team1.name}: {team1_score}, {self.team2.name}: {team2_score}")

class Pool:
    def __init__(self, pool_name: str, teams: list[Team]):
        self.pool_name = pool_name
        self.teams = teams

    def __str__(self):
        team_names = ', '.join([team.name for team in self.teams])
        return f"Pool {self.pool_name}: {team_names}"


teams = import_teams('data/teams.json')
#print(teams[0])
test_match = Match(teams[0], teams[0])
test_match.play_match()        