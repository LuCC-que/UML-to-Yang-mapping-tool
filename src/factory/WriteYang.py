import json
from .BuildYang import makeYangInJson


def writeYang(classes, associations):
    result = ''
    print("the class is: ", json.dumps(classes, indent=4))
    print("the asso is: ", json.dumps(associations, indent=4))

    # if len(associations) == 0:
    #     for _, value in classes.items():
    #         result = writeCls(value, result)

    # else:
    #     for cls1, cls2 in associations.items():
    #         result = writeCls(classes[cls1], result, 1,
    #                           classes[cls2["to"]],
    #                           cls2["type"])

    return result


# def writeCls(cls, result, level=1, cls2=None, asso=None):
#     # print(json.dumps(cls, indent=4))

#     rootElement = 0
#     if ("RootElement" in cls["profiles"]):
#         rootElement = int(cls["profiles"]["RootElement"]["@multiplicity"])

#     if (rootElement == 1):
#         result += "container"
#     elif (rootElement > 1):
#         result += "list"
#     else:
#         result += "grouping"

#     result += ''.join([" ", cls["name"], " ", "{\n"])

#     if (asso == "composite"):
#         result += "\t"*level
#         result = writeCls(cls2, result, level+1)
#     elif (asso == "shared"):
#         result += "\t"*level + "uses " + cls2["name"] + "\n"

#     for key, value in cls["attributes"].items():
#         print(key)
#         print(value)
#         unit = 0
#         OpenModelAttribute = {}

#         if ("OpenModelAttribute" in value):
#             OpenModelAttribute = value["OpenModelAttribute"]
#             unit = int(value["OpenModelAttribute"]["@unit"])

#         result += "\t"*level
#         if (unit <= 1):
#             result += "leaf"
#         elif (unit > 1):
#             result += "leaf-list"
#         result += ''.join([" ", key, " ", "{\n"])
#         result += ''.join(["\t\t"*level, "type",
#                           " ", value["type"], ";\n"])

#         if "@valueRange" in OpenModelAttribute:
#             valueRange = '""'
#             if OpenModelAttribute["@valueRange"] != "":
#                 valueRange = OpenModelAttribute["@valueRange"]
#             result += ''.join(["\t\t"*level,
#                               "valueRange", " ", valueRange, "\n"])

#         result += "\t"*level + "}\n"

#     result += "\t"*(level - 1) + "}" + "\n"

#     if (asso == "shared"):
#         result = writeCls(cls2, result, level)

#     return result
