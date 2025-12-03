from models import Pool, Team, Match
from models import import_teams

teams = import_teams('data/teams.json')

Pool_A = Pool('A', [team for team in teams if team.pool == 'A'])
Pool_B = Pool('B', [team for team in teams if team.pool == 'B'])
Pool_C = Pool('C', [team for team in teams if team.pool == 'C'])
Pool_D = Pool('D', [team for team in teams if team.pool == 'D'])
Pool_E = Pool('E', [team for team in teams if team.pool == 'E'])
Pool_F = Pool('F', [team for team in teams if team.pool == 'F'])

Pool_A.play_matches_in_pool()
Pool_B.play_matches_in_pool()
Pool_C.play_matches_in_pool()
Pool_D.play_matches_in_pool()
Pool_E.play_matches_in_pool()
Pool_F.play_matches_in_pool()

top_2_teams = []
for pool in [Pool_A, Pool_B, Pool_C, Pool_D, Pool_E, Pool_F]:
    pool.sort_teams_by_points()
    top_2_teams.extend(pool.teams[:2])

# Top two from each pool advance to knockout stage
print("Top 2 teams from each pool advancing to the knockout stage:")
for team in top_2_teams:
    print(f"{team.name} from Pool {team.pool} with {team.pool_points} points")

# Gather all third place teams
third_place_teams = []
for pool in [Pool_A, Pool_B, Pool_C, Pool_D, Pool_E, Pool_F]:
    pool.sort_teams_by_points()
    third_place_teams.append(pool.teams[2]) 

print("\nThird place teams from each pool:")
for team in third_place_teams:
    print(f"{team.name} from Pool {team.pool} with {team.pool_points} points")

# Place third place teams in order of pool points to determine best four
third_place_teams.sort(key=lambda x: (-x.pool_points, -x.get_differential(), -x.get_try_differential(), -x.points_for, -x.tries_for))
best_four_third_place = third_place_teams[:4] 

print("\nBest four third place teams advancing to the knockout stage:")
for team in best_four_third_place:
    print(f"{team.name} from Pool {team.pool} with {team.pool_points} points")  