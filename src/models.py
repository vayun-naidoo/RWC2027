import json

# JSON decoder
def import_teams(json_file):
    try:
        with open(json_file, 'r') as f:
            teams = json.load(f)
        for team_name, wr_points in teams.items():
            team = Team(team_name, wr_points)
            #print(team)
    
    except FileNotFoundError:
        print(f"File {json_file} not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {json_file}.")


# Consider the team as read from WR rankings
class Team:
    def __init__(self, name = '', wr_ranking = 30.00):
        self.name = name
        self.wr_ranking = wr_ranking
    
    def __str__(self):
        return f"{self.name} (WR Points: {self.wr_ranking})"

# Consider the team as read from group stage with additional stats
class Group_Team(Team):
    def __init__(self, name, wr_ranking, group_points = None, points_for = None, points_against = None, tries_for = None, tries_against = None):
        super().__init__(name, wr_ranking)
        self.group_points = group_points # This is the actual W/L points in the group stage
        self.points_for = points_for
        self.points_against = points_against
        self.tries_for = tries_for
        self.tries_against = tries_against
    
    def __str__(self):
        return f"{self.name}  (Group Points: {self.group_points})"

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



import_teams('data/teams.json')