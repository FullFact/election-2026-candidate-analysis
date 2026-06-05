# Elections 2026 data

Get candidate data into the right format for the AI tools.

This takes raw CSV data from [Democracy Club](https://democracyclub.org.uk/) and outputs it as a JSON file in various formats to be used in the AI tools.

## Set up
* Clone the repo `git clone https://github.com/FullFact/election-2026-candidate-analysis.git`
* Go to the new `election-2026-candidate-analysis` folder you have just cloned
* `uv sync` to update packages
* `pre-commit install` to add pre-commit

If you can't run this code locally, you can run it in GitHub Codespaces. Go to: https://github.com/codespaces/new - select this repo and your chosen branch. 


## Updating the data
The `raw_data` folder contains existing raw data from the [Democracy Club](https://democracyclub.org.uk/).

This data from Democracy Club is regularly updated, you can download the latest data from here if you wish: https://candidates.democracyclub.org.uk/data/. 


## Formatting Democracy Club data

To run the code: `uv run python src/main.py` - you may need to adjust the data for your input file. The output JSON files will be in the `data_outputs` folder.


## Getting Twitter usernames into the right format
This takes Democracy Club CSV data and gets it into a JSON file mapping parties to lists of usernames. Adjust the name of the file you are reading data from in `twitter_by_party.py` and run:
```
uv run python twitter_by_party.py
```


## Uploading Twitter usernames to a list
Input data format as a JSON:
```
{
    "Labour": ["username1", "username2", ... ],
    "Party 2": ["username3", ... ],
    ....
}
```

This uses `script/add_to_list.py`.

To run the script you will need a database with accounts details in the root of this repo. This defaults to `accounts.db`. (Do not commit this!)


To create a new list:
```
uv run python scripts/add_to_list.py from-json <PATH_TO_JSON> --prefix "Local 2026 - " --private
```


To add to an existing list:
```
uv rub python scripts/add_to_list.py manual --list-id <LIST_ID> username1 username2
```
You find the `<LIST_ID>` from the URL of the list in Twitter.


To list all the members of a list:
```
uv run python scripts/add_to_list.py get-members --list-id <LIST_ID>
```


See more details and options on how to run in `add_to_list.py`.


## Tests
`uv run pytest .`


