import json
from .makeYang import makeYangInJson


def writeYang(classes, associations):
    result = ''
    print(json.dumps(classes, indent=4))

    if len(associations) == 0:
        for _, value in classes.items():
            result = writeCls(value, result)

    return result


def writeCls(cls, result):
    # print(json.dumps(cls, indent=4))

    rootElement = 0
    if ("RootElement" in cls["profiles"]):
        rootElement = int(cls["profiles"]["RootElement"]["@multiplicity"])

    if (rootElement == 1):
        result += "container"
    elif (rootElement > 1):
        result += "list"
    else:
        result += "grouping"

    result += ''.join([" ", cls["name"], " ", "{\n"])

    for key, value in cls["attributes"].items():
        print(key)
        print(value)
        unit = 0
        if ("@unit" in value):
            unit = int(value["@unit"])

        result += "\t"
        if (unit <= 1):
            result += "leaf"
        elif (unit > 1):
            result += "leaf-list"
        result += ''.join([" ", key, " ", "{\n"])
        result += ''.join(["\t\t", " ", "type", " ", value["type"], ";\n"])
        result += "\t}\n"

    result += "}"
    return result
