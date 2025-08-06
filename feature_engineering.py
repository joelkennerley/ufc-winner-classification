from collections import defaultdict
import pandas as pd

fighter_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "elo": 1500,
                                     "last_fight": pd.NaT, "history": [0]})


# start at 0 as we will iterate through entire dataset to only capture w/l in ufc
# and to make sure that each entry reps their record at that time not today

# ======== creating fighters record features exclusively in the UFC ===========

def set_record(data, row, index):
    data.at[index, 'f1_wins'] = fighter_stats[row['fighter1_id']]['wins']
    data.at[index, 'f1_losses'] = fighter_stats[row['fighter1_id']]['losses']
    data.at[index, 'f1_wins'] = fighter_stats[row['fighter1_id']]['wins']
    data.at[index, 'f1_elo'] = fighter_stats[row['fighter1_id']]['elo']

    data.at[index, 'f2_wins'] = fighter_stats[row['fighter2_id']]['wins']
    data.at[index, 'f2_losses'] = fighter_stats[row['fighter2_id']]['losses']
    data.at[index, 'f2_wins'] = fighter_stats[row['fighter2_id']]['wins']
    data.at[index, 'f2_elo'] = fighter_stats[row['fighter2_id']]['elo']
    return data

def fighter1_wins(row):
    # update record in dictionary
    fighter_stats[row['fighter1_id']]['wins'] += 1
    fighter_stats[row['fighter2_id']]['losses'] += 1
    # update elo in dictionary
    winner_elo = fighter_stats[row['fighter1_id']]['elo']
    loser_elo = fighter_stats[row['fighter2_id']]['elo']
    new_winner_elo, new_loser_elo = update_elo(winner_elo, loser_elo)
    fighter_stats[row['fighter1_id']]['elo'] = new_winner_elo
    fighter_stats[row['fighter2_id']]['elo'] = new_loser_elo


def fighter2_wins(row):
    # update record in dictionary
    fighter_stats[row['fighter2_id']]['wins'] += 1
    fighter_stats[row['fighter1_id']]['losses'] += 1
    # update elo in dictionary
    winner_elo = fighter_stats[row['fighter2_id']]['elo']
    loser_elo = fighter_stats[row['fighter1_id']]['elo']
    new_winner_elo, new_loser_elo = update_elo(winner_elo, loser_elo)
    fighter_stats[row['fighter2_id']]['elo'] = new_winner_elo
    fighter_stats[row['fighter1_id']]['elo'] = new_loser_elo

# =================================================================

# ========== fighter elo calculations =============================

def expected_score(rating_a, rating_b):
    # expected score of player a
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 200))

def update_elo(winner_rating, loser_rating, k=4):
    expected_win = expected_score(winner_rating, loser_rating)
    new_winner_rating = winner_rating + k * (1 - expected_win)
    new_loser_rating = loser_rating + k * (0 - (1 - expected_win))
    return new_winner_rating, new_loser_rating

# ===================================================================

# =========== creating new features =================================

def add_difference_columns(data):
    # create new feature which captures the diff from f1 to f2
    columns = ['reach', 'age', 'height', 'SLpM', 'str_acc', 'SApM', 'str_def', 'td_avg',
                 'td_acc', 'td_def', 'sub_avg', 'wins', 'elo', 'total_fights']
    for col in columns:
        data[f'{col}_diff'] = round(data[f'f1_{col}'] - data[f'f2_{col}'],3)
    return data

def days_since_last_fight(data):
    # days since last fight
    data = data.sort_values(by='date')  # iterate through df from earliest fight
    for index, row in data.iterrows():
        nums = [1,2]
        # add last
        for num in nums:
            last_fight = fighter_stats[row[f'fighter{num}_id']]['last_fight']
            days_since = (pd.to_datetime(data.at[index, 'date']) - pd.to_datetime(last_fight)).days
            data.at[index, f'f{num}_last_fight'] = days_since
            fighter_stats[row[f'fighter{num}_id']]['last_fight'] = data.at[index, 'date']
    return data

def last_fights_result(data):
    data = data.sort_values(by='date')  # iterate through df from earliest fight
    for index, row in data.iterrows():
        nums = [1,2]
        for num in nums:
            # result history is a list of all previous fights as wins and losses
            # sum up last 3 items in list to get amount won in last 3
            data.at[index, f'f{num}_last_3'] = sum(fighter_stats[row[f'fighter{num}_id']]['history'][-5:])

        if data.at[index, 'result'] == 1:
            fighter_stats[row[f'fighter1_id']]['history'].append(1)
            fighter_stats[row[f'fighter2_id']]['history'].append(0)
        else:
            fighter_stats[row[f'fighter2_id']]['history'].append(1)
            fighter_stats[row[f'fighter1_id']]['history'].append(0)
    return data

def win_percent(data):
    data = data.sort_values(by='date')  # iterate through df from earliest fight
    for index, row in data.iterrows():
        for num in [1,2]:
            wins = data.at[index, f'f{num}_wins']
            losses = data.at[index, f'f{num}_losses']
            data.at[index, f'f{num}_win_pct'] = wins/(wins + losses)
    return data

def experience(data):
    data = data.sort_values(by='date')  # iterate through df from earliest fight
    for index, row in data.iterrows():
        for num in [1, 2]:
            wins = data.at[index, f'f{num}_wins']
            losses = data.at[index, f'f{num}_losses']
            data.at[index, f'f{num}_total_fights'] = wins + losses
    return data

# =====================================================================

# ============== main functions =======================================

def engineer_features(data):
    data = add_difference_columns(data)
    data = days_since_last_fight(data)
    return data

def calculate_record(data):
    data = data.sort_values(by='date') # iterate through df from earliest fight
    for index, row in data.iterrows():
        # sets each df entry to value in dictionary fighter_stats
        data = set_record(data, row, index)
        # updates fighter_stats dict (w/l and elo) depending on result
        if data.at[index, 'result'] == 1:
            fighter1_wins(row)
        elif data.at[index,'result'] == data.at[index,'fighter2']:
            fighter2_wins(row)
    return data

def main():
    data = pd.read_csv('preprocessed_data.csv')
    data = calculate_record(data)
    data = days_since_last_fight(data)
    data = last_fights_result(data)
    data = win_percent(data)
    data = experience(data)
    data = add_difference_columns(data)
    print(data.columns)
    data.to_csv('test_features.csv', index = False)

if __name__ == '__main__':
    main()