import pandas as pd
import numpy as np
import pickle
import os

from data_collection.get_player_data import get_player_data, get_game_ids_by_season
from nba_api.stats.endpoints import BoxScoreAdvancedV3

# Function to gather advanced boxscores for all games LeBron has played in
def get_adv_boxscores_data_by_season(seasons, player_game_logs):
    try: 
        adv_boxscores_data_by_season = []
        game_ids_by_season = get_game_ids_by_season(player_game_logs=player_game_logs, seasons = seasons)
        
        # Iterate through each season      
        for season_game_ids in game_ids_by_season:
            boxscores_data = pd.DataFrame()
            
            # Iterate through each game id 
            for game_id in season_game_ids:
                boxscore = BoxScoreAdvancedV3(game_id=game_id)
                boxscore_data = boxscore.get_data_frames()[0]
            
                # Combine Box Score with rest
                boxscores_data = pd.concat([boxscores_data, boxscore_data])
                #print('Added Box Score')
                
            # Add season box scores to list 
            adv_boxscores_data_by_season.append(boxscores_data)
            
            print('Added Season Advanced Box Scores')
        
        print('Extracted Advanced Boxscores for all Seasons')
        
        # Return list of dataframes containing boxscores from each season
        return adv_boxscores_data_by_season           
    except Exception as e:
        print('Failed to Load Advanced Boxscores. If due to timeout, try again later or with vpn', e)

def save_adv_boxscores(seasons, model_player_fullname):
    
    print('Collecting Advanced Boxscores, this may take a few mintes')
    model_player_data = get_player_data(seasons = seasons, fullname = model_player_fullname)
    adv_boxscores_data_by_season = get_adv_boxscores_data_by_season(seasons = seasons, player_game_logs= model_player_data)

    try: 
        file_path = os.path.join('..', 'data', f"{'advanced_boxscores'}")
        with open(f"{file_path}.pkl", 'wb') as file:
            pickle.dump(adv_boxscores_data_by_season, file)
        print('Saved into Data directory')
        
    except Exception as e:
        with open(f"{'advanced_boxscores'}.pkl", 'wb') as file:
            pickle.dump(adv_boxscores_data_by_season, file)
        print('Saved into src directory')
        
if __name__ == "__main__":
    seasons = np.arange(2019, 2024, 1)
    save_adv_boxscores(seasons  = seasons, model_player_fullname = 'LeBron James')