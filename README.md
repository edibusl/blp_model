# BLP Model
This flask app demonstrates a virtual FS that enforces the BLP model (Bell–LaPadula Model) file access rules.

## Installation
```bash
git clone https://github.com/edibusl/blp_model.git
cd blp_model
virtualenv -p python3 blp_env
source blp_env/bin/activate
pip install requirements.txt
```

## Running server (using gunicorn)
```bash
cd blp_model
source blp_env/bin/activate
gunicorn --timeout 9999999 --log-level debug --bind 0.0.0.0:3030 --worker-class=gthread start_server:app
```

## Running unit tests (using pytest)
```bash
cd blp_model
source blp_env/bin/activate
PYTHONPATH="." pytest tests/test_blp.py -v
```