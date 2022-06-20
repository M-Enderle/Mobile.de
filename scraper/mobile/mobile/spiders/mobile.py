import re
import unicodedata
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy import Item, Field
from datetime import date

cars = ["Abarth", "Alfa Romeo", "Aston Martin", "Audi", "Bentley", "BMW", "Bugatti", "Cadillac", "Chevrolet",
        "Chrysler", "Citroën", "Dacia", "Daewoo", "Daihatsu", "Dodge", "Donkervoort", "DS", "Ferrari", "Fiat", "Fisker",
        "Ford", "Honda", "Hummer", "Hyundai", "Infiniti", "Iveco", "Jaguar", "Jeep", "Kia", "KTM", "Lada",
        "Lamborghini", "Lancia", "Land Rover", "Landwind", "Lexus", "Lotus", "Maserati", "Maybach", "Mazda", "McLaren",
        "Mercedes-Benz", "MG", "Mini", "Mitsubishi", "Morgan", "Nissan", "Opel", "Peugeot", "Porsche", "Renault",
        "Rolls-Royce", "Rover", "Saab", "Seat", "Skoda", "Smart", "SsangYong", "Subaru", "Suzuki", "Tesla", "Toyota",
        "Volkswagen", "Volvo"]


class Car(Item):
    title = Field()
    price = Field()
    manufacturer = Field()
    category = Field()
    origin = Field()
    mileage = Field()
    cubicCapacity = Field()
    power = Field()
    fuel = Field()
    consumption = Field()
    co2 = Field()
    num_seats = Field()
    doors = Field()
    gear = Field()
    emissions = Field()
    environment = Field()
    first_registration = Field()
    num_of_owners = Field()
    hu = Field()
    climate_control = Field()
    parking_assistant = Field()
    airbag = Field()
    color = Field()
    interior = Field()
    scraped_on = Field()
    condition = Field()
    features = Field()
    url = Field()


class MobileSpider(CrawlSpider):
    name = 'mobile'
    allowed_domains = ['mobile.de']
    start_urls = ['https://suchen.mobile.de/fahrzeuge/details.html?id=342337642&damageUnrepaired=NO_DAMAGE_UNREPAIRED'
                  '&isSearchRequest=true&makeModelVariant1.makeId=17200&pageNumber=1&ref=quickSearch&scopeId=C'
                  '&sortOption.sortBy=creationTime&sortOption.sortOrder=DESCENDING&searchId=617845af-2226-ed2f-98e2'
                  '-841ddd9bc1aa']
    base_url = 'https://www.mobile.de/'

    rules = [Rule(LinkExtractor(), callback='parse_car', follow=False)]

    def parse_car(self, response):

        def get(css: str, to_remove: list = None, is_float: bool = False):
            value = response.css(css).get()
            if not value:
                return None
            value = unicodedata.normalize("NFKD", value).strip().lower()
            if to_remove:
                for string in to_remove:
                    value = value.replace(string, "")
            if is_float:
                try:
                    value = float(re.search(r'\b[0-9]+(\,|\.)?[0-9]*', value).group(0).replace(",", "."))
                except AttributeError:
                    return None
            return value

        def parse_hu(hu):
            if hu and (hu.lower() == "neu" or hu.lower() == "new"):
                m = str(date.today().month)
                y = str(int(date.today().year) + 2)

                if len(m) < 2:
                    m = "0" + m
                current_date = m + "/" + y
                return current_date

            return hu

        def parse_fr(fr): # first_registration
            if fr and (fr.lower() == "neu" or fr.lower() == "new"):
                m = str(date.today().month)
                y = str(int(date.today().year))

                if len(m) < 2:
                    m = "0" + m
                current_date = m + "/" + y
                return current_date
            return fr

        title = get("#ad-title::text")
        if not title:
            return
        item = Car()
        item['title'] = title
        item['price'] = get(".g-col-6.vip-price-rating__tech-details span::text", ["€", ",", "."], True)
        item['condition'] = get("#damageCondition-v::text")
        item['mileage'] = get("#mileage-v::text", ["km"])
        item['category'] = get("#category-v::text")
        item['airbag'] = get("#airbag-v::text")
        item['origin'] = get("#countryVersion-v::text")
        item['cubicCapacity'] = get("#cubicCapacity-v::text", ["cm3", "ccm"], True)
        item['fuel'] = get("#fuel-v::text")
        item['num_seats'] = get("#numSeats-v::text")
        item['gear'] = get("#transmission-v::text")
        item['hu'] = parse_hu(get("#hu-v::text"))
        item['first_registration'] = parse_fr(get("#firstRegistration-v::text"))
        item['climate_control'] = get("#climatisation-v::text")
        item['parking_assistant'] = get("#climatisation-v::text")
        item['interior'] = get("#interior-v::text")
        item['scraped_on'] = date.today()
        item['url'] = response.url

        item['manufacturer'] = None
        for car in cars:
            if car.lower() in str(title).lower():
                item['manufacturer'] = car.lower()

        item['consumption'] = None
        counter = 0
        for fuel_con in response.css(r"#envkv\.consumption-v .u-margin-bottom-9::text"):
            consumption = unicodedata.normalize("NFKD", fuel_con.get())
            if not item['consumption']:
                item['consumption'] = 0
            if re.search(r'\b[0-9]+(\,|\.)?[0-9]*', consumption):
                item['consumption'] += float(
                    re.search(r'\b[0-9]+(\,|\.)?[0-9]*', consumption).group(0).replace(",", "."))
                counter += 1
        if counter > 0:
            item['consumption'] /= counter

        item['co2'] = None
        if re.search(r'[0-9]+', str(get("#envkv\.emission-v::text"))):
            item['co2'] = re.search(r'[0-9]+', str(get("#envkv\.emission-v::text"))).group(0)

        item['power'] = None
        if get("#power-v::text"):
            item['power'] = get("#power-v::text").split("(")[1].lower().replace("hp)", "").replace("ps)", "").strip()

        try:
            item['doors'] = int(get("#doorCount-v::text").split("/")[0])
        except AttributeError:
            item['doors'] = None

        item['color'] = None
        if get("#color-v::text"):
            item['color'] = get("#color-v::text").lower()
        elif get("#manufacturerColorName-v::text"):
            item['color'] = get("#manufacturerColorName-v::text").lower()

        item['features'] = []
        rows = response.css("#features .g-row .g-col-6")
        for row in rows:
            item['features'].append(row.css(".bullet-list p::text").get())

        item['num_of_owners'] = None
        if get("#numberOfPreviousOwners-v::text"):
            item['num_of_owners'] = int(get("#numberOfPreviousOwners-v::text"))

        item['environment'] = None
        if get("#emissionsSticker-v::text"):
            item['environment'] = int(get("#emissionsSticker-v::text").split()[0])

        item['emissions'] = None
        if get("#emissionClass-v::text"):
            item['emissions'] = re.search(r'[0-9]+', str(get("#emissionClass-v::text"))).group(0)

        if sum([1 for x in item if item[x] is not None]) < 18:
            return None

        return item
