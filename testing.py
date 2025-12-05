from src.models import Tournament

t = Tournament('data/teams.json')

t.play(print_results=True, print_statement=True)