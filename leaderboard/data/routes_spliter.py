import xml.etree.ElementTree as ET
import os
import sys


xml_file = sys.argv[1]
assert os.path.exists(xml_file), f"Input file {xml_file} does not exist!"

basename = os.path.splitext(os.path.basename(xml_file))[0]
savedir = "citcom_data"
print(xml_file, basename)
# assert not os.path.exists(f"{savedir}/{basename}"), f"Output directory {savedir} already exists!"
# os.makedirs(f"{savedir}/{basename}")

tree = ET.parse(xml_file)
routes = tree.getroot()

for route in routes:
    new_routes = ET.Element("routes")
    id = route.get("id")
    route.set("id", "0")
    new_routes.append(route)
    ET.ElementTree(new_routes).write(f"{savedir}/{basename}_route_{id}.xml")
