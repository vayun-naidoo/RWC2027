import json

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
    def __init__(self, team1, team2, team1_score = None, team1_tries = None, team2_tries = None, team2_score = None):
        self.team1 = team1
        self.team2 = team2
        self.team1_tries = team1_tries
        self.team2_tries = team2_tries
        self.team1_score = team1_score
        self.team2_score = team2_score
    
    def play_match(self):
        # Placeholder for match simulation logic
        pass

teams = import_teams('data/teams.json')

for t in teams:
    print(t)