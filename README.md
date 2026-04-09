# Elections 2026 data

Get candidate data into the right format for the AI tools.

This takes raw CSV data from [Democracy Club](https://democracyclub.org.uk/) and outputs it as a JSON file in various formats to be used in the AI tools.

## Set up
* Clone the repo `git clone https://github.com/FullFact/election-2026-candidate-analysis.git`
* Go to the new `election-2026-candidate-analysis` folder you have just cloned
* `uv sync` to update packages
* `pre-commit install` to add pre-commit


## Running the code

To run the code: `uv run python src/main.py`. The output JSON files will be in the `data_outputs` folder.

If you can't run this code locally, you can run it in GitHub Codespaces. Go to: https://github.com/codespaces/new - select this repo and your chosen branch. 

### Updating the data
The current code downloads all election candidate data for 7th March 2026 so you do not have to do it manually. 

If you wish to read the CSV data from a file there is an option to do that (use `read_csv_data_from_file`).

The `raw_data` folder contains existing raw data from the [Democracy Club](https://democracyclub.org.uk/).

This data from Democracy Club is regularly updated, you can download the latest data from here if you wish: https://candidates.democracyclub.org.uk/data/. 


## Tests
`uv run pytest .`