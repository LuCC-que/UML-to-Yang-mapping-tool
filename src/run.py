import pathlib

# import json
# path = pathlib.Path().resolve().joinpath("resources/container1.uml")
# print(path)
# with open(path) as xml_file:

#     data_dict = xmltodict.parse(xml_file.read())

# print(json.dumps(data_dict, indent=4))

import pathlib

from factory.makeYang import makeYangInJson

path = pathlib.Path().resolve().joinpath("resources/container1.uml")

Json = makeYangInJson(path).xmlModel
# print(json.dumps(Json, indent=4))
