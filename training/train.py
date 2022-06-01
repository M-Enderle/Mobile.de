from keras.utils.vis_utils import plot_model

from dataset import x_train, x_test, y_train, y_test, convert
from keras import Input, Model
from keras.layers import Reshape, Embedding, Concatenate, Dense, LayerNormalization
import numpy as np
import tensorflow as tf
import keras.backend as K

categorical_train, numeric_train = convert(x_train)

inputs = []
embeddings = []
for c in range(len(categorical_train.columns)):
    input_ = Input(shape=(1,),
                   name='input_' + str(categorical_train.columns[c]).replace("ä", "ae").replace("ö", "oe").replace("ü",
                                                                                                                   "ue").replace(
                       "ß", "ss"))
    no_of_unique_cat = len(categorical_train.iloc[:, c].unique())
    embedding_size = min(np.ceil(no_of_unique_cat / 2), 50)
    embedding_size = int(embedding_size)
    embedding = Embedding(no_of_unique_cat + 1, embedding_size, input_length=1,
                          name='embedding_' + str(categorical_train.columns[c]).replace("ä", "ae").replace("ö",
                                                                                                           "oe").replace(
                              "ü", "ue").replace("ß", "ss"))(input_)
    embedding = Reshape(target_shape=(embedding_size,),
                        name='reshape_' + str(categorical_train.columns[c]).replace("ä", "ae").replace("ö",
                                                                                                       "oe").replace(
                            "ü", "ue").replace("ß", "ss"))(embedding)
    inputs.append(input_)
    embeddings.append(embedding)

cat_concat = Concatenate(name="concat_categorical")(embeddings)
cat_dense = Dense(1024, activation='selu', kernel_initializer='lecun_normal')(cat_concat)

input_numeric = Input(shape=(5,), name='input_continuous')
norm = LayerNormalization(axis=1)(input_numeric)
inputs.append(input_numeric)
numeric_dense = Dense(1024, activation='selu', kernel_initializer='lecun_normal')(norm)

x = Concatenate(name="concat")([numeric_dense, cat_dense])
x = Dense(1024, activation='selu', kernel_initializer='lecun_normal')(x)
x = Dense(512, activation='selu', kernel_initializer='lecun_normal')(x)
x = Dense(1024, activation='selu', kernel_initializer='lecun_normal')(x)
out = Dense(1, activation='relu', name='output')(x)

model = Model(inputs=inputs, outputs=out)

# plot the model
plot_model(model, to_file='model.png', show_shapes=True)

model.compile(optimizer='nadam',
              loss="mean_absolute_percentage_error", metrics=['mean_absolute_percentage_error'])

model.fit([categorical_train[x] for x in categorical_train.columns] + [numeric_train], y_train, epochs=150,
          batch_size=200,
          validation_split=0.14)

from sklearn.metrics import r2_score

categorical_test = x_test.select_dtypes(include=['int8', 'int64'])
numerical_test = x_test.select_dtypes(include=['float32'])

y_predict = model.predict(x=[categorical_test[x] for x in categorical_test.columns] + [numerical_test])

print("R^2: ", r2_score(y_test, y_predict))

from sklearn.metrics import mean_absolute_error

print("MAE: ", mean_absolute_error(y_test, y_predict))

# print mean_absolute_percentage_error
from sklearn.metrics import mean_absolute_percentage_error

