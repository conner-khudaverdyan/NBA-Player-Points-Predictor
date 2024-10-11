import pandas as pd
import numpy as np

from feature_engineering.get_player_data import get_player_gamelog,get_player_team_games,  get_player_id, get_player_data
from nba_api.stats.endpoints import LeagueGameFinder
class FactorTeammateFeatures():
    def __init__(self, model_player_data, factor_teammate_name, team_id, seasons):
        self.seasons= seasons
        self.model_player_data = model_player_data
        self.team_id = team_id
        self.factor_teammate_name = factor_teammate_name

    def get_player_teammate_intersection(self):

        team_games = get_player_team_games(seasons = self.seasons, team_id = self.team_id)
        player_data = self.model_player_data
        teammate_data = get_player_data(self.seasons, self.factor_teammate_name)
        

        player_data['GAME_DATE'] = pd.to_datetime(player_data['GAME_DATE'], format = '%b %d, %Y')
        teammate_data['GAME_DATE'] = pd.to_datetime(teammate_data['GAME_DATE'], format = '%b %d, %Y')

        player_mins = player_data[['GAME_DATE', 'MIN']].rename(columns={'MIN': 'MIN_Model_Player'})
        factor_teammate_mins = teammate_data[['GAME_DATE', 'MIN']].rename(columns={'MIN': 'MIN_Factor_Teammate'})
        
        # Find games for the team of the player of interest
        game_finder = LeagueGameFinder(team_id_nullable= self.team_id)
        games_df = game_finder.get_data_frames()[0]
        
        # Convert to datetime
        games_df['GAME_DATE'] = pd.to_datetime(games_df['GAME_DATE'])
        
        # Find list of season ids corresponding to our list of seasons
        season_ids = []
        for season in self.seasons:
            season_id = '2' + str(season)
            season_ids.append(season_id)
        
        # Info on all games of our player's team within the specified seasons
        players_team_games = games_df[games_df['SEASON_ID'].isin(season_ids)]

        # Merging all three 
        merged_data = pd.merge(players_team_games[['SEASON_ID','GAME_DATE', 'GAME_ID']], player_mins, on='GAME_DATE', how='left')
        merged_data = pd.merge(merged_data, factor_teammate_mins, on='GAME_DATE', how='left')

        # NA's represent games where either our player of interest or our factor teammate missed a game (or barely participated)
        merged_data = merged_data.fillna(0)

        # Classify Games Factor Teammated played in as games he had more than 15 minutes played
        merged_data['Factor_Teammate_Yes'] = merged_data['MIN_Factor_Teammate']> 15
        
        return merged_data

    def get_factor_teammate_miss_streak(self):
        
        # Compute how many games in a row Factor Teammate (Davis) has missed prior to current Game
        streak_list = []
        game_ids = []
        merged_data = self.get_player_teammate_intersection()
        
        # Iterate through each row to calculate streak of missed games
        for season in self.seasons:
            missed_streak = 0
            
            # Divide by season to avoid streaks incrementing across seasons
            season_data = merged_data[merged_data['SEASON_ID'] == '2'+ str(season)].reset_index(drop = True)
            
            # Add streak of 0 and save game id for first game of every season
            streak_list.append(0)
            game_ids.append(season_data['GAME_ID'][0])
            
            # Start streak counter on second game of season
            for i in range(1, len(season_data['GAME_ID'])):
                for j in range(0,i):
                    if season_data['Factor_Teammate_Yes'][j]:
                        missed_streak = 0 # Reset streak counter
                    else:
                        missed_streak += 1  # Increment streak counter
                game_ids.append(season_data['GAME_ID'][i])
                streak_list.append(missed_streak) # Store current streak value
                
        factor_teammate_streak = pd.DataFrame({"Factor_Teammate_miss_streak" :streak_list, 'GAME_ID': game_ids})

        return factor_teammate_streak

    def get_factor_teammate_features(self):
        try: 
            streak = self.get_factor_teammate_miss_streak()
            status = self.get_player_teammate_intersection()
            
            features = pd.merge(status, streak, on = 'GAME_ID', how = 'left').rename(columns = {'GAME_ID': 'Game_ID'})
            
            print('Successfully retrieved Factor Teammate Features')
            return features
        
        except Exception as e:
            print('Failed to Load Factor Teamate features. To access the dataset try downloading the dataset csv directly from the repository',e)
            raise
            
        

if __name__ == "__main__":
    seasons = np.arange(2019, 2024, 1)
    ad_status_factors = get_ad_factors(seasons)
    
        
