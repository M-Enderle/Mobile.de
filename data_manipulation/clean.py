import pandas as pd
import missingno as msno
import matplotlib.pyplot as plt
import numpy as np


def set_color(_fig, _ax):
    _fig.patch.set_facecolor('#1b212c')
    _ax.patch.set_facecolor('#1b212c')
    _ax.spines['bottom'].set_color('white')
    _ax.spines['top'].set_color('white')
    _ax.spines['left'].set_color('white')
    _ax.spines['right'].set_color('white')
    _ax.xaxis.label.set_color('white')
    _ax.yaxis.label.set_color('white')
    _ax.grid(alpha=0.1)
    _ax.title.set_color('white')
    _ax.tick_params(axis='x', colors='white')
    _ax.tick_params(axis='y', colors='white')


def matrix(_cars):
    global counter
    fig, ax = plt.subplots(figsize=(25, 10), dpi=300)
    set_color(fig, ax)
    msno.matrix(_cars, ax=ax)
    plt.tight_layout()
    plt.savefig(f"../images/matrix/{counter}.png", dpi=300)
    counter += 1


counter = 0

# load dataset
cars = pd.read_csv('../resources/cars.csv', low_memory=False)

# for each row check if 'land rover' is in the title and if so set the manufacturer to 'land rover'
for index, row in cars.iterrows():
    if 'land rover' in row['title'].lower():
        cars.loc[index, 'manufacturer'] = 'land rover'

cars.drop(['features', 'scraped_on', 'parking_assistant', 'origin', 'hu', "environment_class", "doors", "num_seats"],
          axis=1, inplace=True)

matrix(cars)

# fill with 1 where num of owners is nan
cars['num_of_owners'] = cars['num_of_owners'].fillna(1)

# drop the weird row
cars = cars[cars.num_of_owners != "num_of_owners"]

# convert to num
cars = cars.astype({"num_of_owners": "float"})
cars = cars.astype({"num_of_owners": "int"})

# drop all rows where num_of_owners is more than 20
cars = cars[cars['num_of_owners'] <= 20]

cars = cars[cars['airbag'].notnull()]

# set all airbag values to 'front-airbags' where the value is 'front airbags'
cars['airbag'] = cars['airbag'].replace('front airbags', 'front-airbags')
cars['airbag'] = cars['airbag'].replace('driver airbag', 'fahrer-airbag')
cars['airbag'] = cars['airbag'].replace('front and side airbags', 'front- und seiten-airbags')
cars['airbag'] = cars['airbag'].replace('front and side and more airbags', 'front-, seiten- und weitere airbags')

matrix(cars)

cars = cars[cars['climate_control'].notnull()]

cars['climate_control'] = cars['climate_control'].replace('a/c (man.)', 'klimaanlage')
cars['climate_control'] = cars['climate_control'].replace('no climatisation', 'keine klimaanlage oder -automatik')
cars['climate_control'] = cars['climate_control'].replace('automatic air conditioning', 'klimaautomatik')
cars['climate_control'] = cars['climate_control'].replace('automatic climatisation, 2 zones', '2-zonen-klimaautomatik')
cars['climate_control'] = cars['climate_control'].replace('automatic climatisation, 3 zones', '3-zonen-klimaautomatik')

matrix(cars)

cars['color'] = cars['color'].fillna('andere')

for color in ["rot", "lila", "gelb", "blau", "schwarz", "weiß", "grau", "braun", "orange", "pink",
              "violett", "grau", "pink", "violett", "silber", "gold", "beige", "grün"]:
    cars['color'] = cars['color'].apply(lambda x: color if color in x.lower() else x)

color_dict = {"red": "rot", "blue": "blau", "black": "schwarz", "white": "weiß", "grey": "grau", "brown": "braun",
              "orange": "orange", "pink": "pink", "violet": "violett", "silver": "silber", "gold": "gold",
              "beige": "beige", "green": "grün", "weiss": "weiß", "grün": "grün", "yellow": "gelb",
              "purple": "violett",
              "lila": "violett"}

for key in color_dict:
    cars['color'] = cars['color'].apply(lambda x: color_dict[key] if key in x.lower() else x)

# create a dictionary with the key being each unique color and the value being the toal number of cars with that color
color_amt_dict = cars['color'].value_counts().to_dict()
cars['color'] = cars['color'].apply(lambda x: 'andere' if color_amt_dict[x] < 250 else x)

matrix(cars)

cars['condition'] = cars['condition'].replace('damaged, accident-damaged vehicle, not roadworthy',
                                              'beschädigt, unfallfahrzeug, nicht fahrtauglich')
cars['condition'] = cars['condition'].replace('damaged', 'beschädigt')
cars['condition'] = cars['condition'].replace('damaged, accident-damaged vehicle', 'beschädigt, unfallfahrzeug')
cars['condition'] = cars['condition'].replace('damaged, not roadworthy', 'beschädigt, nicht fahrtauglich')
cars['condition'] = cars['condition'].replace('accident-free, not roadworthy', 'unfallfrei, nicht fahrtauglich')
cars['condition'] = cars['condition'].replace('damaged, accident-free, not roadworthy',
                                              'beschädigt, unfallfrei, nicht fahrtauglich')
cars['condition'] = cars['condition'].replace('repaired accident damage', 'reparierter unfallschaden')
cars['condition'] = cars['condition'].replace('repaired accident damage, not roadworthy',
                                              'reparierter unfallschaden, nicht fahrtauglich')
cars['condition'] = cars['condition'].replace('damaged, accident-free', 'beschädigt, unfallfrei')
cars['condition'] = cars['condition'].replace('accident-free', 'unfallfrei')
cars['condition'] = cars['condition'].replace('not roadworthy', 'nicht fahrtauglich')

