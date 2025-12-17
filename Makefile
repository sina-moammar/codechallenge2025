.PHONY: install generate test leaderboard clean dummy-test all

install:
	uv sync

generate:
	uv run src/codechallenge2025/dataset_generator.py

test:
	uv run tests/run_challenge.py

leaderboard:
	uv run tests/update_leaderboard.py

clean:
	rm -rf data/*.csv leaderboard.json Leaderboard.md

dummy-test:
	cp src/codechallenge2025/dummy_solution.py src/codechallenge2025/participant_solution.py
	@echo "Dummy solution installed. Now commit & push to test CI."

all: install generate test leaderboard