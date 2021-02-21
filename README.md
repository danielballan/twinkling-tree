# Twinkling Tree

This is used to control individually-controllable RGB LED lights on my tree. It
has a couple aspects, which might be useful _a la carte_ in other projects.

* Set the lights to a color or set of colors by providing a color name from the
  [XKCD color survey](https://blog.xkcd.com/2010/05/03/color-survey-results/).
* Run a variety of nice-looking dynamic patterns.
* Control the lights via a variety of different chat clients, including text
  messages, using the included configuration for [opsdroid](http://opsdroid.dev/).

## Setup

[![Join the chat at https://gitter.im/danielballan/twinkling-tree](https://badges.gitter.im/danielballan/twinkling-tree.svg)](https://gitter.im/danielballan/twinkling-tree?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

```
sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run examples from Python

Must run as root for access to NeoPixels.

```
sudo su
source venv/bin/activate
python -m twinkling_tree.stunts.rainbow
```

## Optional: Use opsdroid to run examples from chat clients

Configure

```
cp configuration.example.yaml configuration.yaml
# Add tokens to configuration.yaml. Then:
opsdroid config build configuration.yaml
```

Must run as root for access to NeoPixels. Try it interactively at first.

```
sudo su
source venv/bin/activate
opsdroid start -f configuration.yaml
```

Wait for the log line like:

```
INFO opsdroid.core: Opsdroid is now running, press ctrl+c to exit.
```

to test.

And run it as a system service like:

```
# This path to the file below must be specified an absolute path.
# Otherwise ln will fail *silently*.
sudo ln -s /home/pi/twinkling-tree/opsdroid.service /etc/systemd/system/opsdroid.service
sudo systemctl daemon-reload
sudo systemctl start opsdroid.service
sudo systemctl enable opsdroid.service
sudo systemctl status opsdroid.service
```

Tail logs like

```
sudo journalctl -f -u opsdroid.service
```
