import requests
from bs4 import BeautifulSoup
import pandas as pd
import utlis

headers = {
    'Referer': 'https://itunes.apple.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/75.0.3770.142 Safari/537.36'
}

proxies = {"http": "http://111.233.225.166:1234"}
all_cars = []

# dict key:damage information value:url
url_dic = {

    "Badly damaged": [
        "https://www.arabam.com/ikinci-el/otomobil?damagestatus=A%C4%9F%C4%B1r%20Hasarl%C4%B1&sort=startedAt.desc"
        "&take=50&page=",
        "https://www.arabam.com/ikinci-el/otomobil-sahibinden?damagestatus=A%C4%9F%C4%B1r+Hasarl%C4%B1&sort=startedAt.desc&take=50&page=",
        "https://www.arabam.com/ikinci-el/otomobil-galeriden?damagestatus=A%C4%9F%C4%B1r+Hasarl%C4%B1&sort=startedAt.desc&take=50&page="],



    "Unchanging": ["https://www.arabam.com/ikinci-el/otomobil?damagestatus=De%C4%9Fi%C5%9Fensiz&sort=startedAt.desc&take=50&page=",
                   "https://www.arabam.com/ikinci-el/otomobil-sahibinden?damagestatus=De%C4%9Fi%C5%9Fensiz&sort=startedAt.desc&take=50"
                   "&page=",
                   "https://www.arabam.com/ikinci-el/otomobil-galeriden?damagestatus=De%C4%9Fi%C5%9Fensiz&sort=startedAt.desc&take=50&page="],

    "Without Tramer": ["https://www.arabam.com/ikinci-el/otomobil?damagestatus=Tramersiz&sort=startedAt.desc&take=50&page=",
                       "https://www.arabam.com/ikinci-el/otomobil-sahibinden?damagestatus=Tramersiz&sort=startedAt.desc&take=50&page=",
                       "https://www.arabam.com/ikinci-el/otomobil-galeriden?damagestatus=Tramersiz&sort=startedAt.desc&take=50&page="],

    "Unpainted": ["https://www.arabam.com/ikinci-el/otomobil?damagestatus=Boyas%C4%B1z&sort=startedAt.desc&take=50&page=",
                  "https://www.arabam.com/ikinci-el/otomobil-sahibinden?damagestatus=Boyas%C4%B1z&sort=startedAt.desc&take=50&page=",
                  "https://www.arabam.com/ikinci-el/otomobil-galeriden?damagestatus=Boyas%C4%B1z&sort=startedAt.desc&take=50&page="
                  ],

    "Unpainted-Unchanging": ["https://www.arabam.com/ikinci-el/otomobil?damagestatus=Boyas%C4%B1z+ve+De%C4%9Fi%C5"
                             "%9Fensiz&sort=startedAt.desc&take=50&page=",
                             "https://www.arabam.com/ikinci-el/otomobil-sahibinden?damagestatus=Boyas%C4%B1z+ve+De%C4"
                             "%9Fi%C5%9Fensiz&sort=startedAt.desc&take=50&page=",
                             "https://www.arabam.com/ikinci-el/otomobil-galeriden?damagestatus=Boyas%C4%B1z+ve+De%C4"
                             "%9Fi%C5%9Fensiz&sort=startedAt.desc&take=50&page="],

    "Unpainted-Unchanging-Without Tramer": [
        "https://www.arabam.com/ikinci-el/otomobil?damagestatus=Boyas%C4%B1z,"
        "+De%C4%9Fi%C5%9Fensiz+ve+Tramersiz&sort=startedAt.desc&take=50&page=",
        "https://www.arabam.com/ikinci-el/otomobil-sahibinden?damagestatus=Boyas%C4%B1z,"
        "+De%C4%9Fi%C5%9Fensiz+ve+Tramersiz&sort=startedAt.desc&take=50&page=",
        "https://www.arabam.com/ikinci-el/otomobil-galeriden?damagestatus=Boyas%C4%B1z,"
        "+De%C4%9Fi%C5%9Fensiz+ve+Tramersiz&sort=startedAt.desc&take=50&page="]
}

for key in url_dic:
    for url in url_dic[key]:
        for page in range(1, 51):

            print(f'{url}{page}')
            try:
                response = requests.get(f'{url}{page}',
                                        headers=headers, proxies=proxies)
                # print(response)
                response = response.text
            except requests.exceptions.ConnectionError as e:
                print(f"Error connecting to the server: {e}")

            except requests.exceptions.HTTPError as e:
                print(f"HTTP error occurred: {e}")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")

            # This code is contributed by Susobhan Akhuli

            else:
                soup = BeautifulSoup(response, "lxml")
                cars = soup.find_all('tr', class_="listing-list-item should-hover bg-white")

                for car in cars:
                    car_ = ""
                    brand = car.find("div",
                                     class_="listing-text-new word-break val-middle color-black2018").get_text().strip()
                    car_ += brand + ","
                    num = 0
                    print(brand)
                    car_price = car.find("span", class_="db no-wrap listing-price").get_text().strip()
                    car_ += car_price + ","
                    for info in car.find_all("td", class_="listing-text"):
                        info = info.find("div", class_="fade-out-content-wrapper")
                        car_ += info.get_text().strip().replace("\n", " ") + " km,"
                    # key = damage information
                    car_ += key
                    # print(car_)
                    print(car_.split(","))
                    print(len(car_.split(",")))

                    if len(car_.split(",")) == 8:
                        all_cars.append(car_)
            # print(all_cars)

            if page % 2 == 0 and all_cars:
                f = open("car1.txt", "w")
                for car in all_cars:
                    f.write(car)
                    f.write("\n")
                f.close()
                all_cars = []

                dataframe1 = pd.read_csv('car1.txt', encoding='windows-1254', on_bad_lines='skip')
                dataframe1.columns = ['Brand', 'Price', 'Year', 'Kilometer', 'Color', 'Date', 'Province/District',
                                      'Damage Information']

                dataframe1 = utlis.arrange_df(dataframe1)
                dataframe2 = pd.read_csv('data.csv', low_memory=False)
                frames = [dataframe1, dataframe2]

                result = pd.concat(frames)
                result = result.drop_duplicates()
                result = result.dropna()

                result.to_csv('data.csv', index=None)

result = pd.read_csv("data.csv", low_memory=False)
result = result.drop_duplicates()
result = result.dropna()
result.to_csv('data.csv', index=None)
