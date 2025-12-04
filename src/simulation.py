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
third_place_teams = []

for pool in [Pool_A, Pool_B, Pool_C, Pool_D, Pool_E, Pool_F]:
    pool.sort_teams_by_points()
    top_2_teams.extend(pool.teams[:2])
    third_place_teams.append(pool.teams[2]) 

third_place_teams.sort(key=lambda x: (-x.pool_points, -x.get_differential(), -x.get_try_differential(), -x.points_for, -x.tries_for))

# Top two from each pool advance to knockout stage
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
print('C/E/F best:', cef_best.name)

def_best = max((t for t in third_place_teams if t.pool in ['D', 'E', 'F']), key = lambda x: x.pool_points)
third_place_teams.remove(def_best)
print('D/E/F best:', def_best.name)

aef_best = max((t for t in third_place_teams if t.pool in ['A', 'E', 'F']), key = lambda x: x.pool_points)
third_place_teams.remove(aef_best)
print('A/E/F best:', aef_best.name)

bef_best = max((t for t in third_place_teams if t.pool in ['B', 'E', 'F']), key = lambda x: x.pool_points)
third_place_teams.remove(bef_best)
print('B/E/F best:', bef_best.name,)

print("=" * 100)
# ===============================
# KNOCKOUT: R16
# ===============================

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

print("Knockout Bracket - R16:")
# Left hand side of bracket
R16_1 = Match(a_1st, cef_best, True).play_knockout_match()
print(f'{R16_1[0][0].name} {R16_1[0][1]} - {R16_1[1][0].name} {R16_1[1][1]}')
R16_1_winner = (R16_1[0][0], R16_1[1][0])[R16_1[0][1] - R16_1[1][1] < 0]

R16_2 = Match(b_1st, def_best, True).play_knockout_match()
print(f'{R16_2[0][0].name} {R16_2[0][1]} - {R16_2[1][0].name} {R16_2[1][1]}')
R16_2_winner = (R16_2[0][0], R16_2[1][0])[R16_2[0][1] - R16_2[1][1] < 0]
print()

R16_3 = Match(c_2nd, f_2nd, True).play_knockout_match()
print(f'{R16_3[0][0].name} {R16_3[0][1]} - {R16_3[1][0].name} {R16_3[1][1]}')
R16_3_winner = (R16_3[0][0], R16_3[1][0])[R16_3[0][1] - R16_3[1][1] < 0]

R16_4 = Match(e_1st, d_2nd, True).play_knockout_match()
print(f'{R16_4[0][0].name} {R16_4[0][1]} - {R16_4[1][0].name} {R16_4[1][1]}')
R16_4_winner = (R16_4[0][0], R16_4[1][0])[R16_4[0][1] - R16_4[1][1] < 0]
print()

# Right hand side of bracket
R16_5 = Match(a_2nd, e_2nd, True).play_knockout_match()
print(f'{R16_5[0][0].name} {R16_5[0][1]} - {R16_5[1][0].name} {R16_5[1][1]}')
R16_5_winner = (R16_5[0][0], R16_5[1][0])[R16_5[0][1] - R16_5[1][1] < 0]

R16_6 = Match(f_1st, b_2nd, True).play_knockout_match()
print(f'{R16_6[0][0].name} {R16_6[0][1]} - {R16_6[1][0].name} {R16_6[1][1]}')
R16_6_winner = (R16_6[0][0], R16_6[1][0])[R16_6[0][1] - R16_6[1][1] < 0]
print()

R16_7 = Match(c_1st, aef_best, True).play_knockout_match()
print(f'{R16_7[0][0].name} {R16_7[0][1]} - {R16_7[1][0].name} {R16_7[1][1]}')
R16_7_winner = (R16_7[0][0], R16_7[1][0])[R16_7[0][1] - R16_7[1][1] < 0]

R16_8 = Match(d_1st, bef_best, True).play_knockout_match()
print(f'{R16_8[0][0].name} {R16_8[0][1]} - {R16_8[1][0].name} {R16_8[1][1]}')
R16_8_winner = (R16_8[0][0], R16_8[1][0])[R16_8[0][1] - R16_8[1][1] < 0]
print()

