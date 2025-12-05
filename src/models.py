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
        pass
        #print(f"File {json_file} not found.")
    except json.JSONDecodeError:
        pass
        #print(f"Error decoding JSON from file {json_file}.")
    
    return team_list

# Consider the team as read from pool stage with additional stats
class Team:
    def __init__(self, name = '', wr_ranking = 30.00, pool = '', pool_points = 0, won = 0, draw = 0, loss = 0, points_for = 0, points_against = 0, tries_for = 0, tries_against = 0, bonus_points = 0):
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
        return f"{self.name:<15} {self.won} \t {self.draw} \t {self.loss} \t {self.points_for} \t {self.points_against} \t {self.get_differential()} \t {self.tries_for} \t {self.bonus_points} \t {self.pool_points} \t ({self.wr_ranking})"
    
# Match object to hold match information
class Match:
    def __init__(self, team1: Team, team2: Team, is_knockout: bool = False):
        self.team1 = team1
        self.team2 = team2
        self.is_knockout = is_knockout

    def play_match(self):
        # ==============================================================
        # STEP 1: CALCUATE EXPECTED TRIES BASED ON RANKING DIFFERENCE
        # ==============================================================

        rating_diff = self.team1.wr_ranking - self.team2.wr_ranking

        # From here, the 'A' team is the team with the higher ranking while the 'B' team is the lower ranked team
        lambda_a = max(0.2, CONST_TRY_AVE + (rating_diff / 10))
        lambda_b = max(0.2, CONST_TRY_AVE - (rating_diff / 10))

        team1_tries = np.random.poisson(lambda_a)
        team2_tries = np.random.poisson(lambda_b)

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

    def play_knockout_match(self):
        if not self.is_knockout:
            raise ValueError("This is not a knockout match.")
        
        result_1, result_2 = self.play_match()

        # Check for draw and resolve with sudden death
        # TODO: Fix sudden death logic to be more realistic

        while result_1[1] == result_2[1]:
         #   print(f"Match between {self.team1.name} and {self.team2.name} ended in a draw at {result_1[1]} - {result_2[1]}. Proceeding to sudden death...")
            result_1, result_2 = self.play_match()
        
        return result_1, result_2

class Pool:
    def __init__(self, pool_name: str, teams: list[Team]):
        self.pool_name = pool_name
        self.teams = teams

    def sort_teams_by_points(self):
        self.teams.sort(key=lambda x: (-x.pool_points, -x.get_differential(), -x.get_try_differential(), -x.points_for, -x.points_against))

    def __str__(self):
        self.sort_teams_by_points()
        return f"Pool {self.pool_name:<11}W \t D \t L \t PF \t PA \t +/- \t TF \t BP \t PTS\n" + "\n".join([str(team) for team in self.teams])
    
    def calculate_match_points(self, result_1, result_2, print_results = False): # Calculate points based on outcome of game
        team1_name, team1_score, team1_tries = result_1
        team2_name, team2_score, team2_tries = result_2
        self.print_results = print_results

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

        # Update tries for a team
        team1_name.tries_for = (team1_name.tries_for or 0) + team1_tries
        team2_name.tries_for = (team2_name.tries_for or 0)  + team2_tries
      
    def play_matches_in_pool(self, print_results = False):
        matches = itertools.combinations(self.teams, 2) # Generate all possible match combinations in the pool
        self.print_results = print_results

        match_results = []
        for team1, team2 in matches:
            match = Match(team1, team2)
            result_1, result_2 = match.play_match()
            self.calculate_match_points(result_1, result_2)
            match_results.append(f"{result_1[0].name} {result_1[1]} - {result_2[1]} {result_2[0].name}")

        if print_results:
            print(self , "\n")
            print("\n".join(match_results))
            print('\n' + '='*100 + '\n')



