import nba_api
import numpy as np
import pandas as pd
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerCareerStats, PlayerGameLog 
from nba_api.stats.endpoints import LeagueGameFinder
from datetime import datetime


def get_player_gamelog(player_id, season):
    gamelog = PlayerGameLog(player_id=player_id, season=season)
    gamelog_df = gamelog.get_data_frames()[0]
    return gamelog_df


def get_player_id(fullname):
    player_id = players.find_players_by_full_name(fullname)[0]['id']

    return player_id

# Make function to gather Player Games 
def get_player_data(seasons, fullname):
    player_id = get_player_id(fullname)
    player_data = pd.DataFrame()

    for season in seasons:
        player_season_data = get_player_gamelog(player_id, season)
        player_data = pd.concat([player_data, player_season_data])
    
    return player_data
        
    
def get_player_team_games(team_id = '1610612747',seasons = '2023'):   # Los Angeles Lakers team ID

    # DataFrame of Team Games
    game_finder = LeagueGameFinder(team_id_nullable=team_id)
    game_data_frames = game_finder.get_data_frames()
    gdf = game_data_frames[0]

    # Convert game date to datetime

    gdf['GAME_DATE'] = pd.to_datetime(gdf['GAME_DATE'])
    team_games = gdf[gdf['SEASON_ID'].isin(seasons) ]
    return team_games


def get_game_ids_by_season(player_game_logs, seasons):
    game_ids_by_season = []
    for season in seasons:
        
        # Recall we are only interested in games LeBron played in, so we look at the game ids in lebron_data. 
        game_ids = player_game_logs[player_game_logs['SEASON_ID'] == '2'+ str(season)]['Game_ID']
        game_ids_by_season.append(game_ids)
    return game_ids_by_season

if __name__ == "__main__":
    try:
        seasons =  np.arange(2019, 2024, 1)
        lebron_data = get_player_data(seasons = seasons, fullname = 'LeBron James')

    except Exception as e:
        print('Failed to retrieve LeBron Data:', e)