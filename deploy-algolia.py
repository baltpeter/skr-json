from algoliasearch import algoliasearch
import os
from pathlib import Path
import json
import sys

if not len(sys.argv) == 2:
	print("Please provide the SKR name as the only argument.")
	sys.exit(0)

client = algoliasearch.Client(os.environ['algolia_app_id'], os.environ['algolia_admin_api_key'])
index = client.init_index(sys.argv[1])

records = []

# see https://stackoverflow.com/a/10378012
pathlist = Path(sys.argv[1]).glob('**/*.json')
for path in pathlist:
    record = json.load(open(str(path), encoding='utf-8'))
    
    records.append(record)

index.saveObjects(records)