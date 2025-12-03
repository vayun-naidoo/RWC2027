import json
import numpy as np
import random
import itertools

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
    def __init__(self, name = '', wr_ranking = 30.00, pool = None, pool_points = 0, won = 0, draw = 0, loss = 0, points_for = 0, points_against = 0, tries_for = 0, tries_against = 0, bonus_points = 0):
        self.name = name
        self.wr_ranking = wr_ranking
        self.pool = pool
        self.pool_points = pool_points # This is the actual points value for the pool stage
        self.won = won
        self.draw = draw
        self.loss = loss
        self.points_for = points_for
        self.points_against = points_against
        self.tries_for = tries_for
        self.tries_against = tries_against
        self.bonus_points = bonus_points

    def get_differential(self):
        return (self.points_for or 0) - (self.points_against or 0)
    
    def get_try_differential(self):
        return (self.tries_for or 0) - (self.tries_against or 0)
    
    def __str__(self):
        return f"{self.name:<15} {self.won} \t {self.draw} \t {self.loss} \t {self.points_for} \t {self.points_against} \t {self.get_differential()} \t {self.tries_for} \t {self.bonus_points} \t {self.pool_points}"
    
# Match object to hold match information
class Match:
    def __init__(self, team1: Team, team2: Team, is_knockout: bool = False):
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
        
        #print(f"Expected tries: {self.team1.name}: {team1_tries}, {self.team2.name}: {team2_tries}")
        
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

        #print(f"Expected conversions: {self.team1.name}: {team1_conversions}, {self.team2.name}: {team2_conversions}")

        # ==============================================================
        # STEP 3: CALCUATE PENALTIES
        # ==============================================================

        # In this tentative example, we will just assign a flat rate of penalties per team. This can be improved later to reflect team discipline and style of play
        team1_penalties = np.random.poisson(1.5)
        team2_penalties = np.random.poisson(1.5)

        #print(f"Expected penalties: {self.team1.name}: {team1_penalties}, {self.team2.name}: {team2_penalties}")

        # ==============================================================
        # STEP 4: CALCUATE FINAL SCORES
        # ==============================================================
        team1_score = (team1_tries * 5) + (team1_conversions * 2) + (team1_penalties * 3)
        team2_score = (team2_tries * 5) + (team2_conversions * 2) + (team2_penalties * 3)

        #print(f"Final Score: {self.team1.name}: {team1_score}, {self.team2.name}: {team2_score}")
        return [[self.team1, team1_score, team1_tries], [self.team2, team2_score, team2_tries]]


class Pool:
    def __init__(self, pool_name: str, teams: list[Team]):
        self.pool_name = pool_name
        self.teams = teams

    def sort_teams_by_points(self):
        self.teams.sort(key=lambda x: (-x.pool_points, -x.get_differential(), -x.get_try_differential(), -x.points_for, -x.points_against))

    def __str__(self):
        self.sort_teams_by_points()
        return f"Pool {self.pool_name:<11}W \t D \t L \t PF \t PA \t +/- \t TF \t BP \t PTS\n" + "\n".join([str(team) for team in self.teams])
    
    def calculate_match_points(self, result_1, result_2): # Calculate points based on outcome of game
        team1_name, team1_score, team1_tries = result_1
        team2_name, team2_score, team2_tries = result_2

        outcome_points_team1 = 0
        outcome_points_team2 = 0

        if team1_score > team2_score: # Team 1 wins
            outcome_points_team1 += 4
            outcome_points_team2 += 0
            
            # Update team objects
            team1_name.won += 1
            team2_name.loss += 1
            
        elif team2_score > team1_score: # Team 2 wins
            outcome_points_team2 += 4
            outcome_points_team1 += 0

            # Update team objects
            team2_name.won += 1
            team1_name.loss += 1
        else: # Draw
            outcome_points_team1 += 2
            outcome_points_team2 += 2

            # Update team objects
            team1_name.draw += 1
            team2_name.draw += 1
        
        # Try bonus points
        if team1_tries >= 4:
            outcome_points_team1 += 1
            team1_name.bonus_points = (team1_name.bonus_points or 0) + 1
        if team2_tries >= 4:
            outcome_points_team2 += 1
            team2_name.bonus_points = (team2_name.bonus_points or 0) + 1

        # Losing bonus points for difference less than or equal to 7
        if abs(team1_score - team2_score) <= 7:
            if team1_score > team2_score:
                outcome_points_team2 += 1
                team2_name.bonus_points = (team2_name.bonus_points or 0) + 1

            elif team2_score > team1_score:
                outcome_points_team1 += 1
                team1_name.bonus_points = (team1_name.bonus_points or 0) + 1

        # Update team pool points
        team1_name.pool_points = (team1_name.pool_points or 0) + outcome_points_team1
        team2_name.pool_points = (team2_name.pool_points or 0) + outcome_points_team2

        # Update points for and against
        team1_name.points_for = (team1_name.points_for or 0) + team1_score
        team1_name.points_against = (team1_name.points_against or 0) + team2_score 

        team2_name.points_for = (team2_name.points_for or 0) + team2_score
        team2_name.points_against = (team2_name.points_against or 0) + team1_score

        # Update tries for
        team1_name.tries_for = (team1_name.tries_for or 0) + team1_tries
        team2_name.tries_for = (team2_name.tries_for or 0)  + team2_tries
      
    def play_matches_in_pool(self):
        matches = itertools.combinations(self.teams, 2) # Generate all possible match combinations in the pool
        
        for team1, team2 in matches:
            match = Match(team1, team2)
            result_1, result_2 = match.play_match()
            self.calculate_match_points(result_1, result_2)
        print(self , "\n")





 