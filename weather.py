import requests
import json
import argparse
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QShortcut
import sys


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("city", help="location")
    parser.add_argument("when", help="current or forecast", choices=['current', 'forecast'])
    return parser.parse_args()


def request(city, when):
    api_key = '2b026bcac31d496ee0f24ef0af206b8e'
    url = ''
    if when == "current":
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    elif when == "forecast":
        url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'
    response = requests.request('GET', url)
    if not response.status_code == 200:
        raise RuntimeError("Something bad happened")
    return response.json()


def output(response):
    info_list = []
    info = ""
    if 'list' not in response.keys():                       # current
        info = f"description: {response['weather'][0]['main']}, {response['weather'][0]['description']}\n" \
               f"temperature: {response['main']['temp']} celsius\n" \
               f"humidity: {response['main']['humidity']}%\n"  \
               f"cloudiness: {response['clouds']['all']}%\n" \
               f"wind: {response['wind']['speed']} m/s\n"
        if 'rain' in response.keys():
            info += f"mm of rain for the last hour: {response['rain']['1h']}"
        place = f"{response['name']}, {response['sys']['country']}"
        info_list.append(info)
    else:                                                           # forecast
        resp_list = response['list']
        for k in resp_list:
            time = k['dt_txt'].split(' ')
            time.pop(0)
            time = time[0]
            if time == '12:00:00' or time == '15:00:00':
                info += f"description: {k['weather'][0]['main']}, {k['weather'][0]['description']}\n" \
                        f"temperature: {k['main']['temp']} celsius\n" \
                        f"humidity: {k['main']['humidity']}%\n" \
                        f"cloudiness: {k['clouds']['all']}%\n" \
                        f"wind: {k['wind']['speed']} m/s\n" \
                        f"probability of precipitation: {k['pop']}\n"
                if 'rain' in k.keys():
                    info += f"mm of rain for the 3 last hours: {k['rain']['3h']}\n"
                info += f"time: {k['dt_txt']}\n"
                info += "\n"
            if time == '15:00:00':
                info_list.append(info)
                info = ""
            if len(info_list) == 3:
                break
        place = f"{response['city']['name']}, {response['city']['country']}"
    return [info_list, place]       # todo after 12am case


class Window(QMainWindow):
    def __init__(self, infos):
        super().__init__()
        info, place = infos
        self.setStyleSheet("background-color: black; color:white")

        self.label = QLabel(info[0], self)
        self.label.setFont(QFont('Arial', 20))
        self.label.resize(600, 800)
        self.label.move(100, 250)
        self.label.setAlignment(Qt.AlignTop)
        if len(info) > 1:                       # forecast
            self.label1 = QLabel(info[1], self)
            self.label1.setFont(QFont('Arial', 20))
            self.label1.resize(600, 800)
            self.label1.move(700, 250)
            self.label1.setAlignment(Qt.AlignTop)

            self.label2 = QLabel(info[2], self)
            self.label2.setFont(QFont('Arial', 20))
            self.label2.resize(600, 800)
            self.label2.move(1300, 250)
            self.label2.setAlignment(Qt.AlignTop)

        self.label_top = QLabel('weather info', self)
        self.label_top.setFont(QFont('Arial', 30))
        self.label_top.resize(800, 100)
        self.label_top.move(800, 50)

        self.label_place = QLabel(place, self)
        self.label_place.setFont(QFont('Arial', 30))
        self.label_place.resize(800, 60)
        self.label_place.move(800, 150)

        self.shortcut = QShortcut(QKeySequence("Esc"), self)           # closing window by keyboard
        self.shortcut.activated.connect(self.close_window)

    def close_window(self):
        self.close()

        self.show()
        self.close()


def main():
    args = arguments()
    city = args.city
    when = args.when
    response = request(city, when)
    infos = output(response)
    print(json.dumps(response, indent=4))

    app = QApplication(sys.argv)
    window = Window(infos)
    window.showFullScreen()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
