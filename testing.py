from src.models import Tournament

t = Tournament('data/teams.json')

t.play(print_statement=True)