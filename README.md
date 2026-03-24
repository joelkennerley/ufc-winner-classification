# UFC Winner Classification
This project aims to classify the winner of a UFC fight based on historical fight data using machine learning techniques.

# Overview
Using historical data scraped from UFCStats.com, this project builds a classification model to predict the winner of a UFC fight based on pre-fight statistics. The current model uses a Random Forest Classifier from the scikit-learn library and is trained and evaluated using cross-validation, achieving an accuracy of approximately 68%. The predictions for the next ufc fight card is then displayed through a webapp.

## Running the program
1. Clone the repo into your ide
2. pip install -r requirements.txt
3. Run app.py and navigate to http://127.0.0.1:5000 in your browser. Note this may take a moment to load as it scrapes and processes live data.

## Technologies/Libraries
- Python
- Pandas: For data cleaning and preprocessing
- scikit-learn: For model training and evaluation
- Collections
- Numpy
- Data sourced via web scraping (see [previous project](https://github.com/joelkennerley/ufc-stats-scraper) for scraping details)
- Flask: For UI

## Data
The dataset was gathered by scraping detailed fight statistics from UFCStats.com, including:
- Fighter physical attributes (height, reach, weight class)
- Striking and grappling stats
- Fight history
- Pre-fight performance metrics

## Model
- Algorithm: Random Forest Classifier
- Features: A selection of fight and fighter-based statistics
- Target: Winner (binary classification – either Fighter A or Fighter B)
- Validation: K-fold cross-validation
- Performance: ~68% accuracy on testing

## Issues and future improvements
- The data used is limited to data provided on ufcstats.com
- elo system isnt very effective as ufc fights happen far less frequently than other sports