class Tournament:

    def __init__(self, data):
        self.data = data

    def play(self , print_results = False, print_statement = False):
        self.print_results = print_results
        self.print_statement = print_statement

        results = {}
        teams = import_teams(self.data)
        results = {team.name: "Pool Stage" for team in teams}

        Pool_A = Pool('A', [team for team in teams if team.pool == 'A'])
        Pool_B = Pool('B', [team for team in teams if team.pool == 'B'])
        Pool_C = Pool('C', [team for team in teams if team.pool == 'C'])
        Pool_D = Pool('D', [team for team in teams if team.pool == 'D'])
        Pool_E = Pool('E', [team for team in teams if team.pool == 'E'])
        Pool_F = Pool('F', [team for team in teams if team.pool == 'F'])

        Pool_A.play_matches_in_pool(print_results = self.print_results)
        Pool_B.play_matches_in_pool(print_results = self.print_results)
        Pool_C.play_matches_in_pool(print_results = self.print_results)
        Pool_D.play_matches_in_pool(print_results = self.print_results)
        Pool_E.play_matches_in_pool(print_results = self.print_results)
        Pool_F.play_matches_in_pool(print_results = self.print_results)

        top_2_teams = []
        third_place_teams = []

        for pool in [Pool_A, Pool_B, Pool_C, Pool_D, Pool_E, Pool_F]:
            pool.sort_teams_by_points()
            top_2_teams.extend(pool.teams[:2])
            third_place_teams.append(pool.teams[2]) 

        third_place_teams.sort(key=lambda x: (-x.pool_points, -x.get_differential(), -x.get_try_differential(), -x.points_for, -x.tries_for))

        # Top two from each pool advance to knockout stage

        if print_statement:
            print("Top 2 teams from each pool advancing to the knockout stage:")
            for team in top_2_teams:
                print(f"{team.name} from Pool {team.pool} with {team.pool_points} points")

            print("\nThird place teams from each pool (ranked):")
            for team in third_place_teams:
                print(f"{team.name} from Pool {team.pool} with {team.pool_points} points ({team.get_differential()} PD) ({team.get_try_differential()} TD) ({team.points_for} PF) ({team.tries_for} TF)")

        # Organising top four third place for berths
        # Sort according to brackets top to bottom left to right
        # Find best team in group and remove and repeat

            print()
        cef_best = max((t for t in third_place_teams if t.pool in ['C', 'E', 'F']), key = lambda x: x.pool_points)
        third_place_teams.remove(cef_best)
        

        def_best = max((t for t in third_place_teams if t.pool in ['D', 'E', 'F']), key = lambda x: x.pool_points)
        third_place_teams.remove(def_best)
       

        aef_best = max((t for t in third_place_teams if t.pool in ['A', 'E', 'F']), key = lambda x: x.pool_points)
        third_place_teams.remove(aef_best)
     

        bef_best = max((t for t in third_place_teams if t.pool in ['B', 'E', 'F']), key = lambda x: x.pool_points)
        third_place_teams.remove(bef_best)
      
        if print_statement:
            print('C/E/F best:', cef_best.name)
            print('D/E/F best:', def_best.name)
            print('A/E/F best:', aef_best.name)
            print('B/E/F best:', bef_best.name)
            print("=" * 100)
        # ===============================
        # KNOCKOUT: R16
        # ===============================

        r16_qual = top_2_teams + [aef_best, bef_best, cef_best, def_best]

        for team in r16_qual:
            results[team.name] = "R16"

        a_1st = top_2_teams[0]
        a_2nd = top_2_teams[1]

        b_1st = top_2_teams[2]
        b_2nd = top_2_teams[3]

        c_1st = top_2_teams[4]
        c_2nd = top_2_teams[5]

        d_1st = top_2_teams[6]
        d_2nd = top_2_teams[7]

        e_1st = top_2_teams[8]
        e_2nd = top_2_teams[9]

        f_1st = top_2_teams[10]
        f_2nd = top_2_teams[11]

        R16_1 = Match(a_1st, cef_best, True).play_knockout_match()
        R16_1_winner = (R16_1[0][0], R16_1[1][0])[R16_1[0][1] - R16_1[1][1] < 0]

        R16_2 = Match(b_1st, def_best, True).play_knockout_match()
        R16_2_winner = (R16_2[0][0], R16_2[1][0])[R16_2[0][1] - R16_2[1][1] < 0]


        R16_3 = Match(c_2nd, f_2nd, True).play_knockout_match()    
        R16_3_winner = (R16_3[0][0], R16_3[1][0])[R16_3[0][1] - R16_3[1][1] < 0]

        R16_4 = Match(e_1st, d_2nd, True).play_knockout_match()   
        R16_4_winner = (R16_4[0][0], R16_4[1][0])[R16_4[0][1] - R16_4[1][1] < 0]

        R16_5 = Match(a_2nd, e_2nd, True).play_knockout_match()
        R16_5_winner = (R16_5[0][0], R16_5[1][0])[R16_5[0][1] - R16_5[1][1] < 0]

        R16_6 = Match(f_1st, b_2nd, True).play_knockout_match()
        R16_6_winner = (R16_6[0][0], R16_6[1][0])[R16_6[0][1] - R16_6[1][1] < 0]

        R16_7 = Match(c_1st, aef_best, True).play_knockout_match()
        R16_7_winner = (R16_7[0][0], R16_7[1][0])[R16_7[0][1] - R16_7[1][1] < 0]

        R16_8 = Match(d_1st, bef_best, True).play_knockout_match()
        R16_8_winner = (R16_8[0][0], R16_8[1][0])[R16_8[0][1] - R16_8[1][1] < 0]

        if print_statement:
            print("Knockout Bracket - R16:")
            print(f'{R16_1[0][0].name} {R16_1[0][1]} - {R16_1[1][0].name} {R16_1[1][1]}')
            print(f'{R16_2[0][0].name} {R16_2[0][1]} - {R16_2[1][0].name} {R16_2[1][1]}\n')
            print(f'{R16_3[0][0].name} {R16_3[0][1]} - {R16_3[1][0].name} {R16_3[1][1]}')
            print(f'{R16_4[0][0].name} {R16_4[0][1]} - {R16_4[1][0].name} {R16_4[1][1]}\n')
            print(f'{R16_5[0][0].name} {R16_5[0][1]} - {R16_5[1][0].name} {R16_5[1][1]}')
            print(f'{R16_6[0][0].name} {R16_6[0][1]} - {R16_6[1][0].name} {R16_6[1][1]}\n')
            print(f'{R16_7[0][0].name} {R16_7[0][1]} - {R16_7[1][0].name} {R16_7[1][1]}')
            print(f'{R16_8[0][0].name} {R16_8[0][1]} - {R16_8[1][0].name} {R16_8[1][1]}\n')

            print(f'{R16_1_winner.name} to play {R16_2_winner.name} in QF1')
            print(f'{R16_3_winner.name} to play {R16_4_winner.name} in QF2')
            print(f'{R16_5_winner.name} to play {R16_6_winner.name} in QF3')
            print(f'{R16_7_winner.name} to play {R16_8_winner.name} in QF4')
            print("=" * 100)

        # ===============================
        # KNOCKOUT: QF
        # ===============================

        qf_qual = [R16_1_winner, R16_2_winner, R16_3_winner, R16_4_winner, R16_5_winner, R16_6_winner, R16_7_winner, R16_8_winner]

        for team in qf_qual:
            results[team.name] = "QF"

        QF1 = Match(R16_1_winner, R16_2_winner, True).play_knockout_match()
        QF1_winner = (QF1[0][0], QF1[1][0])[QF1[0][1] - QF1[1][1] < 0]

        QF2 = Match(R16_3_winner, R16_4_winner, True).play_knockout_match()
        QF2_winner = (QF2[0][0], QF2[1][0])[QF2[0][1] - QF2[1][1] < 0]

        QF3 = Match(R16_5_winner, R16_6_winner, True).play_knockout_match()
        QF3_winner = (QF3[0][0], QF3[1][0])[QF3[0][1] - QF3[1][1] < 0]

        QF4 = Match(R16_7_winner, R16_8_winner, True).play_knockout_match()
        QF4_winner = (QF4[0][0], QF4[1][0])[QF4[0][1] - QF4[1][1] < 0]

        sf_qual = [QF1_winner, QF2_winner, QF3_winner, QF4_winner]

        for team in sf_qual:
            results[team.name] = "SF"

        if print_statement:
            print("Knockout Bracket - QF")
            print(f'{QF1[0][0].name} {QF1[0][1]} - {QF1[1][0].name} {QF1[1][1]}')
            print(f'{QF2[0][0].name} {QF2[0][1]} - {QF2[1][0].name} {QF2[1][1]}\n')
            print(f'{QF3[0][0].name} {QF3[0][1]} - {QF3[1][0].name} {QF3[1][1]}')
            print(f'{QF4[0][0].name} {QF4[0][1]} - {QF4[1][0].name} {QF4[1][1]}\n')
            print(f'{QF1_winner.name} to play {QF2_winner.name} in SF1')
            print(f'{QF3_winner.name} to play {QF4_winner.name} in SF2')
            print("=" * 100)

        # ===============================
        # KNOCKOUT: SF
        # ===============================
        
        SF1 = Match(QF1_winner, QF2_winner, True).play_knockout_match()
        SF1_winner = (SF1[0][0], SF1[1][0])[SF1[0][1] - SF1[1][1] < 0]
        SF1_loser = (SF1[0][0], SF1[1][0])[SF1[0][1] - SF1[1][1] > 0]

        SF2 = Match(QF3_winner, QF4_winner, True).play_knockout_match()
        SF2_winner = (SF2[0][0], SF2[1][0])[SF2[0][1] - SF2[1][1] < 0]
        SF2_loser = (SF2[0][0], SF2[1][0])[SF2[0][1] - SF2[1][1] > 0]

        if print_statement:
            print("Knockout Bracket - SF")
            print(f'{SF1[0][0].name} {SF1[0][1]} - {SF1[1][0].name} {SF1[1][1]}')
            print(f'{SF2[0][0].name} {SF2[0][1]} - {SF2[1][0].name} {SF2[1][1]}')
            print()
            print(f'{SF1_loser.name} to play {SF2_loser.name} in Bronze Final')
            print(f'{SF1_winner.name} to play {SF2_winner.name} in Final')
            print('=' * 100)

        results[SF1_loser.name] = "4th"
        results[SF2_loser.name] = "4th" # default to 4th for now
        results[SF1_winner.name] = "2nd"
        results[SF2_winner.name] = "2nd"

        # ===============================
        # KNOCKOUT: Finals
        # ===============================

        BF = Match(SF1_loser, SF2_loser, True).play_knockout_match()
        BF_winner = (BF[0][0], BF[1][0])[BF[0][1] - BF[1][1] < 0]
        results[BF_winner.name] = "3rd"

        final = Match(SF1_winner, SF2_winner, True).play_knockout_match()
        champion = (final[0][0], final[1][0])[final[0][1] - final[1][1] < 0]
        results[champion.name] = "C"

        if print_statement:
            print(f'{BF[0][0].name} {BF[0][1]} - {BF[1][0].name} {BF[1][1]}')
            print(f'{BF_winner.name} wins bronze!\n')
            print(f'{final[0][0].name} {final[0][1]} - {final[1][0].name} {final[1][1]}')
            print(f'{champion.name} wins MRWC 2027!')
        return results
 