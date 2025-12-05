import json
import numpy as np
import random
import itertools

CONST_TRY_AVE = 3.0

def import_teams(json_file):
    team_list = []
    try:
        with open(json_file, 'r') as f:
            import_teams = json.load(f)
        for team in import_teams['teams']:
            # Initialize with empty path
            team_obj = Team(name=team['team_name'], wr_ranking=team['wr_points'], pool=team['pool'])
            team_list.append(team_obj)
    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    return team_list

class Team:
    def __init__(self, name='', wr_ranking=30.00, pool='', pool_points=0, won=0, draw=0, loss=0, points_for=0, points_against=0, tries_for=0, tries_against=0, bonus_points=0):
        self.name = name
        self.wr_ranking = wr_ranking
        self.pool = pool
        self.pool_points = pool_points
        self.won = won
        self.draw = draw
        self.loss = loss
        self.points_for = points_for
        self.points_against = points_against
        self.tries_for = tries_for
        self.tries_against = tries_against
        self.bonus_points = bonus_points
        
        # === NEW: FLIGHT RECORDER ===
        self.path = [] 

    def log_path(self, event):
        self.path.append(event)

    def get_differential(self):
        return (self.points_for or 0) - (self.points_against or 0)
    
    def get_try_differential(self):
        return (self.tries_for or 0) - (self.tries_against or 0)
    
    def __str__(self):
        return f"{self.name:<15} ({self.wr_ranking})"

class Match:
    def __init__(self, team1: Team, team2: Team, is_knockout: bool = False):
        self.team1 = team1
        self.team2 = team2
        self.is_knockout = is_knockout

    def play_match(self):
        # Calculate Expected Tries
        rating_diff = self.team1.wr_ranking - self.team2.wr_ranking
        lambda_a = max(0.2, CONST_TRY_AVE + (rating_diff / 10))
        lambda_b = max(0.2, CONST_TRY_AVE - (rating_diff / 10))

        team1_tries = np.random.poisson(lambda_a)
        team2_tries = np.random.poisson(lambda_b)

        # Conversions
        team1_conversions = sum(1 for _ in range(team1_tries) if random.random() < 0.78)
        team2_conversions = sum(1 for _ in range(team2_tries) if random.random() < 0.78)

        # Penalties
        team1_penalties = np.random.poisson(1.5)
        team2_penalties = np.random.poisson(1.5)

        # Final Score
        team1_score = (team1_tries * 5) + (team1_conversions * 2) + (team1_penalties * 3)
        team2_score = (team2_tries * 5) + (team2_conversions * 2) + (team2_penalties * 3)

        return [[self.team1, team1_score, team1_tries], [self.team2, team2_score, team2_tries]]

    def play_knockout_match(self):
        if not self.is_knockout:
            raise ValueError("This is not a knockout match.")
        
        result_1, result_2 = self.play_match()

        # Sudden Death Logic
        while result_1[1] == result_2[1]:
            result_1, result_2 = self.play_match()
        
        return result_1, result_2

class Pool:
    def __init__(self, pool_name: str, teams: list[Team]):
        self.pool_name = pool_name
        self.teams = teams

    def sort_teams_by_points(self):
        self.teams.sort(key=lambda x: (-x.pool_points, -x.get_differential(), -x.get_try_differential(), -x.points_for, -x.points_against))

    def calculate_match_points(self, result_1, result_2):
        team1_obj, team1_score, team1_tries = result_1
        team2_obj, team2_score, team2_tries = result_2

        outcome_points_team1 = 0
        outcome_points_team2 = 0

        if team1_score > team2_score:
            outcome_points_team1 += 4
            team1_obj.won += 1
            team2_obj.loss += 1
        elif team2_score > team1_score:
            outcome_points_team2 += 4
            team2_obj.won += 1
            team1_obj.loss += 1
        else:
            outcome_points_team1 += 2
            outcome_points_team2 += 2
            team1_obj.draw += 1
            team2_obj.draw += 1
        
        if team1_tries >= 4:
            outcome_points_team1 += 1
            team1_obj.bonus_points += 1
        if team2_tries >= 4:
            outcome_points_team2 += 1
            team2_obj.bonus_points += 1

        if abs(team1_score - team2_score) <= 7:
            if team1_score > team2_score:
                outcome_points_team2 += 1
                team2_obj.bonus_points += 1
            elif team2_score > team1_score:
                outcome_points_team1 += 1
                team1_obj.bonus_points += 1

        team1_obj.pool_points += outcome_points_team1
        team2_obj.pool_points += outcome_points_team2
        
        # Stats update
        team1_obj.points_for += team1_score
        team1_obj.points_against += team2_score 
        team2_obj.points_for += team2_score
        team2_obj.points_against += team1_score
        team1_obj.tries_for += team1_tries
        team2_obj.tries_for += team2_tries
      
    def play_matches_in_pool(self):
        matches = itertools.combinations(self.teams, 2)
        for team1, team2 in matches:
            match = Match(team1, team2)
            result_1, result_2 = match.play_match()
            self.calculate_match_points(result_1, result_2)

