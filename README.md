# POCs xml to csv

Transforms point of contact XML data, exported from Geonetwork using the `/srv/api/registries/actions/entries/collect?` GET API endpoint, into a CSV data. If no output file is specified, it is written directly in the console (stdout).
Not every field is included, only the most essential ones. It should be quite straightforward to adjust the selection if necessary.

This CLI uses the [click](https://click.palletsprojects.com) library. If you want to understand how it works, it is advised that you at least run through click's documentation.

## Why this script ?
GeoNetwork provides an API endpoint that can collect the POCs and feed them directly into its POC registry. This is actually the same endpoint, with PUT protocol. 
While this works great, it is not that easy for later clean-up of redundant or unwanted records. At least when you collect a few thousands of POCs. We assumed it would be simpler to do on a spreadsheet.

## How was the source XML data retrieved
It was done through the GN API, using the following script
```shell

# Adjust the following variables
CATALOG="http://localhost:8080/catalogue"
CATALOGUSER=admin
CATALOGPASS=admin

rm results.json
rm -f /tmp/cookie;

# Initiate the authenticated session
curl -s -c /tmp/cookie -o /dev/null \
  -X GET \
  --user "$CATALOGUSER:$CATALOGPASS" \
  -H "Accept: application/json" \
  "$CATALOG/srv/api/me";
#cat /tmp/cookie

TOKEN="`grep XSRF-TOKEN /tmp/cookie | cut -f 7`":
JSESSIONID="`grep JSESSIONID /tmp/cookie | cut -f 7`";

# Should display user details:
curl "$CATALOG/srv/api/me" \
  -H 'accept: application/json, text/plain, */*' \
  -H 'accept-language: eng' \
  -H "X-XSRF-TOKEN: $TOKEN" \
  -H "Cookie: XSRF-TOKEN=$TOKEN; JSESSIONID=$JSESSIONID"


# Run the search, display 1 result (we could even not display any). The search is persisted in a bucket, that I arbitrarily named pocs
curl -X POST "$CATALOG/srv/api/search/records/_search?bucket=pocs" \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json;charset=utf-8' \
    -H "X-XSRF-TOKEN: $TOKEN" -H "Cookie: XSRF-TOKEN=$TOKEN; JSESSIONID=$JSESSIONID" \
    --compressed \
    -d '{"from":0,"size":1,"query":{"query_string":{"query":"(documentStandard:\"iso19115-3.2018\") AND (isTemplate:\"n\")"}}}'

# Select all the entries from bucket pocs
curl -X PUT "$CATALOG/srv/api/selections/pocs" -H "accept: application/json" \
  -H "X-XSRF-TOKEN: $TOKEN" -H "Cookie: XSRF-TOKEN=$TOKEN; JSESSIONID=$JSESSIONID" \
    --compressed
    
# Optional: display the current state of selections. Should say that pocs has a number of selected records
curl -X GET "$CATALOG/srv/api/selections" -H "accept: application/json" \
  -H "X-XSRF-TOKEN: $TOKEN" -H "Cookie: XSRF-TOKEN=$TOKEN; JSESSIONID=$JSESSIONID" \
    --compressed
    
# Scan the records and collect all CI_Responsibility snippets. Store them in local pocs.xml file
curl -X GET "$CATALOG/srv/api/registries/actions/entries/collect?bucket=pocs&xpath=.//cit:CI_Responsibility&identifierXpath=.//cit:electronicMailAddress/*/text()" \
    -H  "accept: application/xml"\
    -H "X-XSRF-TOKEN: $TOKEN" -H "Cookie: XSRF-TOKEN=$TOKEN; JSESSIONID=$JSESSIONID" \
    --compressed \
    -o pocs.xml
```


## Install
It leverages setuptools, [as advised in the click documentation](https://click.palletsprojects.com/en/8.0.x/quickstart/#switching-to-setuptools) to build an executable file. You don't necessary need this, but it can provide you ultimately with a nice executable. It should even be able to run on Windows (not tested though).

To install the script, you can run 
```shell
python3 -m venv .venv
. .venv/bin/activate
pip install --editable .
pocs_xml2csv --help
```

## Run
To convert the sample pocs.xml file, you can run 
```shell
pocs_xml2csv data/pocs.xml -o pocs.csv
```