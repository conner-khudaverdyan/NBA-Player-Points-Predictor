import numpy as np
import pandas as pd
import os
import pickle

from feature_engineering.get_player_data import get_player_data

from feature_engineering.get_factor_teammate_status import FactorTeammateFeatures
from feature_engineering.rolling_averages import RollingAverages
from feature_engineeringn.get_team_def_off_ratings import OffDefRatings

class DatasetFormer:
    def __init__(self, seasons, model_player_fullname, factor_teammate_fullname, model_player_data):
        self.seasons = seasons
        self.model_player_name = model_player_fullname
        self.model_player_data  = model_player_data
        self.factor_teammate_name = factor_teammate_fullname
        
        self.train_set = None
        self.test_set = None
        self.dataset = None
        self.dataset_copy = None
        
        # Load traditional boxscores file from data directory
        try: 
            trad_path = os.path.join('..', 'data', 'traditional_boxscores.pkl')
            with open(trad_path, 'rb') as file:
                self.boxscores_data_by_season = pickle.load(file)  
            print('Successfully loaded traditional boxscores')
                 
        except Exception as e:
            print('Failed to initialize dataset former. Ensure that traditional_boxscores.pkl exists in data directory before running. If not, run get_trad_boxscores and try again')
            raise
        
        # Load advanced boxscores file from data directory
        try: 
            trad_path = os.path.join('..', 'data', 'advanced_boxscores.pkl')
            with open(trad_path, 'rb') as file:
                self.adv_boxscores_data_by_season = pickle.load(file) 
                
            print('Successfully loaded advanced boxscores') 
        except Exception as e:
            print('Failed to initialize dataset former. Ensure that advanced_boxscores.pkl exists in data directory before running. If not, run get_adv_boxscores and try again') 
            raise
        
        self.team_id = self.boxscores_data_by_season[0][self.boxscores_data_by_season[0]['PLAYER_NAME'] == self.factor_teammate_name]['TEAM_ID'].iloc[0]
        
    
    def get_dataframe_list(self):
        
        if (self.adv_boxscores_data_by_season  == None):
            print('adv boxscores are None')
        if  (self.boxscores_data_by_season == None):
            print('trad boxscores are None')
            print('Load boxscores first')
            return None
        
        print('Assembling all dataframes and features into list')
        
        # Gather and Compute Rolling Averages
        rolling_averages_computer = RollingAverages(seasons= self.seasons,  model_player_data = self.model_player_data, factor_teammate_name = self.factor_teammate_name, team_id = self.team_id)
        player_rolling_averages_ppg = rolling_averages_computer.get_player_rolling_avg_ppg(lag = 5)
        player_ppg_so_far = rolling_averages_computer.get_player_rolling_avg_ppg(total_ppg = True)
        team_rolling_avg_ppg = rolling_averages_computer.get_team_rolling_avg_ppg(lag = 5, boxscores_data_by_season= self.boxscores_data_by_season)
 
    
        # Gather factors of player that user deamed as the most to affect modeled player's points
        factor_teammate_feature_fetcher = FactorTeammateFeatures(seasons = self.seasons, factor_teammate_name = self.factor_teammate_name, model_player_data= self.model_player_data, team_id = self.team_id)
        factor_teammate_features = factor_teammate_feature_fetcher.get_factor_teammate_features()
        
        # Gather defensive Ratings of Team and Opponents
        off_def_retriever = OffDefRatings(seasons = self.seasons, model_player_data = self.model_player_data, adv_boxscores_data_by_season = self.adv_boxscores_data_by_season, team_id = self.team_id)
        opp_team_def_ratings = off_def_retriever.get_opp_team_def_ratings()
        opp_starter_def_ratings = off_def_retriever.get_opp_starter_def_ratings()
        starter_off_ratings = off_def_retriever.get_starter_off_ratings()

        
        # Combine into a list of dataframes
        print(factor_teammate_features.columns)
        return [player_rolling_averages_ppg,player_ppg_so_far,opp_team_def_ratings,factor_teammate_features, team_rolling_avg_ppg, opp_starter_def_ratings, starter_off_ratings]
     
     
    # Function to transform our list of dataframes into one large dataframe   
    def combine_dataframes(self):
        
        
        dataset = self.model_player_data[['Game_ID','PTS', 'SEASON_ID']]
        dataset['Game_ID'] = dataset['Game_ID'].astype(int)
        dataframe_list = self.get_dataframe_list()
        print('combining dataframes within dataframe list')
        for subset in dataframe_list:
            #print(subset['Game_ID'].dtype)
            #print(dataset)
            try: 
                subset['Game_ID'] = subset['Game_ID'].astype(int)
                dataset = dataset.merge(subset.drop(columns=['SEASON_ID', 'GAME_DATE']), on='Game_ID', how='left')
            except Exception as e:
                if ('SEASON_ID' not in subset.columns) and ('GAME_DATE' in subset.columns):
                    dataset = dataset.merge(subset.drop(columns=['GAME_DATE']), on='Game_ID', how='left')
                elif ('GAME_DATE' not in subset.columns) and ('SEASON_ID' in subset.columns):
                    dataset = dataset.merge(subset.drop(columns=['SEASON_ID']), on='Game_ID', how='left')
                else: dataset = dataset.merge(subset, on='Game_ID', how='left')
                    
        dataset['GAME_DATE'] = pd.to_datetime(dataframe_list[0]['GAME_DATE'])
        #print('Successfully Combined')
        return dataset
    
    def form_dataset(self):
        self.dataset = self.combine_dataframes()
        #self.dataset.copy = self.dataset.copy()
        
    # Function to divide our dataset into test and training split
    def train_test_divide(self,date_of_game_to_split): 
        if self.dataset == None:
            self.form_dataset()
            
        try: 
            index_of_game_to_split = self.dataset[self.dataset['GAME_DATE'] == date_of_game_to_split]['Game_ID'].index.tolist()[0]
        
        except Exception as e:
            print('Make sure date_of_game_to_split is in form mm/dd/yyyy')
            return None

        #dataset_copy = self.dataset.copy()

        self.dataset = self.dataset.drop(columns = ['SEASON_ID','TEAM_NAME', 'OPP_TEAM_ID',])
        self.dataset = self.dataset.sort_values(by = 'GAME_DATE').reset_index(drop = True)

        self.train_set = self.dataset.iloc[0:index_of_game_to_split,]
        self.test_set = self.dataset.iloc[_of_game_to_split:,]
    
    
    # Save funtion so that we do not have to reload dataset and boxscores repeatedly
    def save(self, filename):
        file_path = os.path.join('..', 'data', filename)
        with open(file_path, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename):
        file_path = os.path.join('..', 'data', filename)
        with open(file_path, 'rb') as f:
            return pickle.load(f)
        


    
