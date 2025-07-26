from collections import defaultdict
import pandas as pd

# start at 0 as we will iterate through entire dataset to only capture w/l in ufc
# and to make sure that each entry reps their record at that time not today
fighter_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "draws": 0, "elo": 1500})

# Note that wins/losses are now only wins/losses gained in ufc promotion

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

def draw(row):
    fighter_stats[row['fighter1_id']]['draws'] += 1
    fighter_stats[row['fighter2_id']]['draws'] += 1

def expected_score(rating_a, rating_b):
    # expected score of player a
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(winner_rating, loser_rating, k=32):
    expected_win = expected_score(winner_rating, loser_rating)
    new_winner_rating = winner_rating + k * (1 - expected_win)
    new_loser_rating = loser_rating + k * (0 - (1 - expected_win))
    return new_winner_rating, new_loser_rating

def main():
    data = pd.read_csv('cleaned_data.csv')
    data = data.sort_values(by='date') # iterate through df from earliest fight

    for index, row in data.iterrows():
        # sets each df entry to value in dictionary fighter_stats
        data = set_record(data, row, index)
        # updates fighter_stats dict (w/l/d and elo) depending on result
        if data.at[index, 'result'] == data.at[index, 'fighter1']:
            fighter1_wins(row)
        elif data.at[index,'result'] == data.at[index,'fighter2']:
            fighter2_wins(row)
        else:
            draw(row)

    data.to_csv('updated_records_elo.csv', index=False)

if __name__ == '__main__':
    main()