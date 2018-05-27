# busink - displays real time bus arrivals on an e-ink screen
#
# Copyright 2018 Elad Alfassa <elad@fedoraproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from rpi_epd2in7.epd import EPD
from dateutil.parser import parse
import dateutil
from datetime import datetime
import configparser
import requests
import time

HEADERS = {"Accept": "application/json"}


# class EPD(object):
#     """ Mock EPD for development without RPi """
#     width = 176
#     height = 264
#
#     def init(self):
#         """ mock EPD init """
#         return True
#
#     def diplay_frame(self, image):
#         image.show()
#
#     def smart_update(self, image):
#         image.show()
#
#     def sleep(self):
#         return True


class App(object):
    def __init__(self, config):
        self.epd = EPD()
        self.epd.init()
        self.font = config['font']
        self.route = config['route']
        self.stop = config['stop']
        self.curlbus = config['curlbus']

    def draw(self, eta, last_updated):
        self.epd.init()
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        # Draw the line number on the top conrner
        font = ImageFont.truetype(self.font, 30)
        draw.text((5, 2), self.route, font=font, fill=0)
        draw.rectangle([(0, 0), (60, 40)])

        # Draw the ETA
        font = ImageFont.truetype(self.font, 60)
        draw.text((self.epd.height/2 - 50, self.epd.width/2 - 50), eta, font=font, fill=0)

        # Draw the last_updated timestamp
        font = ImageFont.truetype(self.font, 16)
        draw.text((0, self.epd.width - 20), last_updated, font=font, fill=0)
        self.epd.smart_update(image.rotate(90, expand=True))
        self.epd.sleep()

    def update(self):
        response = requests.get("{0}/{1}".format(self.curlbus, self.stop), headers=HEADERS)
        response_data = response.json()
        last_updated = response_data['timestamp']
        next_eta = "Nothing :("
        etas = []
        for visit in response_data['visits'][self.stop]:
            if visit['line_name'] == self.route:
                etas.append(parse(visit['eta']))
        if len(etas) > 0:
            closest_eta = sorted(etas)[0]
            next_eta = round((closest_eta - datetime.now(dateutil.tz.tzlocal())).total_seconds() / 60)
            if next_eta <= 0:
                next_eta = 'Now'
            else:
                next_eta = '{0}m'.format(next_eta)
        self.draw(next_eta, last_updated)

    def run(self):
        while True:
            self.update()
            time.sleep(60)


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")
    config_dict = {s: dict(config.items(s)) for s in config.sections()}
    app = App(config_dict['app'])
    app.run()


if __name__ == "__main__":
    main()