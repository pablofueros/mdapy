.PHONY: install format lint test

install:
	uvx prek install

format:
	uvx ruff check --fix
	uvx ruff format

lint:
	uvx ruff check
	uv run ty check

test:
	uv run python -m pytest