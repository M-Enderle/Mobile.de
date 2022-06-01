import pandas as pd
from sklearn.metrics.pairwise import pairwise_distances
import requests

cars = pd.read_csv('cars_clean.csv')

min_max = dict()

for key in ["first_registration", "power", "cubicCapacity", "consumption", "co2"]:
    min_ = cars[key].quantile(0.01)
    max_ = cars[key].quantile(0.99)
    cars[key+"_norm"] = (cars[key] - min_) / (max_ - min_)
    min_max[key] = (min_, max_)


def get_img(url):
    html = requests.get(url, headers={b'Accept': b'text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8',
                                      b'Accept-Language': b'en',
                                      b'User-Agent': b'Scrapy/2.6.1 (+https://scrapy.org/)',
                                      b'Accept-Encoding': b'gzip, deflate'}).text

    if html.find("cycle-slide") != -1:
        img_url = html.split("cycle-slide")[1].split("src=\"")[1].split("\"")[0]
    elif html.find("gallery-img-0") != -1:
        img_url = html.split("gallery-img-0")[1].split("img src=\"")[1].split("\"")[0]
    elif html.find("vip-error__details__image") != -1:
        img_url = html.split("vip-error__details__image")[1].split("src=\"")[1].split("\"")[0]
        img_url_html = requests.get(img_url).text
        if img_url_html.find('"code":404') != -1:
            img_url = None
    else:
        img_url = None

    return img_url


def get_closest(car) -> [list, None]:

    if "model" not in car:
        return None

    cars_filtered = cars[cars['title'].str.contains(car['model'].lower())]
    for col in ["manufacturer", "fuel", "climate_control", "gear", "airbag", "environment_class", "emission_class",
                "doors", "num_seats"]:
        if col in car and car[col]:
            cars_filtered = cars_filtered[cars_filtered[col] == car[col]]

    if len(cars_filtered) == 0:
        return None

    to_rank = []
    for col in ["first_registration", "power", "cubicCapacity", "consumption", "co2"]:
        if col in car and car[col]:
            car[col+"_norm"] = (float(car[col]) - min_max[col][0]) / (min_max[col][1] - min_max[col][0])
            to_rank.append(col+"_norm")

    if len(to_rank) == 0:
        return None

    cars_filtered["distance"] = pairwise_distances(cars_filtered[to_rank],
                                                   [[car[key] for key in to_rank]],
                                                   metric="euclidean")

    cars_filtered = cars_filtered[cars_filtered["distance"] < 0.02]

    cars_filtered = cars_filtered.sort_values(by="distance")

    if len(cars_filtered) > 0:

        results = cars_filtered.iloc[:5].to_dict(orient="records")
        for result in results:
            result["img_url"] = get_img(result["url"])

        return results
    return None
