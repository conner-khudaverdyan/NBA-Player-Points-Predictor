import numpy as np
import pandas as pd
import argparse
import os

from feature_engineering.get_player_data import get_player_data

def save_player_data(seasons, model_player_fullname):
    
    model_player_data = get_player_data(seasons = seasons, fullname =model_player_fullname)
    file_path =  os.path.join('..', 'data', 'model_player_data.csv')
    
    try: 
        model_player_data.to_csv(file_path, index=False)
    
        print('Saved model_player_data into Data directory')
        
    except Exception as e:
        print(f"Error saving to {file_path}, exception: {str(e)}")
        # Save in the current directory as a fallback
        fallback_file_path = 'model_player_data.csv'
        model_player_data.to_csv(fallback_file_path, index=False)
        print(f'Successfully saved model_player_data into the src directory as {fallback_file_path}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enter parameters to gather basic data for modeled Plau.")
    
    parser.add_argument('Model_Player_Fullname', type = str, help = 'Fullname of player you want to model, e.g.: "LeBron James"')
    parser.add_argument('season_range_start', type = int, help = 'First Season that defies range that you want to pool data from e.g.: 2019 refers to 2019-2020 season.')
    parser.add_argument('season_range_end', type = int, help = 'Last Season that defines range that you want to pool data from, must be greater than or equal to season_range_start. e.g.: if season_range_start is 2019, if you input 2020, the dataset will include data from 2019-2020 and  2020-2021 seasons.')
    
    args = parser.parse_args()
    seasons = np.arange(args.season_range_start, args.season_range_end, 1)
    save_player_data(seasons, args.Model_Player_Fullname)
    
    #seasons = np.arange(2019, 2024, 1)
    #save_player_data(seasons, 'LeBron James')
