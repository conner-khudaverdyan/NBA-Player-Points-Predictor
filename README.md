# NBA Player Points Predictor

## Description

The **NBA Player Points Predictor** project aims to predict the points scored by NBA players based on various features derived from historical game data. 
## Features

- Documentation of the original workflow in the `notebooks` directory, including data analysis, feature engineering, visualizations, model seletion, etc
- A codebase in the `src` directory engineered to allow users to create custom datasets and train personalized models based on their player of choice and selected parameters.

## Installation

### Prerequisites

For this project I used a conda environment and have included a YAML file with the specified requirements. If you do not you use conda, simply refer to the bball.yml file for the dependencies

### How to Install

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/NBA-Player-Points-Predictor.git
2. Navigate to the project directory:
   ```bash
   cd NBA-Player-Points-Predictor
  
4. Install the necessary dependencies. (See bball.yml)

5. Create a virtualenvironment using bball.yml and conda:
   ```bash
   conda env create -f bball.yml 

## Usage
### Jupyter Notebook
The project includes a Jupyter notebook containing a detailed walkthrough of my original workflow, statistical analysis and thought process while developing the model. You can open this notebook to explore the visualizations and commentary. Note that because the model is designed around predicitng a single player's points, I used LeBron James as a benchmark player for most of my analysis and model selection.

## Custom Model Training
To train your own model based on the player you want to model, navigate to the src directory:

You can use the provided scripts to create your own dataset and train a model by specifying the player and other parameters. 

1. *Collecting Raw Data*

The library I used to collect nba data, `nba_api`, often times out if there are multiple queries in a single file, so to create your own dataset you must run 4 different files in the following order: `get_model_player_data`, `get_opp_team_data`, `get_trad_boxscores`, and `get_adv_boxscores`. Each file contains an argument parser that allows for customization of the data you want to query 

3. *Exporting Functional Dataset*
   
Once you have saved all the necessary files using the 4 files above in the `data` directory , you can run the export_dataset file located in the `dataset_formation` directory which will then save your dataset to the main `data` directory

5. *Training Model*
   
Once you have saved your dataset, you can run the train file within the `model`  directory, which will save your model to the directory.

7. *Prediciting Points*
   
Now that you have trained your model, you can run the predict_points file to predict the points of your chosen player on any given set of games. The file will then return a dataframe contains the prediction as well as the actual points scored (If the game is yet to occur, the actual points value is NA)
