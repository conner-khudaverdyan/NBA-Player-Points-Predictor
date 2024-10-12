import numpy as np
import pandas as pd
import os
import argparse
# python3 -m dataset_formation.export_dataset

from feature_engineering.get_player_data import get_player_data
from dataset_formation.dataset_former import DatasetFormer

# Script that will create our dataset and save csv/pkl  files
    
def export_dataset(seasons, date_of_game_to_split, model_player_fullname ,factor_teammate_fullname):
    data = DatasetFormer(seasons=seasons, model_player_fullname=model_player_fullname, factor_teammate_fullname = factor_teammate_fullname)
    

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
    parser = argparse.ArgumentParser(description="Enter parameters to form your dataset, make sure you have model_player_data.csv, advanced_boxscores.pkl, traditional_boxscores.pkl, and opp_team_data.csv saved in the data directory before running.")
    
    parse.add_argument('Factor_Teammate_Fullname', type = str, help = 'Fullname of teammate you think significantly will impact the model player points, e.g.: "Anthony Davis"')
    
    parse.add_argument('season_range_start', type = int, help = 'First Season that defies range that you want to pool data from e.g.: 2019 refers to 2019-2020 season.')
    parse.add_argument('season_range_end', type = int, help = 'Last Season that defines range that you want to pool data from, must be greater than or equal to season_range_start. e.g.: if season_range_start is 2019, if you input 2020, the dataset will include data from 2019-2020 and  2020-2021 seasons.')
    parse.add_argument('date_of_game_to_split', type = str, help = 'If you want a training and test set to evaluate model, input a string in format MM/DD/YYYY, if you do not want one, just make the split the latest game possible')
    
    args = parser.parse_args()
    # Default for LeBron export_dataset(seasons = np.arange(2019, 2024, 1), date_of_game_to_split='01/15/2024',model_player_fullname = 'LeBron James' ,factor_teammate_fullname = 'Anthony Davis')
    seasons = np.arange(args.season_range_start, season_range_end, 1)
    export_dataset(seasons = seasons, date_of_game_to_split=args.date_of_game_to_split ,factor_teammate_fullname = args.Factor_Teammate_Fullname)
    


