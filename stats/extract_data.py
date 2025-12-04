import pandas as pd

df = pd.read_csv('data/results.csv')

rwc_2023 = df[df['competition'] == '2023 Rugby World Cup']

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(rwc_2023)