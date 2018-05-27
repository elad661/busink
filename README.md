# busink
Realtime bus arrivals on a raspberry pi + an e-ink screen!

Uses [rpi_epd2in7](https://github.com/elad661/rpi_epd2in7/) and [curlbus](https://github.com/elad661/curlbus)

![a picture of busink in action](https://raw.githubusercontent.com/elad661/busink/master/busink.jpg)

## Installation instructions

Follow the instructions to install [rpi_epd2in7](https://github.com/elad661/rpi_epd2in7/),

Edit the configuration file to select your preferred stop and route,
edit the `.service` file to point to your installation location,
and then run

```bash
sudo pip3 install -r requirements.txt
# the following might be needed for Pillow to work:
sudo apt-get install libtiff5 libopenjp2-7

# Install the service
sudo cp busink.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable busink.service
sudo systemctl start busink.service
```

## Development
`main.py` contains a mock EPD class so you can develop on your desktop without
having to move the code to the Pi