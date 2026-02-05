# odyssey-hackathon

## Quick Setup (Conda)

1. Ensure you have Conda installed.
2. Create the environment:
   ```bash
   conda env create -f environment.yml
   ```
   Or run:
   ```bash
   bash scripts/create_conda_env.sh
   ```
3. Activate the environment:
   ```bash
   conda activate odyssey-hackathon
   ```

## Quick Setup (venv)

1. Install Python 3.12+
2. Create and activate a virtual environment:
	```bash
	python3.14 -m venv .venv
	source .venv/bin/activate
	```
3. Install dependencies:
	```bash
	pip install -e .
	```
4. Or run:
	```bash
	bash scripts/create_venv.sh
	```

Project dependencies and Python version are managed in `pyproject.toml`.

The Odyssey Python SDK will be installed automatically from GitHub:
	- https://github.com/odysseyml/odyssey-python
If you want to install it manually:
	```bash

The Google Generative AI SDK (`google-genai`) will also be installed automatically.
To install it manually:
	```bash
	pip install -q -U google-genai

The Pillow library (`PIL`) will also be installed automatically.
To install it manually:
	```bash
	pip install Pillow
	```
	```
	pip install git+https://github.com/odysseyml/odyssey-python.git
	```

Note: Make sure to update the GOOGLE_API_KEY `export GOOGLE_API_KEY=<API_KEY>`

`test_nano_banana.py` -> Works with Google API Key. 