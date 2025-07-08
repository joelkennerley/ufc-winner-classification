import pandas as pd

fight_summary = pd.read_csv('fight_summaries.csv')
fighter_df = pd.read_csv('fighter_stats.csv')

# fighter 1s features merged into summary df
f1_features = pd.merge(fight_summary, fighter_df, how="left", left_on = 'fighter1_id', right_on='id')
# rename shared attributes with f1_...
renamed1 = f1_features.rename(columns=lambda x: f'f1_{x}' if x in fighter_df else x)

# fighter 2s features merged into summary & f1 features df
f1_f2_features = pd.merge(renamed1, fighter_df, how="left", left_on = 'fighter2_id', right_on='id')
full_features = f1_f2_features.rename(columns=lambda x: f'f2_{x}' if x in fighter_df else x)

full_features.to_csv('raw_features.csv', index=False)
