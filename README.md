# NBA Player Points Predictor

## Description

The **NBA Player Points Predictor** project aims to predict the points scored by NBA players based on various features derived from historical game data. 
## Features

- Documentation of the original workflow, including data analysis, feature engineering, visualizations, model seletion, etc.
- A codebase in the `src` directory engineered to allow users to create custom datasets and train personalized models based on their player of choice and selected parameters.

## Installation

### Prerequisites

For this project I used a conda environment and have included a YAML file with the specified requirements. If you do not you use conda, simply refer to the bball.yml file for the dependencies

### How to Install

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/NBA-Player-Points-Predictor.git
2. Navigate to the project directory:

  cd NBA-Player-Points-Predictor
  
3. Install the necessary dependencies. (See bball.yml)
   create a conda environment using bball.yml

bash
Copy code
conda env create -f environment.yml
Usage
Jupyter Notebook
The project includes a Jupyter notebook that documents the entire thought process, from data analysis to model evaluation. You can open this notebook to explore the visualizations and commentary:

Start Jupyter Notebook:

bash
Copy code
jupyter notebook
Open the notebook file (e.g., NBA_Player_Points_Predictor_Analysis.ipynb) and follow along with the analysis.

Custom Model Training
To train your own model based on the player you want to model, navigate to the src directory:

bash
Copy code
cd src
You can use the provided scripts to create your own dataset and train a model by specifying the player and other parameters. Refer to the documentation within the code for specific usage instructions.

YAML Configuration
The project includes a YAML file (environment.yml) in the repository that specifies the dependencies needed for the project. This file can be used to create a conda environment or install dependencies easily.

To create a new conda environment from the YAML file, use:

bash
Copy code
conda env create -f environment.yml
