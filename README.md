## Setup

```
sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run examples

Must run as root for access to NeoPixels.

```
sudo su
source venv/bin/activate
python -m twinkling_tree.stunts.rainbow
```

## Optional: Use opsdroid

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