print(f'{R16_1_winner.name} to play {R16_2_winner.name} in QF1')
print(f'{R16_3_winner.name} to play {R16_4_winner.name} in QF2')
print(f'{R16_5_winner.name} to play {R16_6_winner.name} in QF3')
print(f'{R16_7_winner.name} to play {R16_8_winner.name} in QF4')
print("=" * 100)

# ===============================
# KNOCKOUT: QF
# ===============================
print("Knockout Bracket - QF")
QF1 = Match(R16_1_winner, R16_2_winner, True).play_knockout_match()
print(f'{QF1[0][0].name} {QF1[0][1]} - {QF1[1][0].name} {QF1[1][1]}')
QF1_winner = (QF1[0][0], QF1[1][0])[QF1[0][1] - QF1[1][1] < 0]

QF2 = Match(R16_3_winner, R16_4_winner, True).play_knockout_match()
print(f'{QF2[0][0].name} {QF2[0][1]} - {QF2[1][0].name} {QF2[1][1]}')
QF2_winner = (QF2[0][0], QF2[1][0])[QF2[0][1] - QF2[1][1] < 0]
print()

QF3 = Match(R16_5_winner, R16_6_winner, True).play_knockout_match()
print(f'{QF3[0][0].name} {QF3[0][1]} - {QF3[1][0].name} {QF3[1][1]}')
QF3_winner = (QF3[0][0], QF3[1][0])[QF3[0][1] - QF3[1][1] < 0]

QF4 = Match(R16_7_winner, R16_8_winner, True).play_knockout_match()
print(f'{QF4[0][0].name} {QF4[0][1]} - {QF4[1][0].name} {QF4[1][1]}')
QF4_winner = (QF4[0][0], QF4[1][0])[QF4[0][1] - QF4[1][1] < 0]
print()

print(f'{QF1_winner.name} to play {QF2_winner.name} in SF1')
print(f'{QF3_winner.name} to play {QF4_winner.name} in SF2')
print("=" * 100)

# ===============================
# KNOCKOUT: SF
# ===============================
print("Knockout Bracket - SF")
SF1 = Match(QF1_winner, QF2_winner, True).play_knockout_match()
print(f'{SF1[0][0].name} {SF1[0][1]} - {SF1[1][0].name} {SF1[1][1]}')
SF1_winner = (SF1[0][0], SF1[1][0])[SF1[0][1] - SF1[1][1] < 0]
SF1_loser = (SF1[0][0], SF1[1][0])[SF1[0][1] - SF1[1][1] > 0]

SF2 = Match(QF3_winner, QF4_winner, True).play_knockout_match()
print(f'{SF2[0][0].name} {SF2[0][1]} - {SF2[1][0].name} {SF2[1][1]}')
SF2_winner = (SF2[0][0], SF2[1][0])[SF2[0][1] - SF2[1][1] < 0]
SF2_loser = (SF2[0][0], SF2[1][0])[SF2[0][1] - SF2[1][1] > 0]

print()
print(f'{SF1_loser.name} to play {SF2_loser.name} in Bronze Final')
print(f'{SF1_winner.name} to play {SF2_winner.name} in Final')
print('=' * 100)

# ===============================
# KNOCKOUT: Finals
# ===============================

BF = Match(SF1_loser, SF2_loser, True).play_knockout_match()
print(f'{BF[0][0].name} {BF[0][1]} - {BF[1][0].name} {BF[1][1]}')
BF_winner = (BF[0][0], BF[1][0])[BF[0][1] - BF[1][1] < 0]
print(f'{BF_winner.name} wins bronze.\n')

final = Match(SF1_winner, SF2_winner, True).play_knockout_match()
print(f'{final[0][0].name} {final[0][1]} - {final[1][0].name} {final[1][1]}')
champion = (final[0][0], final[1][0])[final[0][1] - final[1][1] < 0]
print(f'{champion.name} wins MRWC 2027!')