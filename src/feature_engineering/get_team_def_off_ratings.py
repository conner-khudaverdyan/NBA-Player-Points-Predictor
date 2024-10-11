import numpy as np
import pandas as pd
import os

from feature_engineering.get_player_data import get_player_data
from dataset_formation.get_opp_team_data import get_date_season

from nba_api.stats.static import teams as ts
from nba_api.stats.endpoints import LeagueDashTeamStats

class OffDefRatings():
    def __init__(self, model_player_data, seasons,adv_boxscores_data_by_season, team_id):
        self.seasons= seasons
        self.adv_boxscores_data_by_season = adv_boxscores_data_by_season
        self.model_player_data = model_player_data
        self.model_player_id = self.model_player_data['Player_ID'].unique()[0]
        self.team_id = team_id
        
        self.opp_team_data = self.load_opp_team_data()
        self.date_season = get_date_season(self.model_player_data)

    def load_opp_team_data(self):
        try:
            # Define the file path where the CSV was saved
            file_path = os.path.join('..', 'data', 'opp_team_data.csv')
            
            # Load the CSV file into a DataFrame
            opp_team_data = pd.read_csv(file_path)
            print(f'Successfully loaded opp_team_data from {file_path}')
            return opp_team_data
            
        except FileNotFoundError:
            print(f'File not found at {file_path}')
            return None
                
        
    @staticmethod
    def extract_match_details(matchup):
        if 'vs.' in matchup:
            teams = matchup.split('vs.')
            game_type = 'home'
        elif '@' in matchup:
            teams = matchup.split('@')
            game_type = 'away'
        
        for team in teams:
            team = team.strip()
            if team != 'LAL':
                return [team, game_type]
            

    # Function find the Team ID for the assoicated abbreviation
    
    @staticmethod
    def abbrev_to_ID(abbreviation):
        nba_teams = ts.get_teams()
        team_abbrev_to_ID = {}
        
        for team in nba_teams:
            team_abbrev_to_ID[team['abbreviation']] = team['id']
            
        team_id = team_abbrev_to_ID[abbreviation]
        return team_id

    def get_id_from_abbrev(self, date_season):
        date_season[['OPP_TEAM_ABBREV', 'GAME_TYPE']] = date_season['MATCHUP'].apply(OffDefRatings.extract_match_details).apply(pd.Series)

        date_season['OPP_TEAM_ID'] = date_season['OPP_TEAM_ABBREV'].apply(OffDefRatings.abbrev_to_ID)

        return date_season['OPP_TEAM_ID']

        
    def get_opp_team_def_ratings(self):
        try:
            self.opp_team_data = self.opp_team_data.rename(columns = {'TEAM_ID': 'OPP_TEAM_ID'})
            self.date_season['OPP_TEAM_ID'] = self.get_id_from_abbrev(self.date_season)
            
            player_games_all_seasons = self.date_season[['Game_ID', 'MATCHUP', 'WL', 'PTS', 'DATE', 'SEASON_ID', 'OPP_TEAM_ID']].rename(columns = {'PTS': 'Player_PTS', 'DATE': 'GAME_DATE'})

            opp_defense_data = pd.merge(player_games_all_seasons, self.opp_team_data, on = ['GAME_DATE', 'OPP_TEAM_ID'], how = 'left') #.rename(columns = {'GAME_ID': 'Game_ID'})
            #print(opp_defense_data.columns)
            opp_defense_data = opp_defense_data[['Game_ID', 'GAME_DATE', 'SEASON_ID', 'OPP_TEAM_ID', 'TEAM_NAME', 'DEF_RATING', 'DEF_RATING_RANK']]
            
            return opp_defense_data
        except Exception as e:
            print('Failed to load Opposing Team Defense Data')
            raise

    def get_opp_adv_stats(self):
        adv_boxscores = pd.DataFrame()
        
        for boxscore in self.adv_boxscores_data_by_season:
            adv_boxscores = pd.concat([adv_boxscores, boxscore])
            
        opp_team_stats = adv_boxscores[adv_boxscores['teamId']!= self.team_id][['personId', 'gameId','position','defensiveRating','estimatedDefensiveRating', 'minutes']]
        
        return opp_team_stats

    # Function to return defense rating for each position
    def get_opp_starter_def_ratings(self):
        opp_team_stats = self.get_opp_adv_stats()

        opp_team_stats = opp_team_stats[opp_team_stats['position'] != '']
        position_def = pd.DataFrame()
        position_def['gameId'] = opp_team_stats['gameId'].sort_values().unique()

        # Categorize forwards by their minutes (how often on the floor)
        forwards = opp_team_stats[opp_team_stats['position'] == 'F'].sort_values(by=['gameId', 'minutes'], ascending=[True, False]) # ordering them by most minutes
        forwards['forward_type'] = forwards.groupby('gameId').cumcount().apply(lambda x: f'forward {x+1}')

        position_def['forward1_def_rating'] = forwards[forwards['forward_type'] == 'forward 1']['defensiveRating'].reset_index(drop = True)
        position_def['forward2_def_rating'] = forwards[forwards['forward_type'] == 'forward 2']['defensiveRating'].reset_index(drop = True)

        # Categorize guards by their minutes (how often on the floor)
        guards = opp_team_stats[opp_team_stats['position'] == 'G'].sort_values(by=['gameId', 'minutes'], ascending=[True, False]) # ordering them by most minutes
        guards['guard_type'] = guards.groupby('gameId').cumcount().apply(lambda x: f'guard {x+1}')

        position_def['guard1_def_rating'] = guards[guards['guard_type'] == 'guard 1']['defensiveRating'].reset_index(drop = True)
        position_def['guard2_def_rating'] = guards[guards['guard_type'] == 'guard 2']['defensiveRating'].reset_index(drop = True)


        centers = opp_team_stats[opp_team_stats['position'] == 'C'].sort_values(by=['gameId', 'minutes'], ascending=[True, False])
        position_def['center_def_rating'] = centers['defensiveRating'].reset_index(drop = True)
        position_def = position_def.rename(columns = {'gameId':'Game_ID'})
        
        return position_def

    @staticmethod
    def min_to_int(minutes):
        parts = minutes.split(':')

        mins = int(parts[0])
        seconds = int(parts[1])
        
        # Convert minutes to a fraction of an hour
        decimal= seconds / 60
        # Combine hours and decimal minutes
        decimal_time = mins + decimal
        
        return decimal_time

    def get_starter_off_ratings(self):
        adv_boxscores = pd.DataFrame()
        for boxscores in self.adv_boxscores_data_by_season:
            adv_boxscores = pd.concat([adv_boxscores, boxscores])
    
        team_stats = adv_boxscores[adv_boxscores['teamId']== self.team_id][['personId', 'gameId','position','offensiveRating', 'minutes']]
        team_stats = team_stats[team_stats['position'] != '']

        team_stats['minutes'] = team_stats['minutes'].apply(OffDefRatings.min_to_int)

        starter_stats = team_stats[team_stats['personId'] != self.model_player_id]
        
        
        starter_off = pd.DataFrame()
        starter_off['gameId'] = team_stats['gameId'].sort_values().unique()

        # Since our modeled player may not always be in a fixed role, we have to go through the tedious process of grouping the positions more generally
        center_off = starter_stats[starter_stats['position'] == 'C'][['gameId','offensiveRating']].rename(columns = {'offensiveRating': 'center_off'})

        # Categorize forwards by their minutes (how often on the floor)
        forwards = starter_stats[starter_stats['position'] == 'F'].sort_values(by=['gameId', 'minutes'], ascending=[True, False]) # ordering them by most minutes
        forwards['forward_type'] = forwards.groupby('gameId').cumcount().apply(lambda x: f'forward {x+1}')

        forward1_off = forwards[forwards['forward_type'] == 'forward 1'][['gameId','offensiveRating']]
        forward2_off = forwards[forwards['forward_type'] == 'forward 2'][['gameId', 'offensiveRating']]
        forward_off = pd.merge(forward1_off, forward2_off, on = 'gameId', how = 'outer', suffixes=('_forward1', '_forward2'))

        # There are games where the modeled player is a center. Grouping by outer make sure the avg is between the forwards. And when our player is a forward, it is the average of the other forward and the center
        forward_center_off = pd.merge(forward_off, center_off, on = 'gameId', how = 'outer')
        forward_center_off['forward_center_off_avg'] = forward_center_off[['offensiveRating_forward1', 'offensiveRating_forward2', 'center_off']].mean(axis=1)

        # Categorize guards by their minutes (how often on the floor)
        guards = starter_stats[starter_stats['position'] == 'G'].sort_values(by=['gameId', 'minutes'], ascending=[True, False]) # ordering them by most minutes
        guards['guard_type'] = guards.groupby('gameId').cumcount().apply(lambda x: f'guard {x+1}')


        guard1 = guards[guards['guard_type'] == 'guard 1'][['gameId','offensiveRating']]
        guard2 = guards[guards['guard_type'] == 'guard 2'][['gameId','offensiveRating']]

        # There are games where our player may be a guard, so on these games there is no guard2. grouping by outer make sure the avg is just guard1 offensive rating
        guard_off = pd.merge(guard1, guard2,on = 'gameId', how =  'outer' , suffixes=('_guard1', '_guard2'))
        guard_off['guard_off_avg'] = guard_off[['offensiveRating_guard1', 'offensiveRating_guard2']].mean(axis=1)

        # Merge guard and forward-center avg off ratings 
        starter_off = pd.merge(starter_off, forward_center_off, on = 'gameId', how = 'left')
        starter_off = pd.merge(starter_off, guard_off, on = 'gameId', how = 'left')
     
        starter_off = starter_off.rename(columns = {'gameId':'Game_ID'})[['Game_ID', 'guard_off_avg', 'forward_center_off_avg']]
        
        return starter_off

    