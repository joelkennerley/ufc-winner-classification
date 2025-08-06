import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

# data = pd.read_csv('preprocessed_data.csv').iloc[-5500:]
# data = data.drop(['f1_elo', 'f2_elo'], axis=1)

data = pd.read_csv('test_features.csv')
print(data.head())

# testing model by dropping different features
data = data.drop(['fight_id', 'bout', 'round', 'format', 'date', 'f2_stance_Sideways', 'female', 'title_fight', 'wins_diff', 'total_fights_diff'], axis=1)
cols = [1,2]
for col in cols:
    data = data.drop([f'fighter{col}_id', f'fighter{col}', f'f{col}_id', f'f{col}_draws', f'f{col}_no_contests', f'f{col}_elo',
                      f'f{col}_stance_Open Stance', f'f{col}_stance_Orthodox', f'f{col}_stance_Southpaw',
                      f'f{col}_stance_Switch', f'f{col}_stance_Unknown', f'f{col}_SLpM', f'f{col}_SApM', f'f{col}_str_acc',
                      f'f{col}_height', f'f{col}_reach', f'f{col}_last_3', f'f{col}_wins', f'f{col}_losses', f'f{col}_sub_avg', f'f{col}_weight',
                      f'f{col}_total_fights', f'f{col}_str_def'], axis=1)

print(data.columns)

X = data.drop('result', axis=1)
Y = data['result']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

rf = RandomForestClassifier()
rf.fit(X_train, Y_train)

y_pred = rf.predict(X_test)

accuracy = accuracy_score(Y_test, y_pred)
print("Accuracy:", accuracy)

model = RandomForestClassifier()
scores = cross_val_score(model, X, Y, cv=5)
print("CV Accuracy:", scores.mean())

importances = rf.feature_importances_
feature_names = X_train.columns

# Create DataFrame
feat_imp = pd.DataFrame({
    'feature': feature_names,
    'importance': importances
}).sort_values(by='importance', ascending=False)

print(feat_imp)




