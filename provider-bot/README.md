# provider-bot 

## How to install
1. `virtualenv -p python3 venv`
2. `. ./venv/bin/activate`
3. `pip install -r requirements.txt`

## How to train
`python -m provider_bot build `

## How to run
1. `sudo docker run -ti -d -p 0.0.0.0:9200:9200 -p 0.0.0.0:7151:7151 -p 0.0.0.0:9300:9300 mindmeldworkbench/dep:es_7 `
2. `mindmeld num-parse`
3. `python ./run_server.py` or 3. `python ./run_api.py`
