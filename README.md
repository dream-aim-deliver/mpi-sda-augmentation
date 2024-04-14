# mpi-sda-augmentation

## Description
This is a augmentation repo that runs in data pipline after twitter, sentinel, and telegram

## Usage
```bash
cp .env.template .env
```

### Run the container
```bash
python augment_main.py
```

## Development
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python augment_main.py
```