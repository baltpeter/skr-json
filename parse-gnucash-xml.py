import xmltodict
import pprint
from collections import OrderedDict
import json
import os
import sys

TYPE_TRANSLATIONS = {
	"root": "Oberkonto",
	"expense": "Aufwand",
	"income": "Ertrag",
	"asset": "Aktiva",
	"liability": "Fremdkapital",
	"payable": "Verbindlichkeit",
	"receivable": "Forderung",
	"cash": "Bargeld",
	"bank": "Bank",
	"credit": "Haben",
	"equity": "Eigenkapital"
}

def parse_slots(act_xml):
	slots_dict = {}

	if "act:slots" in act_xml:
		slots = act_xml["act:slots"]["slot"]
		if isinstance(slots, list):
			for od in slots:
				if isinstance(od, OrderedDict):
					if "#text" in od["slot:value"]: slots_dict[od["slot:key"]] = od["slot:value"]["#text"]
		else:
			if "#text" in slots["slot:value"]: slots_dict[slots["slot:key"]] = slots["slot:value"]["#text"]

	return slots_dict

def get_account_with_id(id, xml):
	for act_xml in xml["gnc-account-example"]["gnc:account"]:
		if act_xml["act:id"]["#text"] == id:
			return act_xml
	return {}

id_category_cache = {}

def get_categories(act_xml, xml):
	if act_xml["act:id"]["#text"] in id_category_cache:
		return id_category_cache[act_xml["act:id"]["#text"]]

	categories = []
	hierarchicalCategories = []

	current_act = act_xml
	while "act:parent" in current_act:
		current_act = get_account_with_id(current_act["act:parent"]["#text"], xml)
		if current_act["act:name"] != "Root Account": categories.append(current_act["act:name"])

	for i, cat in reversed(list(enumerate(categories))):
		hierarchicalCategories.append({ "lvl" + str(i): " > ".join(list(reversed(categories))[:i+1])})

	id_category_cache[act_xml["act:id"]["#text"]] = (categories, hierarchicalCategories)
	return categories, hierarchicalCategories

def main():
	if not len(sys.argv) == 2:
		print("Please provide the GnuCash XML path as the only argument.")
		sys.exit(0)

	accounts = []

	with open(sys.argv[1], encoding='utf-8') as f:
		xml = xmltodict.parse(f.read())

		for act_xml in xml["gnc-account-example"]["gnc:account"]:
			slots_dict = parse_slots(act_xml)

			account = {
				"objectID": act_xml["act:id"]["#text"],
				"name": act_xml["act:name"],
				"type": TYPE_TRANSLATIONS[act_xml["act:type"].lower()] if "act:type" in act_xml else "",
				"code": act_xml["act:code"] if "act:code" in act_xml else -1,
				"description": act_xml["act:description"] if "act:description" in act_xml else "",
				"categories": get_categories(act_xml, xml)[0],
				"hierarchicalCategories": get_categories(act_xml, xml)[1],
				"leaf": False
			}

			if "notes" in slots_dict:
				account["notes"] = slots_dict["notes"]
			if "placeholder" in slots_dict:
				account["placeholder"] = slots_dict["placeholder"] == "true"
			if "tax-related" in slots_dict:	
				account["tax-related"] = slots_dict["tax-related"] == "true"
			if "act:code" in act_xml:
				account["leaf"] = not "-" in act_xml["act:code"] and len(act_xml["act:code"]) == 4
			if "act:parent" in act_xml:
				account["parent"] = act_xml["act:parent"]["#text"]

			accounts.append(account)
	
	name = os.path.splitext(sys.argv[1])[0]
	with open(name + ".json", "w", encoding="utf-8") as f:
			json.dump(accounts, f, indent=4)
	os.makedirs(name, exist_ok=True)
	for act in accounts:
		with open(name + "/" + act["objectID"] + ".json", "w", encoding="utf-8") as f:
			json.dump(act, f, indent=4)


if __name__ == "__main__":
    main()