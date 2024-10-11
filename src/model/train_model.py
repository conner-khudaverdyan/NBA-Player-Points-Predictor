import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# Script to Run and Save our Model

def train_model():
    try: 
        train_set = pd.read_csv('../data/train_set.csv')
        test_set = pd.read_csv('../data/test_set.csv')
    except Exception as e:
        print('Unable to load csv files, check to see if there are the following files in the data directory: train_set.csv, test_set.csv',e)
    
    
    X_train = train_set.drop(columns=['PTS'])
    y_train = train_set['PTS']
    X_test = test_set.drop(columns=['PTS'])
    y_test = test_set['PTS']

    # Ensure categorical variable is encoded numerically
    X_test['Factor_Teammate_Yes'] = X_test['Factor_Teammate_Yes'].apply(lambda x: 1 if x else 0)
    X_train['Factor_Teammate_Yes'] = X_train['Factor_Teammate_Yes'].apply(lambda x: 1 if x else 0)

    data_set_game_ids = pd.concat([X_train['Game_ID'], X_test['Game_ID']])

    # Isolate predictors
    X_train = X_train.loc[:, 'Player_PPG_last_5':]
    X_test = X_test.loc[:, 'Player_PPG_last_5':]

    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    joblib.dump(rf_model, 'model/random_forest_model')
    print("Model training complete and model saved.")

if __name__ == '__main__':
    
    try: 
        train_model()
    except Exeption as e:
        print('failed to train model',e)
        





