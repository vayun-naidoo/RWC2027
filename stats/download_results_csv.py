import kaggle

def download_csv():
    dataset_slug = 'lylebegbie/international-rugby-union-results-from-18712022' 
    download_path = './data'
    kaggle.api.dataset_download_files(dataset_slug, path=download_path, unzip=True)

