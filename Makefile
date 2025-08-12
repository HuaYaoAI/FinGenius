# Makefile for FinGenius project

# Default target
.PHONY: help install test clean

help:
	@echo "FinGenius Makefile"
	@echo "=================="
	@echo "Available targets:"
	@echo "  install     - Install the project using uv (recommended)"
	@echo "  install-conda - Install the project using conda"
	@echo "  test        - Run installation verification"
	@echo "  clean       - Clean up generated files"
	@echo "  help        - Show this help message"

# Install using uv (recommended)
install:
	@echo "Installing using uv..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	uv venv --python 3.12
	@echo "Activating virtual environment and installing dependencies..."
	uv pip install -r requirements.txt
	@echo "Creating configuration file..."
	cp config/config.example.toml config/config.toml
	@echo "Installation completed!"
	@echo "Next steps:"
	@echo "1. Edit config/config.toml to add your API keys"
	@echo "2. Activate the virtual environment: source .venv/bin/activate"
	@echo "3. Run the application: python main.py STOCK_CODE"

# Install using conda
install-conda:
	@echo "Installing using conda..."
	@echo "Creating conda environment..."
	conda create -n fingenius python=3.12
	@echo "Activating conda environment..."
	conda activate fingenius
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Creating configuration file..."
	cp config/config.example.toml config/config.toml
	@echo "Installation completed!"
	@echo "Next steps:"
	@echo "1. Activate the conda environment: conda activate fingenius"
	@echo "2. Edit config/config.toml to add your API keys"
	@echo "3. Run the application: python main.py STOCK_CODE"

# Run installation verification
test:
	@echo "Running installation verification..."
	python test_installation.py

# Clean up generated files
clean:
	@echo "Cleaning up..."
	rm -rf .venv/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf src/*/__pycache__/
	rm -rf config/config.toml
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Cleanup completed!"

# Run the application with a stock code
run:
	@echo "Running FinGenius..."
	@echo "Usage: make run STOCK_CODE=stock_code"
	@echo "Example: make run STOCK_CODE=000001"
	@if [ -z "$(STOCK_CODE)" ]; then \
		echo "Error: STOCK_CODE is not set"; \
		exit 1; \
	fi
	python main.py $(STOCK_CODE)