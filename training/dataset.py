import pandas as pd
from sklearn.model_selection import train_test_split
import pickle

cars = pd.read_csv('../resources/cars_clean.csv', low_memory=False)

cars = cars.drop(["url", "title"], axis=1)

corresponding_values = {}

for col in cars.columns:
    if cars[col].dtype == 'object' or col == 'first_registration':
        cars[col] = pd.Categorical(cars[col])
        corresponding_values[col] = {}
        for cat in cars[col].cat.categories:
            corresponding_values[col][cat] = cars[col].cat.codes[cars[col] == cat].values[0]
        cars[col] = cars[col].cat.codes
    elif cars[col].dtype == 'float64':
        cars[col] = cars[col].astype('float32')

for col in ['num_of_owners', 'cabrio', 'kleinwagen',
            'limousine', 'sportwagen', 'gelaendewagen', 'van', 'kombi']:
    if col in cars.columns:
        cars[col] = pd.Categorical(cars[col])
        corresponding_values[col] = {}
        for cat in cars[col].cat.categories:
            corresponding_values[col][cat] = cars[col].cat.codes[cars[col] == cat].values[0]
        cars[col] = cars[col].cat.codes

pickle.dump(corresponding_values, open('../resources/corresponding_values.pkl', 'wb'))

Y = cars['price']
X = cars.drop(['price'], axis=1)

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42069, shuffle=False)


def convert(x):
    cars_categorical = x.select_dtypes(include=['int8', 'int64'])
    cars_numerical = x.select_dtypes(include=['float32'])
    return cars_categorical, cars_numerical
