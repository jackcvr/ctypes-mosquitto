TRAP 			:= trap 'docker compose --profile "*" down --remove-orphans' EXIT INT TERM
DC 				:= $(TRAP); docker compose
DC_RUN			:= $(DC) run --rm
LEVEL			?= INFO
PYTEST			= pytest -s --log-cli-level=$(LEVEL)

build:
	$(DC) build

test:
	$(DC_RUN) py $(PYTEST)

test-%:
	$(DC_RUN) py $(PYTEST) $(wildcard tests/$* tests/test_$**.py)

app:
	$(DC) up app

bench:
	export INTERVAL=0; $(DC_RUN) app sh -c "sleep 1 && python3 ./scripts/bench.py > benchmark.csv"
	$(MAKE) plot

plot:
	$(DC_RUN) py python3 ./scripts/plot.py

dist: clean test
	$(DC_RUN) py python -m build

pubtest:
	$(DC_RUN) py twine upload --verbose -r testpypi dist/*

publish:
	$(DC_RUN) py twine upload dist/*

clean:
	$(DC_RUN) py rm -rf ./dist *.egg-info/
