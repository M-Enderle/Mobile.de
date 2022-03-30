from keras.engine.input_layer import InputLayer
from sklearn.metrics import r2_score
from keras.models import Sequential
from keras.layers import Dense
import pandas as pd
from tqdm import tqdm

cars = pd.read_csv('cars_clean.csv', low_memory=False)

for col in tqdm(cars.columns):
    if cars[col].dtype == 'object':
        cars[col] = pd.Categorical(cars[col])
        cars[col] = cars[col].cat.codes

for col in ['doors', 'emission_class', 'environment_class', 'num_of_owners', 'num_seats', 'cabrio', 'kleinwagen',
            'limousine', 'sportwagen','geländewagen','van', 'kombi']:
    cars[col] = cars[col].astype('int8')

# create test and train data
from sklearn.model_selection import train_test_split

# shuffle the cars dataset
cars = cars.sample(frac=1)

cars = cars[:1000]

# split the data into train and test
train, test = train_test_split(cars, test_size=0.2)

# create train x which is train without price column
train_x = train.drop(['price'], axis=1)
train_y = train['price']

# create the test like before
test_x = test.drop(['price'], axis=1)
test_y = test['price']


combinations_2 = [(19, 1), (18, 2), (17, 3), (16, 4), (15, 5), (14, 6), (13, 7), (12, 8), (11, 9), (10, 10)]

combinations_3 = [(18, 1, 1), (17, 2, 1), (16, 3, 1), (16, 2, 2), (15, 4, 1),
                (15, 3, 2), (14, 5, 1), (14, 4, 2), (14, 3, 3), (13, 6, 1),
                (13, 5, 2), (13, 4, 3), (12, 7, 1), (12, 6, 2), (12, 5, 3),
                (12, 4, 4), (11, 8, 1), (11, 7, 2), (11, 6, 3), (11, 5, 4),
                (10, 9, 1), (10, 8, 2), (10, 7, 3), (10, 6, 4), (10, 5, 5),
                (9, 9, 2), (9, 8, 3), (9, 7, 4), (9, 6, 5), (8, 8, 4),
                (8, 7, 5), (8, 6, 6), (7, 7, 6)]

combinations_4 = [(17, 1, 1, 1), (16, 2, 1, 1), (15, 3, 1, 1), (15, 2, 2, 1),
                  (14, 4, 1, 1), (14, 3, 2, 1), (14, 2, 2, 2), (13, 5, 1, 1),
                  (13, 4, 2, 1), (13, 3, 3, 1), (13, 3, 2, 2), (12, 6, 1, 1),
                  (12, 5, 2, 1), (12, 4, 3, 1), (12, 4, 2, 2), (12, 3, 3, 2),
                  (11, 7, 1, 1), (11, 6, 2, 1), (11, 5, 3, 1), (11, 5, 2, 2),
                  (11, 4, 4, 1), (11, 4, 3, 2), (11, 3, 3, 3), (10, 8, 1, 1),
                  (10, 7, 2, 1), (10, 6, 3, 1), (10, 6, 2, 2), (10, 5, 4, 1),
                  (10, 5, 3, 2), (10, 4, 4, 2), (10, 4, 3, 3), (9, 9, 1, 1),
                  (9, 8, 2, 1), (9, 7, 3, 1), (9, 7, 2, 2), (9, 6, 4, 1),
                  (9, 6, 3, 2), (9, 5, 5, 1), (9, 5, 4, 2), (9, 5, 3, 3),
                  (9, 4, 4, 3), (8, 8, 3, 1), (8, 8, 2, 2), (8, 7, 4, 1),
                  (8, 7, 3, 2), (8, 6, 5, 1), (8, 6, 4, 2), (8, 6, 3, 3),
                  (8, 5, 5, 2), (8, 5, 4, 3), (8, 4, 4, 4), (7, 7, 5, 1),
                  (7, 7, 4, 2), (7, 7, 3, 3), (7, 6, 6, 1), (7, 6, 5, 2),
                  (7, 6, 4, 3), (7, 5, 5, 3), (7, 5, 4, 4), (6, 6, 6, 2),
                  (6, 6, 5, 3), (6, 6, 4, 4), (6, 5, 5, 4), (5, 5, 5, 5)]


scores = [[], [], []]

for a, b in combinations_2:
    model_2 = Sequential()
    model_2.add(InputLayer(input_shape=train_x.shape[1]))
    model_2.add(Dense(units=a, activation='selu', kernel_initializer='lecun_normal'))
    model_2.add(Dense(units=b, activation='selu', kernel_initializer='lecun_normal'))
    model_2.add(Dense(1, activation='selu', kernel_initializer='lecun_normal'))
    model_2.compile(optimizer='adam', loss='mean_absolute_error')
    model_2.fit(train_x, train_y, batch_size=30, epochs=100, verbose=2, validation_data=(test_x, test_y))
    scores[0].append(r2_score(test_y,model_2.predict(x=test_x)))

for a, b, c in combinations_3:
    model_3 = Sequential()
    model_3.add(InputLayer(input_shape=train_x.shape[1]))
    model_3.add(Dense(units=a, activation='selu', kernel_initializer='lecun_normal'))
    model_3.add(Dense(units=b, activation='selu', kernel_initializer='lecun_normal'))
    model_3.add(Dense(units=c, activation='selu', kernel_initializer='lecun_normal'))
    model_3.add(Dense(1, activation='selu', kernel_initializer='lecun_normal'))
    model_3.compile(optimizer='adam', loss='mean_absolute_error')
    model_3.fit(train_x, train_y, batch_size=30, epochs=100, verbose=2, validation_data=(test_x, test_y))
    scores[1].append(r2_score(test_y, model_3.predict(x=test_x)))

for a, b, c, d in combinations_4:
    model_4 = Sequential()
    model_4.add(InputLayer(input_shape=train_x.shape[1]))
    model_4.add(Dense(units=a, activation='selu', kernel_initializer='lecun_normal'))
    model_4.add(Dense(units=b, activation='selu', kernel_initializer='lecun_normal'))
    model_4.add(Dense(units=c, activation='selu', kernel_initializer='lecun_normal'))
    model_4.add(Dense(units=d, activation='selu', kernel_initializer='lecun_normal'))
    model_4.compile(optimizer='adam', loss='mean_absolute_error')
    model_4.fit(train_x, train_y, batch_size=30, epochs=100, verbose=2, validation_data=(test_x, test_y))
    scores[2].append(r2_score(test_y, model_4.predict(x=test_x)))

with open("scores.txt", "a") as file:
    file.write("2 nodes:\n")
    file.write(", ".join(scores[0]) + "\n")
    file.write("3 nodes:\n")
    file.write(", ".join(scores[1]) + "\n")
    file.write("4 nodes:\n")
    file.write(", ".join(scores[2]) + "\n")
