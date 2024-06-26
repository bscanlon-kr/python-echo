import requests
import argparse
import json
import sys

HEADERS = {"kbn-xsrf": "kibana", "Content-Type": "application/json"}
# Set this if you don't want to have to pass in the command line arg every time
INDEX = "usage-metrics-clickstream-prod"
OUTPUT_FILE = "./output/response.json"
QUERY_FILE = "./queries/query.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cookie", "-c", type=str)
    parser.add_argument("--index", "-i", type=str)
    parser.add_argument("--output", "-o", type=str, help="The name of the output file for the echo query JSON")
    parser.add_argument("--query", "-q", type=str, help="The name of the query file to pull the Kibana query from")
    args = parser.parse_args()

    if args.query:
        query_file = args.query
    else:
        query_file = QUERY_FILE

    if args.output:
        output_file = args.output
    else:
        output_file = OUTPUT_FILE

    if args.index:
        index = args.index
    else:
        index = INDEX

    if args.cookie:
        cookie = args.cookie
    else:
        try:
            cookie_file = open("./cookie", 'r')
            cookie = cookie_file.read()
        except FileNotFoundError:
            print("You need to provide a echo_kinana_sid cookie via the command line -c flag or by storing it in the "
                  "cookie file", file=sys.stderr)
            sys.exit(1)
    HEADERS["Cookie"] = "echo_kibana_sid=" + cookie

    with open(query_file, 'r') as query_file:
        query = json.load(query_file)
        print("Running echo query this may time some time...")
        response = requests.post(
            url="https://echo.kroger.com/kibana/api/console/proxy?path=" + index + "%2F_search&method=GET",
            data=json.dumps(query),
            headers=HEADERS)
        print("Status Code: " + str(response.status_code))
    with open(output_file, 'w') as response_file:
        response_file.write(json.dumps(response.json()))


if __name__ == "__main__":
    main()
