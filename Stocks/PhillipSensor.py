"""
Program: PhillipSensor.py
Author: Phillip "Hifumi" Cuesta (source by Wolfgang Paulus)
Last Mod: 11/8/18 8:20 PM
Purpose: Scans stocks pertinent to the local San Diego area.
Addendum:
Data provided for free by IEX (https://iextrading.com/developer).
View IEX’s Terms of Use (https://iextrading.com/api-exhibit-a/).
"""
import os
from Stocks.sensor import Sensor
import json
import time
import requests
from datetime import datetime
import logging

CONFIG_FILE = 'PhillipSensor.json'
startTime = time.time()

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(os.getcwd(), 'logs', 'phillipsensor.log'),
    filemode='a',
    format='%(asctime)s - %(lineno)s - %(message)s'
)


class MySensor(Sensor):
    def __init__(self):
        """ read sensor settings from config file """
        with open(CONFIG_FILE) as json_text:
            self.__settings = json.load(json_text)
        self.__url = self.__settings.get('service_url')
        self.ticks = self.__settings.get('ticks')
        logging.info("This sensor just woke up .. ready to call " + self.__url)

    def has_updates(self, k):
        response = requests.get(self.__url % k)
        j_response = response.json()
        if not self.__j_response == j_response:
            self.__j_response = j_response
            logging.info("%s.json is now updated." % k)
        else:
            logging.info("%s.json has the same data." % k)

    def get_content(self, k):
        response = requests.get(self.__url % k)
        self.__j_response = response.json()
        pointer = "./tickFile/" + k + ".json"
        if self.can_request():
            updateable = True
            if not os.path.isfile(pointer):
                self.__settings['last_stamp'] = str(datetime.now())
                with open(pointer, 'w') as updater:
                    json.dump(self.__j_response, updater)
                with open(CONFIG_FILE, 'w') as settingUpdate:
                    json.dump(self.__settings, settingUpdate)
                self.__settings['last_request'] = int(time.time())
                logging.info("Data created for %s." % pointer)
            else:
                logging.info("Data exists. Checking update on %s." % pointer)
                self.has_updates(k)
        else:
            updateable = False
            logging.info("Still on the clock. Sleeping for %s seconds cooldown."
                         % int(time.time() - self.__settings['last_request']))
            time.sleep(int(time.time() - self.__settings['last_request']))
        return updateable

    def get_all(self):
        for tick in self.ticks:
            pointer = "./tickFile/" + tick + ".json"
            with open(pointer, 'r') as allRead:
                read_out = json.load(allRead)
            print(read_out)

    def can_request(self):
        return int(time.time() - self.__settings['last_request'] > self.__settings['request_delta'])

    def __save_settings(self):
        with open(os.path.join(os.path.dirname(__file__), CONFIG_FILE), 'w') as outfile:
            json.dump(self.__settings, outfile)

    def __eq__(self, other):
        if isinstance(other, MySensor):
            return self.__j_response == other.__j_response
        return False


if __name__ == "__main__":
    sr = MySensor()
    print("This is me : " + str(sr))
    print("let's go ..")
    ticks_scan = list.copy(sr.ticks)
    ticks_print = list.copy(sr.ticks)
    while ticks_scan:
        up = sr.get_content(ticks_scan[-1])
        if up:
            ticks_scan.pop(-1)
    logging.info("Wrapping up...")
    for tick in ticks_print:
        sTick = str(tick)
        point = "./tickFile/" + tick + ".json"
        with open(point, 'r') as reader:
            data = json.load(reader)
        print("Company: %s\n"
              "Company Type: %s\n"
              "Latest High: %.1f\n"
              "Lastest Low: %.1f\n"
              "Latest Price: %.2f\n" % (data[sTick.upper()]['quote']['companyName'],
                                        data[sTick.upper()]['quote']['sector'],
                                        data[sTick.upper()]['quote']['high'],
                                        data[sTick.upper()]['quote']['low'],
                                        data[sTick.upper()]['quote']['latestPrice']))
    print("Sensor file finished job in %.2f seconds." % (time.time() - startTime))
    logging.info("Sensor file finished job in %.2f seconds." % (time.time() - startTime))
