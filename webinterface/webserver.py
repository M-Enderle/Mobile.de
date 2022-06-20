import json
import os
import pickle
from flask import Flask, render_template, request
import pandas as pd
from tensorflow import keras
from get_closest import get_closest

cars = pd.read_csv('../resources/cars_clean.csv', low_memory=False)
app = Flask(__name__, template_folder='templates')

colors_translated = {'andere': 'other', 'beige': 'beige', 'blau': 'blue', 'braun': '#a5462a', 'gelb': 'yellow',
                     'gold': 'gold', 'grau': 'grey', 'grün': 'green', 'orange': 'orange', 'rot': 'Red',
                     'schwarz': 'black', 'silber': 'silver', 'violett': 'violet', 'weiß': 'white'}

corresponding_value = pickle.load(open('../resources/corresponding_values.pkl', 'rb'))

model = keras.models.load_model('../resources/model.keras')


def convert_to_corresponding_value(input_row):
    for key, value in input_row.items():
        if key in corresponding_value.keys():
            input_row[key] = corresponding_value[key][value]

    return input_row


@app.route('/')
def index():
    return render_template('search.html',
                           manufacturers=[x.title() for x in cars.sort_values("manufacturer")["manufacturer"].unique()],
                           car_types=[x.replace(".svg", "") for x in os.listdir('static/images/cars')],
                           num_of_owners=cars.sort_values("num_of_owners")["num_of_owners"].unique(),
                           conditions=cars["condition"].unique(),
                           first_registration=cars.sort_values("first_registration")["first_registration"].unique(),
                           fuel=cars.sort_values("fuel")["fuel"].unique(),
                           gear=cars.sort_values("gear")["gear"].unique(),
                           emission_class=cars.sort_values("emission_class")["emission_class"].unique(),
                           airbag=cars.sort_values("airbag")["airbag"].unique(),
                           climate_control=cars.sort_values("climate_control")["climate_control"].unique(),
                           interior=cars.sort_values("interior")["interior"].unique(),
                           colors=[{"ger": x, "eng": colors_translated[x]} for x in
                                   cars.sort_values("color")["color"].unique() if x != "andere"])


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    car_types = {"cabrio": 0.0, "kleinwagen": 0.0, "kombi": 0.0, "limousine": 0.0, "sportwagen": 0.0, "gelaendewagen": 0.0, "van": 0.0}

    for car_type in car_types.keys():
        if car_type in data["car_types"]:
            car_types[car_type] = 1.0

    car = {
        "manufacturer": data['manufacturer'],
        "airbag": data['airbag'],
        "climate_control": data['climate_control'],
        "first_registration": int(data['first_registration']),
        "fuel": data['fuel'],
        "color": data['color'],
        "condition": data['condition'],
        "gear": data['gear'],
        "interior": data['interior'],
        "mileage": data['mileage'],
        "num_of_owners": float(data['num_of_owners']),
        "power": data['power'],
        "cabrio": car_types['cabrio'],
        "kleinwagen": car_types['kleinwagen'],
        "kombi": car_types['kombi'],
        "limousine": car_types['limousine'],
        "sportwagen": car_types['sportwagen'],
        "gelaendewagen": car_types['gelaendewagen'],
        "van": car_types['van'],
        "co2": data['co2'],
        "consumption": data['consumption'],
        "cubicCapacity": data['cubicCapacity'],
        "emission_class": float(data['emission_class']),
    }

    convert_to_corresponding_value(car)
    in_order = [car[x] for x in cars.columns if x not in ["price", "title", "url"]]
    df = pd.DataFrame(data=None, columns=[x for x in cars.columns if x not in ["price", "title", "url"]])
    df.loc[0] = in_order
    for col in ["airbag", "climate_control", "color", "condition", "emission_class",
                "first_registration", "fuel", "gear", "interior", "manufacturer", "num_of_owners",
                "cabrio", "kleinwagen", "kombi", "limousine", "sportwagen", "gelaendewagen", "van"]:
        df[col] = df[col].astype('int8')
    for col in ['co2', 'consumption', 'cubicCapacity', 'mileage', 'power']:
        df[col] = df[col].astype('float32')

    cars_categorial = df.select_dtypes(include=['int8'])
    cars_numerical = df.select_dtypes(include=['float32'])
    prediction = model.predict(x=[cars_categorial[x] for x in cars_categorial.columns] + [cars_numerical])
    return json.dumps({"status": "ok", "price": prediction[0][0]}, indent=4, sort_keys=True, default=str)


@app.route('/closest', methods=['POST'])
def get_closest_car():
    data = request.get_json()
    result = get_closest(data)
    if request:
        return json.dumps({"status": "ok", "data": result}, indent=4, sort_keys=True, default=str)
    return json.dumps({"status": "error"}, indent=4, sort_keys=True, default=str)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
