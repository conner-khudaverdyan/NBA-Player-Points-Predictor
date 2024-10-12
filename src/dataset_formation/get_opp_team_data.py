import pandas as pd
import numpy as np
import os

from nba_api.stats.endpoints import LeagueDashTeamStats
from feature_engineering.get_player_data import get_player_data


def convert_season_id(season_id):
    start_year = int(str(season_id)[1:5])
    end_year = start_year + 1
    return f"{start_year}-{str(end_year)[-2:]}"

def get_date_season(model_player_data):
        
    date_season = model_player_data.reset_index(drop = True)

    # Gather Season and Date for API function in next function
    date_season['GAME_DATE'] = pd.to_datetime(date_season['GAME_DATE'], format='%b %d, %Y')
    try:
        date_season['DATE'] = date_season['GAME_DATE'].apply(lambda x: x.strftime('%m/%d/%Y'))
    except Exception as e:
        print(date_season['GAME_DATE'])
    date_season['SEASON'] = date_season['SEASON_ID'].apply(convert_season_id)
    return date_season


def get_opp_team_data(model_player_data):
    opp_team_data = pd.DataFrame()

    date_season = get_date_season(model_player_data)
    
    # Getting Defense Data for teams accumulated from games before each date
    for season,date in zip(date_season['SEASON'], date_season['DATE']):

        #count = count +1 
        print(date)
        teams = pd.DataFrame(LeagueDashTeamStats(measure_type_detailed_defense = 'Defense',season = season, date_to_nullable=date, timeout=300).get_data_frames()[0])
        
        # Combine with other seasons
        teams['GAME_DATE'] = date
        opp_team_data = pd.concat([opp_team_data, teams])
        
    return opp_team_data

def save_opp_team_data(model_player_data):
    opp_team_data = get_opp_team_data(model_player_data)
    try: 
        file_path = os.path.join('..', 'data', 'opp_team_data.csv')
        opp_team_data.to_csv(file_path, index=False)
    
        print('Saved opp_team_data into Data directory')
        
    except Exception as e:
        print(f"Error saving to {file_path}, exception: {str(e)}")
        # Save in the current directory as a fallback
        fallback_file_path = 'opp_team_data.csv'
        opp_team_data.to_csv(fallback_file_path, index=False)
        print(f'Successfully saved opp_team_data into the src directory as {fallback_file_path}')


if __name__ == "__main__":
    
    file_path = os.path.join('..', 'data', 'model_player_data.csv')
    model_player_data = pd.read_csv(file_path)
    save_opp_team_data(model_player_data)