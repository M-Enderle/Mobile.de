import json
import os
import pickle
from flask import Flask, render_template, request, jsonify
import pandas as pd
from tensorflow import keras
from get_closest import get_closest

cars = pd.read_csv('cars_clean.csv', low_memory=False)
app = Flask(__name__, template_folder='templates')
colors_translated = {'andere': 'other', 'beige': 'beige', 'blau': 'blue', 'braun': '#a5462a', 'gelb': 'yellow',
                     'gold': 'gold', 'grau': 'grey', 'grün': 'green', 'orange': 'orange', 'rot': 'Red',
                     'schwarz': 'black', 'silber': 'silver', 'violett': 'violet', 'weiß': 'white'}
corresponding_value = pickle.load(open('corresponding_value.pickel', 'rb'))
model = keras.models.load_model('sick_model_test.keras')

"""
with open(sick_model_json.json) as f:
    model_json = f.read()
model = model_from_json(model_json)
model.load_weights("sick_model_weights.h5")
"""


def convert_to_corresponding_value(input_row):
    inverse_dict = dict()
    for key, value in corresponding_value.items():
        inverse_dict[key] = {v: k for k, v in value.items()}

    for key, value in input_row.items():
        if key in inverse_dict.keys():
            input_row[key] = inverse_dict[key][value]

    return input_row


@app.route('/')
def index():
    return render_template('search.html',
                           manufacturers=[x.title() for x in cars.sort_values("manufacturer")["manufacturer"].unique()],
                           car_types=[x.replace(".svg", "") for x in os.listdir('static/images/cars')],
                           num_seats=cars.sort_values("num_seats")["num_seats"].unique(),
                           doors=cars.sort_values("doors")["doors"].unique(),
                           num_of_owners=cars.sort_values("num_of_owners")["num_of_owners"].unique(),
                           conditions=cars["condition"].unique(),
                           first_registration=cars.sort_values("first_registration")["first_registration"].unique(),
                           hu=[x for x in cars.sort_values("hu")["hu"].unique() if x != "unknown"],
                           fuel=cars.sort_values("fuel")["fuel"].unique(),
                           gear=cars.sort_values("gear")["gear"].unique(),
                           emission_class=cars.sort_values("emission_class")["emission_class"].unique(),
                           environment_class=cars.sort_values("environment_class")["environment_class"].unique(),
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
        "hu": str(float(data['hu'])) if data['hu'] != "unknown" else "unknown",
        "interior": data['interior'],
        "mileage": data['mileage'],
        "num_of_owners": float(data['num_of_owners']),
        "num_seats": float(data['num_seats']),
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
        "doors": float(data['doors']),
        "emission_class": float(data['emission_class']),
        "environment_class": float(data['environment_class']),
    }

    convert_to_corresponding_value(car)
    in_order = [car[x] for x in cars.columns if x not in ["price", "title", "url"]]
    df = pd.DataFrame(data=None, columns=[x for x in cars.columns if x not in ["price", "title", "url"]])
    df.loc[0] = in_order
    for col in ["airbag", "climate_control", "color", "condition", "doors", "emission_class", "environment_class",
                "first_registration", "fuel", "gear", "hu", "interior", "manufacturer", "num_of_owners", "num_seats",
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
    # hshsshssadasdsdasd
    data = request.get_json()
    result = get_closest(data)
    if request:
        return json.dumps({"status": "ok", "data": result}, indent=4, sort_keys=True, default=str)
    return json.dumps({"status": "error"}, indent=4, sort_keys=True, default=str)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
