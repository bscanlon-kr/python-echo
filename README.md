# python-echo
Scripts for querying and parsing echo indices 

# SETUP
- clone this repo
- [Optional] download PyCharm IDE
  - Open repo in PyCharm and setup a venv using python3
  - open terminal in IDE and install `requests` 
    - pip3 install requests
- If not using PyCharm install requests on your system
  - pip3 install requests

# Running
- Get the echo_kinana_sid cookie from your browser
  - Save that cookie in the `cookie` file in the root of this repo
  - The cookie can also be provided via the command line using `-c the_cookie_value`
- Build the query you want in echo select `inspect` copy the request and save it in the /queries/query.json
- Update the script `query_echo.py` to set the `INDEX` you are wanting to query, for example `atlas-prod-checkout`
  - You can also pass in the index when running this script from the terminal like so `query_echo.py -i atlas-prod-checkout`

# Write some code to parse your data
- `parse_echo.py` contains examples of how to parse the echo response each use case will be unique, if you think what you are doing will be helpful in the future please commit those changes back here.

# NOTES
- You will need to get a new cookie no idea how often... if you are getting a non-200 response (logged to the terminal) check that first
- The query you get from echo will have a `size` at the top, that is how many records to pull. The max is 10000
- Sometimes JSON data gets corrupted in echo due to the credit card masking they have so you may have to try/catch to bypass invalid hits