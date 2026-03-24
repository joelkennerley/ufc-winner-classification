import pandas as pd
import joblib
import numpy as np
from ml_pipeline.data_preprocessing_2 import preprocess_data
from upcoming_fights_scraper import scrape_upcoming_card
from ml_pipeline.data_cleaning_1 import clean_data
from ml_pipeline.feature_engineering_3 import combine_historic_and_upcoming


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
    raw_upcoming_fights = scrape_upcoming_card()
    df = join_fighters_fights(raw_upcoming_fights)
    print('cleaning data ...')
    df = clean_data(df)
    print('preprocessing ...')
    df = preprocess_data(df)
    fight_date = df['date'].iloc[0]
    print('engineering_features ...')
    df = combine_historic_and_upcoming(df, fight_date)
    print('predicting winners ...')
    model = joblib.load('../model/ufc_prediction_rf_model.joblib')
    predictions = model.predict(df)
    final_predictions_df = raw_upcoming_fights.copy()
    final_predictions_df['predictions'] = np.where(predictions == 1, final_predictions_df['fighter1'], final_predictions_df['fighter2'])
    final_predictions_df = final_predictions_df.drop(['fighter1_id','fighter2_id'],axis=1,errors='ignore')

    return final_predictions_df

if __name__ == "__main__":
    main()