import pandas as pd
import joblib

from ml_pipeline.data_preprocessing import preprocess_data
from upcoming_fights_scraper import scrape_upcoming_card
from ml_pipeline.data_cleaning import clean_data
from ml_pipeline.feature_engineering import combine_historic_and_upcoming


def join_fighters_fights(upcoming_fights_df):
    fighter_stats_url = 'https://raw.githubusercontent.com/joelkennerley/ufc-stats-scraper/main/data/fighter_stats.csv'
    fighter_df = pd.read_csv(fighter_stats_url)

    f1_features = pd.merge(upcoming_fights_df, fighter_df, how="left", left_on = 'fighter1_id', right_on='id')
    # rename shared attributes with f1_...
    renamed1 = f1_features.rename(columns=lambda x: f'f1_{x}' if x in fighter_df else x)

    # fighter 2s features merged into summary & f1 features df
    f1_f2_features = pd.merge(renamed1, fighter_df, how="left", left_on = 'fighter2_id', right_on='id')
    full_features = f1_f2_features.rename(columns=lambda x: f'f2_{x}' if x in fighter_df else x)
    return full_features

def main():
    df = scrape_upcoming_card()
    df = join_fighters_fights(df)
    df = clean_data(df)
    df = preprocess_data(df)
    df = combine_historic_and_upcoming(df)
    model = joblib.load('../model/ufc_prediction_rf_model.joblib')
    predictions = model.predict(df)
    print(predictions)

if __name__ == "__main__":
    main()