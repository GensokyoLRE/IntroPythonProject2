"""
Program: PhillipSensor.py
Author: Phillip "Hifumi" Cuesta
Last Mod: 11/6/2018 8:13 PM
Purpose: Scanner for Project 2 using Riot API
"""
from League.sensor import Sensor
import json
import time
import requests
from datetime import datetime
import os # for json crafting purposes

CONFIG_FILE = 'PhillipSensor.json'


class LeagueSensor(Sensor):

    def __init__(self, a_region):
        """ read sensor settings from config file """
        with open(CONFIG_FILE) as json_text:
            self.__settings = json.load(json_text)
        self.__key = self.__settings.get('api_key')
        self.__region = a_region
        self.__url = self.__settings.get('service_url') % (self.__region, self.__key)
        print("Polling: " + self.__region)

    def has_updates(self, k):
        # Should keep cache in json of the last rankings received, otherwise update to new rankings.
        pointer = str(self.__region) + ".json"
        with open(pointer) as compareJ:
            compare_file = json.load(compareJ)
        if compare_file == k:
            print("Data is same, no update.")
        else:
            with open(pointer, 'w') as updater:
                json.dump(k, updater)
            with open(CONFIG_FILE) as timeLoad:
                clock_wind = json.load(timeLoad)
            clock_wind["last_update"] = time.time()
            clock_wind["last_date_update"] = str(datetime.now())
            with open(CONFIG_FILE, 'w') as timeWrite:
                json.dump(clock_wind, timeWrite)
            print("Data updated.")

    def get_content(self, k):
        # Read in content by team name and format data accordingly.
        response = requests.get(self.__url)
        region_response = response.json()
        pointer = str(self.__region) + ".json"
        if not os.path.isfile(pointer):
            with open(CONFIG_FILE) as jsonUpdate:
                new_set = json.load(jsonUpdate)
            with open(pointer, 'w') as updater:
                json.dump(region_response, updater)
            new_set["last_update"] = k
            new_set["last_date_update"] = str(datetime.now())
            with open(CONFIG_FILE, 'w') as jsonWrite:
                json.dump(new_set, jsonWrite)
            print("Data created.")
        else:
            print("Data exists.")
        return region_response

    def get_all(self):
        #
        pass


if __name__ == "__main__":
    regions = ["na1", "eun1", "euw1", "kr", "jp1", "ru"]
    for region in regions:
        sr = LeagueSensor(region)
        print("This is me : " + str(sr) + " scanning region tag [" + region + "]\n")
        newData = sr.get_content(time.time())
        sr.has_updates(newData)

