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

Must run as root for access to NeoPixels.

```
sudo su
source venv/bin/activate
opsdroid start -f configuration.yaml
```
