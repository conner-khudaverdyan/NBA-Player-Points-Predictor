import pandas as pd
import numpy as np

from nba_api.stats.endpoints import LeagueGameFinder, CommonPlayerInfo
from feature_engineering.get_player_data import get_player_data

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
class RollingAverages:
    def __init__(self, model_player_data, team_id, factor_teammate_name, seasons):
        self.seasons =seasons
        self.model_player_data = model_player_data
        self.player_id = self.model_player_data['Player_ID'].unique()[0]
        self.player_name = CommonPlayerInfo(self.player_id).get_data_frames()[0]['DISPLAY_FIRST_LAST'][0]
        self.factor_teammate_name = factor_teammate_name
        self.team_id = team_id
        
        
        # The teammate that the user decides will likely affect our players points the most
        self.factor_teammate_name = self.factor_teammate_name
    
    def get_player_rolling_avg_ppg(self, lag = None, total_ppg = None,):
        try:
            if total_ppg:
                output= pd.DataFrame(columns =  ['SEASON_ID','Player_PPG_so_far', 'Game_ID'])
            else:
                output = pd.DataFrame(columns = ['SEASON_ID','Player_PPG_last_5', 'Game_ID'] )

            # Iterate by season
            for season in self.seasons:
                season_id  = '2' + str(season)
                season_data = self.model_player_data[self.model_player_data['SEASON_ID']==season_id]
                
                # Make sure data is sorted by Game Date
                season_data = season_data.sort_values(by = 'GAME_DATE').reset_index()
        
                # Define variables for iteration
                game_id = season_data['Game_ID'] 
                game_date = season_data['GAME_DATE']
                
                season_points = season_data['PTS'] 
                games_played = len(season_points)   
                
                # Add NaN for the first lagged games of every season
                
                if not total_ppg:  
                    for i in range(0, lag):
                        new_row = pd.DataFrame({'SEASON_ID' : [season_id], 'Player_PPG_last_5' : None, 'Game_ID': game_id[i], 'GAME_DATE': game_date[i]})      
                        output = pd.concat([output, new_row], ignore_index=True)  
                    
                    # Compute and add the Rolling Averages for every game after the 5th game. 
                    for i in range(lag, games_played):
                        # Compute the average of the last 5 games
                        avg_last_lag = np.mean(season_points[i-lag:i])
                        # Append the average to the rolling averages list
                        new_row = pd.DataFrame({'SEASON_ID' : [season_id], 'Player_PPG_last_5' : [avg_last_lag], 'Game_ID': game_id[i],'GAME_DATE': game_date[i]})
                        
                        output = pd.concat([output, new_row], ignore_index=True)
                
                else:
                    for i in range(0, games_played):
                        avg_so_far = np.mean(season_points[0:i])
                        new_row = pd.DataFrame({'SEASON_ID' : [season_id], 'Player_PPG_so_far' : [avg_so_far], 'Game_ID': game_id[i],'GAME_DATE': game_date[i]})
                        
                        output = pd.concat([output, new_row], ignore_index=True)
                
            print('Successfully computed Player Rolling Average PPG')    
            return output 
        
        except Exception as e:
            print('Failed to load Player Rolling Average PPG. Instead, try directly importing the premade dataset csv directly from the repository',e )
            raise


    def get_team_rolling_avg_ppg(self, boxscores_data_by_season, lag = None, total_ppg = None):
        try: 
            team_rolling_averages_ppg = pd.DataFrame(columns = ['SEASON_ID','Starters_PPG_last_5', 'Bench_PPG_last_5','Game_ID', 'GAME_DATE'] )

            # Iterate through the list of boxscores for each season
            for season, boxscores in zip(self.seasons, boxscores_data_by_season):
                

                boxscores = boxscores[boxscores['TEAM_ID'] == self.team_id].reset_index() # only player data from our team
                game_ids = boxscores['GAME_ID'].unique() 
                season_id = '2' + str(season)
                
                # Utilize another dataframe that contains GAME_DATE because the boxscores for some reason don't have GAME_DATE
                check = LeagueGameFinder(team_id_nullable = '1610612747').get_data_frames()[0]
                check = check[check['GAME_ID'].isin(game_ids)]
                check['GAME_DATE'] = pd.to_datetime(check['GAME_DATE'])
                game_dates = check[['GAME_ID', 'GAME_DATE']]


                # Identify Starters
                boxscores['Starter'] = boxscores['START_POSITION'] != ''
                
                # Sum up the points for Starters and Bench
                starter_bench_pts = pd.DataFrame(boxscores.groupby(['GAME_ID','Starter'])['PTS'].sum()).reset_index()
                starter_bench_pts = pd.merge(starter_bench_pts, game_dates, on =  'GAME_ID', how = 'left')
                starter_bench_pts = starter_bench_pts.sort_values(by = 'GAME_DATE').reset_index()
                
            
                
                # Split between Starters and Bench
                starter_pts = starter_bench_pts[starter_bench_pts['Starter'] == True].reset_index()
                bench_pts =  starter_bench_pts[starter_bench_pts['Starter'] == False].reset_index()
                #print(starter_pts)
                #print(bench_pts)
                # Get Our model Player's (LeBron's) Points
                model_player_pts = boxscores[boxscores['PLAYER_NAME'] == self.player_name].reset_index()
                model_player_pts = pd.merge(model_player_pts, game_dates, on =  'GAME_ID', how = 'left')
                model_player_pts = model_player_pts.sort_values(by='GAME_DATE').drop_duplicates(subset='GAME_ID', keep='first').reset_index(drop = True)
                
                # Get The Factor Teammate's Points (Anthony Davis)
                factor_teammate_boxscores = boxscores[boxscores['PLAYER_NAME'] == self.factor_teammate_name].rename(columns = {'PTS': 'Factor_Teammate_PTS'})
                factor_teammate_pts = pd.merge(model_player_pts, factor_teammate_boxscores[['GAME_ID', 'Factor_Teammate_PTS']], on = 'GAME_ID',how = 'left')[['Factor_Teammate_PTS', 'GAME_ID']].fillna(0)

                
                # Compute Starter PTS minus the PTS our modeled player (LeBron) and most important teammate (Anthony) contribute
                starter_pts['isolated_PTS'] = starter_pts['PTS'] - model_player_pts['PTS'] - factor_teammate_pts['Factor_Teammate_PTS']
                #print(starter_pts)
                games_played = len(model_player_pts)

                # Sorted ID's and Dates
                game_ids = starter_pts['GAME_ID']
                game_dates = starter_pts['GAME_DATE']
                
                # Add NaN for the first 5 games of every season
                for i in range(0, lag):
                    
                    new_row = pd.DataFrame({'SEASON_ID' : [season_id], 'Starters_PPG_last_5' : None, 'Bench_PPG_last_5':None, 'Game_ID': game_ids[i], 'GAME_DATE': game_dates[i]})      
                    team_rolling_averages_ppg = pd.concat([team_rolling_averages_ppg, new_row], ignore_index=True) 
                    #bench_rolling_averages_ppg = pd.concat([bench_rolling_averages_ppg, new_row], ignore_index=True)   
                
                # Compute and add the Rolling Averages for every game after the 5th game. 
                for i in range(lag, games_played):
                
                    # Compute the average of the last 5 games
                    starter_avg_last_5 = np.mean(starter_pts['isolated_PTS'][i-5:i])
                  
                    bench_avg_last_5 = np.mean(bench_pts['PTS'][i-5:i])
                    date = starter_pts['GAME_DATE']
                    # Create row containing rolling average
                    
                    team_new_row = pd.DataFrame({'SEASON_ID' : [season_id], 'Starters_PPG_last_5' : [starter_avg_last_5], 'Bench_PPG_last_5' : [bench_avg_last_5],'Game_ID': game_ids[i],'GAME_DATE': game_dates[i]})
                    
                    # Add row to existing Data Frame
                    team_rolling_averages_ppg = pd.concat([team_rolling_averages_ppg, team_new_row], ignore_index=True)
        
            team_rolling_averages_ppg = team_rolling_averages_ppg[team_rolling_averages_ppg['Game_ID'].astype(int).isin(self.model_player_data['Game_ID'].astype(int))]
            
            print('Successfully computed Team Rolling Average PPG')
            
            return team_rolling_averages_ppg
        
        except Exception as e:
            print('Failed to compute Team Rolling Averages. Instead, try directly importing the premade dataset csv directly from the repository', e)
            raise

if __name__ == "__main__":
    seasons = np.arange(2019, 2024, 1)
    lebron_data = get_player_data(seasons = seasons, fullname = 'LeBron James')
    
    boxscores_data_by_season = get_boxscores_data_by_season(seasons=seasons, player_game_logs=lebron_data)
    
    roll = RollingAverages(seasons= seasons, model_player_data = lebron_data, factor_teammate_name = 'Anthony Davis')
    
    lebron_rolling_averages_ppg = roll.get_player_rolling_avg_ppg(lag = 5)
    lebron_ppg_so_far = roll.get_player_rolling_avg_ppg(total_ppg = True)

    team_rolling_avg_ppg = roll.get_team_rolling_avg_ppg(lag = 5, boxscores_data_by_season= boxscores_data_by_season)
 