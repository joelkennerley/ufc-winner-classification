import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import joblib

# data = pd.read_csv('preprocessed_data.csv').iloc[-5500:]
# data = data.drop(['f1_elo', 'f2_elo'], axis=1)

data = pd.read_csv('../data/model_ready_data.csv')
print(data.head())



print(data.columns)

X = data.drop('result', axis=1)
Y = data['result']

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

rf = RandomForestClassifier()
rf.fit(X_train, Y_train)

y_pred = rf.predict(X_test)

accuracy = accuracy_score(Y_test, y_pred)
print("Accuracy:", accuracy)

scores = cross_val_score(rf, X, Y, cv=5)
print("CV Accuracy:", scores.mean())

joblib.dump(rf, '../model/ufc_prediction_rf_model.joblib')

importances = rf.feature_importances_
feature_names = X_train.columns

# Create DataFrame
feat_imp = pd.DataFrame({
    'feature': feature_names,
    'importance': importances
}).sort_values(by='importance', ascending=False)

print(feat_imp)




