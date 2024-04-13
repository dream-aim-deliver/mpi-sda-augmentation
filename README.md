# mpi-sda-satellite

## Description
This is a Satellite Image scraper that uses the SentinelHub API to scrape Images for a given location and date.

## Usage
```bash
cp .env.template .env
```
### Fill in the environment variables
- sh_client_id = {ENTER THE CLIENT ID FROM [Sentinal Hub](https://www.sentinel-hub.com/)}
- sh_client_secret = {ENTER CLIENT SECRET FROM [Sentinal Hub](https://www.sentinel-hub.com/)}
- HOST={THE HOSTNAME OF THE FASTAPI APP}
- PORT={THE PORT OF THE FASTAPI APP}

### Run the container
```bash
./run.sh
```
### Run the Hawaii demo
./demo.sh
## Development
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```