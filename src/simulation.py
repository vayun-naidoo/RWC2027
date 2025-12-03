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

print("Top 2 teams from each pool advancing to the knockout stage:")
for team in top_2_teams:
    print(f"{team.name} from Pool {team.pool} with {team.pool_points} points")