class Tournament:
    def __init__(self, data):
        self.data = data

    def resolve_winner(self, match_result, stage_name):
        """Helper to determine winner and log paths"""
        t1_obj, t1_score, _ = match_result[0]
        t2_obj, t2_score, _ = match_result[1]
        
        if t1_score > t2_score:
            t1_obj.log_path(f"Beat {t2_obj.name} ({stage_name})")
            t2_obj.log_path(f"Lost to {t1_obj.name} ({stage_name})")
            return t1_obj, t2_obj 
        else:
            t2_obj.log_path(f"Beat {t1_obj.name} ({stage_name})")
            t1_obj.log_path(f"Lost to {t2_obj.name} ({stage_name})")
            return t2_obj, t1_obj

    def play(self):
        teams = import_teams(self.data)
        
        pools = {}
        for p_code in ['A', 'B', 'C', 'D', 'E', 'F']:
            p = Pool(p_code, [t for t in teams if t.pool == p_code])
            p.play_matches_in_pool()
            p.sort_teams_by_points()
            
            # Log Pool Results
            p.teams[0].log_path(f"1. Pool {p_code} Winner")
            p.teams[1].log_path(f"2. Pool {p_code} Runner-Up")
            p.teams[2].log_path("3. Pool Exit (3rd)")
            p.teams[3].log_path("4. Pool Exit (4th)")
            
            pools[p_code] = p

        # Gather Qualifiers
        top_2_teams = []
        third_place_teams = []
        for p in pools.values():
            top_2_teams.extend(p.teams[:2])
            third_place_teams.append(p.teams[2])

        third_place_teams.sort(key=lambda x: (-x.pool_points, -x.get_differential()))
        
        # 3rd Place Selection Logic
        qualifying_thirds = []
        def get_best_third(pool_options):
            candidates = [t for t in third_place_teams if t.pool in pool_options and t not in qualifying_thirds]
            if not candidates: return None
            best = max(candidates, key=lambda x: x.pool_points)
            qualifying_thirds.append(best)
            return best

        cef_best = get_best_third(['C', 'E', 'F'])
        def_best = get_best_third(['D', 'E', 'F'])
        aef_best = get_best_third(['A', 'E', 'F'])
        bef_best = get_best_third(['B', 'E', 'F'])
        
        # Correct path for qualifiers
        for t in [cef_best, def_best, aef_best, bef_best]:
            if t: 
                # Remove the "Pool Exit" log and replace with qualification
                if len(t.path) > 0 and "Pool Exit" in t.path[-1]:
                    t.path.pop()
                t.log_path("Qualified Best 3rd")

        # R16 Mappings (Based on array indexing of sorted pools A-F)
        r16_matches = [
            (top_2_teams[0], cef_best),
            (top_2_teams[2], def_best),
            (top_2_teams[5], top_2_teams[11]),
            (top_2_teams[8], top_2_teams[7]),
            (top_2_teams[1], top_2_teams[9]),
            (top_2_teams[10], top_2_teams[3]),
            (top_2_teams[4], aef_best),
            (top_2_teams[6], bef_best)
        ]
        
        qf_qualifiers = []
        
        for t1, t2 in r16_matches:
            if t1 and t2:
                res = Match(t1, t2, True).play_knockout_match()
                w, l = self.resolve_winner(res, "R16")
                qf_qualifiers.append(w)
            else:
                # Fallback if 3rd place missing
                winner = t1 if t1 else t2
                if winner: qf_qualifiers.append(winner)

        # Quarter Finals
        sf_qualifiers = []
        for i in range(0, 8, 2):
            if i+1 < len(qf_qualifiers):
                res = Match(qf_qualifiers[i], qf_qualifiers[i+1], True).play_knockout_match()
                w, l = self.resolve_winner(res, "QF")
                sf_qualifiers.append(w)
            
        # Semi Finals
        finalists = []
        losing_semi_finalists = []
        
        # SF1
        if len(sf_qualifiers) >= 2:
            res_sf1 = Match(sf_qualifiers[0], sf_qualifiers[1], True).play_knockout_match()
            w_sf1, l_sf1 = self.resolve_winner(res_sf1, "SF")
            finalists.append(w_sf1)
            losing_semi_finalists.append(l_sf1)
        
        # SF2
        if len(sf_qualifiers) >= 4:
            res_sf2 = Match(sf_qualifiers[2], sf_qualifiers[3], True).play_knockout_match()
            w_sf2, l_sf2 = self.resolve_winner(res_sf2, "SF")
            finalists.append(w_sf2)
            losing_semi_finalists.append(l_sf2)
        
        # Finals
        if len(losing_semi_finalists) == 2:
            res_bronze = Match(losing_semi_finalists[0], losing_semi_finalists[1], True).play_knockout_match()
            w_bronze, l_bronze = self.resolve_winner(res_bronze, "Bronze Final")
            w_bronze.log_path("Bronze Medal")
        
        if len(finalists) == 2:
            res_final = Match(finalists[0], finalists[1], True).play_knockout_match()
            w_final, l_final = self.resolve_winner(res_final, "Final")
            w_final.log_path("Champion")

        return {team.name: tuple(team.path) for team in teams}