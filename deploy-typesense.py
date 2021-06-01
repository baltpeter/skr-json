import typesense
import os
from pathlib import Path
import json
import sys

if not len(sys.argv) == 2:
    print("Please provide the SKR name as the only argument.")
    sys.exit(0)

index_name = sys.argv[1]
if index_name.endswith('.xml'):
    print("Please only provide the SKR name (without '.xml').")
    sys.exit(0)

client = typesense.Client({
    'api_key': os.environ['TYPESENSE_KEY'],
    'nodes': [{
        'host': os.environ['TYPESENSE_HOST'],
        'port': os.environ['TYPESENSE_PORT'],
        'protocol': os.environ['TYPESENSE_PROTOCOL']
    }],
    'connection_timeout_seconds': 10
})


# Using collection aliases would be a lot cleaner here of course but this should be fast enough for me not to care.
try:
    client.collections[index_name].delete()
except:
    pass
schema = {
    'name': index_name,
    'default_sorting_field': 'sort-code',
    'fields': [
        {'name': 'id', 'type': 'string'},
        {'name': 'name', 'type': 'string'},
        {'name': 'type', 'type': 'string', 'facet': True},
        {'name': 'code', 'type': 'string'},
        {'name': 'sort-code', 'type': 'int32'},
        {'name': 'description', 'type': 'string'},
        {'name': 'categories', 'type': 'string[]'},
        {'name': 'leaf', 'type': 'bool'},
        {'name': 'notes', 'type': 'string', 'optional': True},
        {'name': 'placeholder', 'type': 'bool', 'optional': True},
        {'name': 'tax-related', 'type': 'bool', 'optional': True},
        {'name': 'parent', 'type': 'string', 'optional': True},
    ]
}
for i in range(0, 6):
    schema['fields'].append(
        {'name': 'hierarchicalCategories.lvl' + str(i), 'type': 'string', 'facet': True, 'optional': i != 0})

client.collections.create(schema)

records = []

# see https://stackoverflow.com/a/10378012
pathlist = Path(index_name).glob('**/*.json')
for path in pathlist:
    record = json.load(open(str(path), encoding='utf-8'))

    records.append(record)

client.collections[index_name].documents.import_(records)
