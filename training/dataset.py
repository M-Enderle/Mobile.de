import pandas as pd
from sklearn.model_selection import train_test_split

cars = pd.read_csv('cars_clean.csv', low_memory=False)
cars = cars.iloc[:50000, :]

# select only consumption, condition, cubicCapacity, mileage, manufacturer, first_registration


corresponding_value = dict()

for col in cars.columns:
    if cars[col].dtype == 'object' or col == 'first_registration':
        cars[col] = pd.Categorical(cars[col])
        cars[col] = cars[col].cat.codes
    elif cars[col].dtype == 'float64':
        cars[col] = cars[col].astype('float32')

for col in ['doors', 'emission_class', 'environment_class', 'num_of_owners', 'num_seats', 'cabrio', 'kleinwagen',
            'limousine', 'sportwagen', 'geländewagen', 'van', 'kombi']:
    if col in cars.columns:
        cars[col] = pd.Categorical(cars[col])
        cars[col] = cars[col].cat.codes

Y = cars['price']
X = cars.drop(['price'], axis=1)

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42069, shuffle=False)


def convert(x):
    cars_categorical = x.select_dtypes(include=['int8', 'int64'])
    cars_numerical = x.select_dtypes(include=['float32'])
    return cars_categorical, cars_numerical
