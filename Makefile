N_LOOKBACK=5

venv/bin/activate: requirements.txt
	python -m venv venv
	./venv/bin/pip install -r requirements.txt

start: venv/bin/activate
	./venv/bin/python -m streamalyzer.start --n_lookback $(N_LOOKBACK)

test: venv/bin/activate
	./venv/bin/python -m pytest --cov=streamalyzer/ --cov-report=term --cov-report=html streamalyzer/

clean:
	rm -rf __pycache__
	rm -rf venv

.PHONY: clean start
