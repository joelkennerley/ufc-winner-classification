import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

def encode_winner(data):
    # winner = fighter1 when result is 1
    data['result'] = np.where(data['result'] == data['fighter1'], 1, 0)
    return data

def encode_title_fights(data):
    # encode title fights as 1 and non title as 0
    data['title_fight'] = data['bout'].str.lower().str.contains('title').astype(int)
    return data

def encode_gender(data):
    # womens fight encoded as 1
    data['female'] = data['bout'].str.lower().str.contains("women's").astype(int)
    return data

def handle_na(data):
    # change nan to 'unkown'
    data['f1_stance'] = data['f1_stance'].fillna('Unknown')
    data['f2_stance'] = data['f2_stance'].fillna('Unknown')
    return data

def drop_non_pred(data):
    # drop non predictive columns
    data = data.drop(['fighter1_id', 'fighter2_id', 'fight_id', 'fighter1', 'fighter2', 'round', 'format', 'bout'], axis=1)
    return data

def stance_ohe(data):
    # encode stance of fighters using one hot encoding
    ohe = OneHotEncoder(handle_unknown='ignore', sparse_output=False).set_output(transform='pandas')
    ohe_transform1 = ohe.fit_transform(data[['f1_stance']])
    ohe_transform2 = ohe.fit_transform(data[['f2_stance']])
    data = pd.concat([data, ohe_transform1, ohe_transform2], axis=1).drop(['f1_stance', 'f2_stance'], axis=1)
    return data

def main():
    data = pd.read_csv('cleaned_data.csv')
    data = encode_winner(data)
    data = encode_title_fights(data)
    data = encode_gender(data)
    data = handle_na(data)
    data = drop_non_pred(data)
    data = stance_ohe(data)

    data.to_csv('preprocessed_data.csv', index=False)


if __name__ == "__main__":
    main()
