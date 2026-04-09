# Elections 2026 Analysis

Analysis of candidates from elections across the UK (May 2026).


## Set up
* Clone the repo `git clone https://github.com/FullFact/election-2026-candidate-analysis.git`
* Go to the new `election-2026-candidate-analysis` folder you have just cloned
* `uv sync` to update packages
* `pre-commit install` to add pre-commit


## Writing & running code

The `raw_data` folder contains the raw data from the Democracy Club.

This is regularly updated, you can download the latest data from here: 

You can use `main.py` to run the analysis (`uv run python src/main.py`) or there is a Jupyter Notebook (`exploratory_analysis.ipynb`). Obviously you can create your own files too!

The outputs should go into the `data_outputs` folder.

If you can't run this code locally, you can run it in GitHub Codespaces. Go to: https://github.com/codespaces/new - select this repo and your chosen branch. 


## Tests
`uv run pytest .`