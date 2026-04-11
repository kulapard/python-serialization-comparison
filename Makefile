.PHONY: bench clean

bench: ## Run benchmark
	uv run bench.py

clean: ## Remove venv and cache
	rm -rf .venv __pycache__ *.egg-info
