import nba_api
import numpy as np
import pandas as pd
import pickle
import os

from feature_engineering.get_player_data import get_game_ids_by_season, get_player_data
from nba_api.stats.endpoints import BoxScoreTraditionalV2


# Create function to gather boxscores for all games LeBron has participated in

def get_boxscores_data_by_season(seasons, player_game_logs):
    try: 
        boxscores_data_by_season = []
        game_ids_by_season = get_game_ids_by_season(player_game_logs=player_game_logs, seasons = seasons)
        # Iterate through each season
        for season_game_ids in game_ids_by_season:
            boxscores_data = pd.DataFrame()
            
            # Iterate through each game id 
            for game_id in season_game_ids:

                boxscore = BoxScoreTraditionalV2(game_id=game_id)
                boxscore_data = boxscore.get_data_frames()[0]
            
                # Combine Box Score with rest
                boxscores_data = pd.concat([boxscores_data, boxscore_data])
               
                
            # Add season box scores to list 
            boxscores_data_by_season.append(boxscores_data)
            
            print('Added Season Box Scores')
            
        print('Extracted Boxscores for all Seasons')
        
        # Return list of dataframes containing boxscores from each season
        return boxscores_data_by_season
    
    except Exception as e:
        print('Failed to load boxscores. If due to timeout, try again later or with vpn')
        raise
    
def save_trad_boxscores(seasons, model_player_fullname):
    
    print('Collecting Traditional Boxscores, this may take a few mintes')
    model_player_data = get_player_data(seasons = seasons, fullname = model_player_fullname)
    boxscores_data_by_season = get_boxscores_data_by_season(seasons = seasons, player_game_logs= model_player_data)
   
    try: 
        file_path = file_path = os.path.join('..', 'data', 'traditional_boxscores')
        with open(f"{file_path}.pkl", 'wb') as file:
            pickle.dump(boxscores_data_by_season, file)
        print('Saved into Data directory')
        
    except Exception as e:
        with open(f"{'traditional_boxscores'}.pkl", 'wb') as file:
            pickle.dump(boxscores_data_by_season, file)
        print('Saved into src directory')

if __name__ == "__main__":
    seasons = np.arange(2019, 2024, 1)
    save_trad_boxscores(seasons  = seasons, model_player_fullname = 'LeBron James')