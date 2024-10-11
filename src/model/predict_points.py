import numpy as np
import pandas as pd
from feature_engineering.get_player_data import get_player_data
from dataset_formation.dataset_former import DatasetFormer
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime
import joblib
import argparse


class Predictor:
    def __init__(self, model_file='model/random_forest_model'):
        self.model_file = model_file
        self.data = DatasetFormer.load('../data/dataset_object.pkl')
        self.model = joblib.load(self.model_file)
        self.new_data_file = new_data_file
        
    def get_data_rows(self, game_date_start, game_date_end, new_data_file):
        try: 
            # Get Desired Rows
            x = self.data.dataset[(self.data.dataset['GAME_DATE'] >= game_date_start) & (self.data.dataset['GAME_DATE'] <= game_date_end)] 
            
            # If new data, combine with old data
            if new_data_file:
                new_game_data = pd.read_csv(new_data_file)
                x = pd.concat(x, new_game_data)
            
            # Ensure categorical variable is encoded numerically
            x['Factor_Teammate_Yes'] = x['Factor_Teammate_Yes'].apply(lambda x: 1 if x else 0)
            x['Factor_Teammate_Yes'] = x['Factor_Teammate_Yes'].apply(lambda x: 1 if x else 0)
            
            return x

        except Exception as e:
            print('One or more games failed to meet requirements for model. The Player either did not participate in any of the games or  was in the first games of the season (set by lag parameter in Rolling Averages, default is 5)',e)
            return None
    

        
    def classify_data_origin(self, game_date):
        first_test_game_date = self.data.test_set['GAME_DATE'].min()
        last_test_game_date = self.data.test_set['GAME_DATE'].max()
        
        if game_date < first_test_game_date:
            return 'Training Set'
        elif game_date< last_test_game_date:
            return 'Test Set'
        elif game_date > last_test_game_date:
            return 'New Data'
        else:
            return 'No Game Found'
        
    def predict_points(self,game_date_start, game_date_end, new_data_file = None):
        # Convert input parameters to datetime
        start_date = datetime.strptime(game_date_start, '%m/%d/%y')
        end_date = datetime.strptime(game_date_end, '%m/%d/%y')
            
        x =  self.get_data_rows(start_date, end_date, new_data_file)
        print(x)
    
        pred_df = pd.DataFrame()
        
        # Column to indiciate if data was training, test, or completely fresh data
        pred_df['Dataset_Origin'] = x['GAME_DATE'].apply(lambda date: self.classify_data_origin(date))

        # Column for comparison to actual values
        pred_df['Actual_PTS'] = x['PTS']
        
        # Remove unnecessary columns for prediction
        x = x.drop(columns = ['GAME_DATE', 'PTS', 'Game_ID'])
        
        # Make predictions on dataset 
        predictions = self.model.predict(x)
        pred_df['Prediction'] = predictions
        
        return pred_df
    
        
            
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Predict Player points for a given game date.")
    #parser.add_argument('game_date', type=str, help="Date of the game in MM/DD/YYYY format")
    parser.add_argument('game_date_start', type = str, help= "Inclusive, Date in format: 'MM/DD/YYYY ")
    parser.add_argument('game_date_end', type = str, help= "Inclusive, Date in format: 'MM/DD/YYYY ")
    parser.add_argument('--new_data_file', type=str, help="Path to CSV file containing new data in the format of a pandas dataframe", default=None) 
    
    args = parser.parse_args()

    new_data_file = None
    if args.new_data_file:
        new_data_file = pd.read_csv(args.new_data_file)
        
    model = Predictor(model_file='model/random_forest_model')
    prediction_df = model.predict_points(game_date_start=args.game_date_start, game_date_end = args.game_date_end,new_data_file = new_data_file)

    if prediction_df is not None:
        print(f"Predicted points for games from {args.game_date_start} to {args.game_date_end}: \n {prediction_df}")
