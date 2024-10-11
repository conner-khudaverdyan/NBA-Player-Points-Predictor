import numpy as np
import pandas as pd
import os
# python3 -m dataset_formation.export_dataset

from feature_engineering.get_player_data import get_player_data
from dataset_formation.dataset_former import DatasetFormer

# Script that will create our dataset and save csv/pkl  files
    
def export_dataset(seasons, date_of_game_to_split, model_player_fullname ,factor_teammate_fullname, model_player_data):
    model_player_data['SEASON_ID'] = model_player_data['SEASON_ID'].astype(str)
    model_player_data['Game_ID'] = model_player_data['Game_ID'].astype(str)
    
    data = DatasetFormer(seasons=seasons, model_player_fullname=model_player_fullname, factor_teammate_fullname = factor_teammate_fullname, model_player_data = model_player_data, filename = )
    

    # Split Training and Test set. (Defaul is midwaythrough 2023-2024 season)
    data.train_test_divide(date_of_game_to_split=date_of_game_to_split)
 
    
    # Save for potential further use
    data.save('dataset_object.pkl')
    
    train_set = data.train_set
    test_set = data.test_set

    train_set = train_set[~train_set['Player_PPG_last_5'].isna()].drop(columns={'GAME_DATE'})
    test_set = test_set[~test_set['Player_PPG_last_5'].isna()].drop(columns={'GAME_DATE'})

    train_set.to_csv('../data/train_set.csv', index=False)
    test_set.to_csv('../data/test_set.csv', index=False)
    print("Data preparation complete and CSV files saved.")
    
if __name__ == '__main__':
    file_path = os.path.join('..', 'data', 'model_player_data.csv')
    model_player_data = pd.read_csv(file_path)
    export_dataset(seasons = np.arange(2019, 2024, 1), date_of_game_to_split='01/15/2024',model_player_fullname = 'LeBron James' ,factor_teammate_fullname = 'Anthony Davis', model_player_data = model_player_data)
