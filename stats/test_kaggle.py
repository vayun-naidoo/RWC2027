from kaggle.api.kaggle_api_extended import KaggleApi
api = KaggleApi()
try:
    api.authenticate()
    print("Success! Kaggle is connected.")
except Exception as e:
    print(f"Error: {e}")