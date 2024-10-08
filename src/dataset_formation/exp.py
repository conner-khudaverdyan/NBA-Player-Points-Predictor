
import numpy as np
import pandas as pd
import os
import pickle
import time

from data_collection.get_player_data import *
from dataset_formation.get_trad_boxscores import *
from dataset_formation.dataset_former import DatasetFormer
from data_collection.get_factor_teammate_status import FactorTeammateFeatures
from nba_api.stats.endpoints import LeagueGameFinder

seasons = np.arange(2019, 2024, 1)
print('Getting Lebron Data')
lebron_data = get_player_data(fullname = 'LeBron James', seasons = seasons)
print('finished')
time.sleep(30)
print('Getting boxscores')
get_boxscores_data_by_season(seasons = seasons , player_game_logs =  lebron_data)

#file_path = os.path.join('..', 'data', 'dataset_object.pkl')

#dataset = DatasetFormer.load(file_path)
#file_path = os.path.join('..', 'data', 'model_player_data.csv')
#model_player_data = pd.read_csv(file_path)

#data  = DatasetFormer('Lebron James', 'Anthony Davis', model_player_data)

#print(dataset.dataset['Factor_Teammate_Yes'])

'''
seasons = np.arange(2019, 2024, 1)
factor_teammate_feature_fetcher = FactorTeammateFeatures(seasons = seasons, factor_teammate_name = 'Anthony Davis', model_player_data= model_player_data, team_id = '1610612747')
factor_teammate_features = factor_teammate_feature_fetcher.get_factor_teammate_features()
#print(factor_teammate_features['Game_ID'].dtype)
#print(model_player_data['Game_ID'].dtype)
#print(factor_teammate_features[factor_teammate_features['Game_ID'].astype(str).isin(model_player_data['Game_ID'].astype(str))])
print(factor_teammate_features['Game_ID'])
bruh = LeagueGameFinder(team_id_nullable = '1610612747').get_data_frames()[0]
print(factor_teammate_features[factor_teammate_features['Game_ID'].isin(bruh['GAME_ID'])])
print(factor_teammate_features[factor_teammate_features['Game_ID'].astype(int).isin(model_player_data['Game_ID'])])
'''

#seasons = np.arange(2019, 2024, 1)
#get_adv_boxscores_by_season()
