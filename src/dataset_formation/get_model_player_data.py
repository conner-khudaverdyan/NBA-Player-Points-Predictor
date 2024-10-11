import numpy as np
import pandas as pd
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
        opp_team_data.to_csv(fallback_file_path, index=False)
        print(f'Successfully saved model_player_data into the src directory as {fallback_file_path}')

if __name__ == "__main__":
    seasons = np.arange(2019, 2024, 1)
    save_player_data(seasons, 'LeBron James')
