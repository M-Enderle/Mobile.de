import pandas as pd
from sklearn.model_selection import train_test_split

_cars = pd.read_csv('../resources/cars_clean.csv', low_memory=False)

_cars = _cars.drop(['title', 'url'], axis=1)
unique_values = {}


def create_dummies(_cars):
    _columns = ['airbag', 'climate_control', 'color', 'condition',
                'emission_class', 'fuel', 'gear', 'interior', 'manufacturer']

    for _col in _columns:
        unique_values[_col] = _cars[_col].unique()

    for _col in _cars.columns:
        if _cars[_col].dtype == 'object' or _col == 'first_registration':
            _cars[_col] = pd.Categorical(_cars[_col])
            _cars[_col] = _cars[_col].cat.codes
        elif _cars[_col].dtype == 'float64':
            _cars[_col] = _cars[_col].astype('float32')

    for _col in ['emission_class', 'num_of_owners', 'cabrio', 'kleinwagen',
                 'limousine', 'sportwagen', 'geländewagen', 'van', 'kombi']:
        if _col in _cars.columns:
            _cars[_col] = pd.Categorical(_cars[_col])
            _cars[_col] = _cars[_col].cat.codes

    return _columns


columns = create_dummies(_cars)

Y = _cars['price']
X = _cars.drop(['price'], axis=1)

X = pd.get_dummies(X, columns=columns, prefix_sep="-")

for col in X.columns:
    c = str(col).split("-")
    if c[0] in unique_values:
        if c[0] in ["emission_class"]:
            X.rename(columns={col: c[0] + "_" + str(unique_values[c[0]][int(c[1])])}, inplace=True)
        else:
            X.rename(columns={col: str(unique_values[c[0]][int(c[1])])}, inplace=True)

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=42069, shuffle=False)


def convert(x):
    cars_categorical = x.select_dtypes(include=['int8', 'int64'])
    cars_numerical = x.select_dtypes(include=['float32'])
    return cars_categorical, cars_numerical