# set the condition to 'unfallfrei' if the condition is NaN
cars['condition'] = cars['condition'].fillna('unfallfrei')

matrix(cars)

fuels = ["hybrid", "benzin", "diesel", "erdgas", "autogas"]
cars = cars[cars['fuel'].notnull()]

# for each row, check if one of the fuels is contained in the fuel 
# value and replace it with the corresponding fuel. Else keep the value as is
for fuel in fuels:
    cars['fuel'] = cars['fuel'].apply(lambda x: fuel if fuel in str(x).lower() else x)

fuel_dict = {"petrol": "benzin"}
for key in fuel_dict:
    cars['fuel'] = cars['fuel'].apply(lambda x: fuel_dict[key] if key in str(x).lower() else x)

# drop all rows where fuel is not in fuels
cars.loc[~cars["fuel"].isin(fuels), "fuel"] = "andere"

# show all unique values of fuel
print(cars['fuel'].unique())

matrix(cars)

cars = cars[cars['gear'].notnull()]
gear_dict = {"manual gearbox": "schaltgetriebe", "automatic transmission": "automatik"}
for key in gear_dict:
    cars['gear'] = cars['gear'].apply(lambda x: gear_dict[key] if key in str(x).lower() else x)

matrix(cars)

interior_list = ["vollleder", "teilleder", "stoff",
                 "andere", "alcantara", "velours",
                 "cloth"]

interior_dict = {"full leather": "vollleder", "part leather": "teilleder",
                 "other": "andere", "velours": "velours", "velour": "velours",
                 "cloth": "stoff"}

for key in interior_dict:
    cars['interior'] = cars['interior'].apply(lambda x: interior_dict[key] if key in str(x).lower() else x)

for interior in interior_list:
    cars['interior'] = cars['interior'].apply(lambda x: interior if interior in str(x).lower() else x)
# ist die loop das problem? ja

cars.loc[~cars["interior"].isin(interior_list), "interior"] = "andere"
matrix(cars)

cars = cars[cars['co2'].notnull()]
cars = cars[cars['consumption'].notnull()]
cars = cars[cars['cubicCapacity'].notnull()]
cars = cars[cars['emission_class'].notnull()]
cars = cars[cars['first_registration'].notnull()]
cars = cars[cars['gear'].notnull()]
cars = cars[cars['manufacturer'].notnull()]
matrix(cars)

cars['first_registration'] = pd.to_datetime(cars['first_registration'])
cars['first_registration'] = cars['first_registration'].dt.year

for cat in ['cabrio', "roadster", "cabriolet"]:
    cars.loc[cars.category.str.contains(cat), 'cabrio'] = 1
cars.cabrio = cars.cabrio.fillna(0)

for cat in ['kleinwagen', "small car"]:
    cars.loc[cars.category.str.contains(cat), 'kleinwagen'] = 1
cars.kleinwagen = cars.kleinwagen.fillna(0)

for cat in ['kombi', "estate car"]:
    cars.loc[cars.category.str.contains(cat), 'kombi'] = 1
cars.kombi = cars.kombi.fillna(0)

for cat in ["limousine", "saloon"]:
    cars.loc[cars.category.str.contains(cat), 'limousine'] = 1
cars.limousine = cars.limousine.fillna(0)

for cat in ['sportwagen', "coupé", "sports car"]:
    cars.loc[cars.category.str.contains(cat), 'sportwagen'] = 1
cars.sportwagen = cars.sportwagen.fillna(0)

for cat in ['geländewagen', "pickup", "suv", "off-road"]:
    cars.loc[cars.category.str.contains(cat), 'gelaendewagen'] = 1
cars.gelaendewagen = cars.gelaendewagen.fillna(0)

for cat in ['van', "minibus"]:
    cars.loc[cars.category.str.contains(cat), 'van'] = 1
cars.van = cars.van.fillna(0)

cars = cars.drop(columns=['category'])

matrix(cars)

# delete all rows where at least one col is NaN!
cars = cars.dropna()
matrix(cars)

# for each column, print the amount of values possible
for col in cars.columns:
    print(col, len(cars[col].unique()))

cars = cars.astype({"co2": "float64", "consumption": "float64", "cubicCapacity": "float64",
                    "emission_class": "float64", "mileage": "float64", "power": "float64",
                    "price": "float64", "cabrio": "float64", "kleinwagen": "float64",
                    "kombi": "float64", "limousine": "float64", "sportwagen": "float64",
                    "gelaendewagen": "float64", "van": "float64"})

cars = cars.astype({"cabrio": "int", "kleinwagen": "int", "kombi": "int", "limousine": "int",
                    "sportwagen": "int", "gelaendewagen": "int", "van": "int"})
print(cars.dtypes)

# delete all rows where the price is over 1M
cars = cars[cars['price'] < 1000000]

# get all numeric columns
numeric_cols = cars.select_dtypes(include=np.number).columns

for col in numeric_cols:
    if cars[col].nunique() < 5:
        continue
    diff_q = np.quantile(cars[col], [0.005, 0.995])
    diff_q[0] = diff_q[0] - (diff_q[0] * 0.05)
    diff_q[1] = diff_q[1] + (diff_q[1] * 0.05)
    cars = cars[(cars[col] > diff_q[0]) & (cars[col] < diff_q[1])]

cars = cars.drop_duplicates(subset=cars.drop(columns=['url', 'title']).columns)
print(cars.shape)

matrix(cars)

# save the dataset as a csv file
cars.to_csv('../resources/cars_clean.csv', index=False)
