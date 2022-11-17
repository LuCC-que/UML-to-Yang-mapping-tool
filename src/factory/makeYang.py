import xmltodict
import json
import re
from operator import itemgetter


class makeYangInJson:

    def __init__(self, filePath, cfg={}) -> None:
        self.filePath = filePath
        self.xmlModel = None
        self.profiles = None
        self.profileInfo = {}
        self.YangInJson = {}
        self.toXmlModel()
        self.toYangJson()

    def toXmlModel(self) -> None:
        with open(self.filePath) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())

        # take the xml element
        self.xmlModel = data_dict["xmi:XMI"]["uml:Model"]
        del data_dict["xmi:XMI"]["uml:Model"]

        # take the profile info
        self.profiles = data_dict["xmi:XMI"]

    def toYangJson(self) -> None:

        # collect all the profiles info first
        for key in self.profiles:
            if re.fullmatch(r'\b\w*_Profile:\w*\b', key):
                self.profileHandler(key, self.profiles[key])

        for key in self.xmlModel:
            if key == "packagedElement":
                self.elementHandler(self.xmlModel[key])

    def elementHandler(self, pkgElement) -> None:
        # print(json.dumps(elements, indent=4))
        if type(pkgElement) is dict:
            class_type = pkgElement["@xmi:type"]
            if class_type == "uml:Class":
                self.umlClassHandler(pkgElement)
            if class_type == "uml:Association":
                self.umlAssoHandler(pkgElement)

        elif type(pkgElement) is list:
            for element in pkgElement:
                self.elementHandler(element)
        else:
            raise Exception("Unknown type: pkgElement")

    def umlClassHandler(self, umlClass) -> None:
        # self.YangInJson[umlClass["@xmi:id"]] = {}
        print(json.dumps(umlClass, indent=4))
        _cls = {
            "name": umlClass["@name"],
            "profiles": [],
            "attributes": self.attributesHandler(umlClass["ownedAttribute"])
        }

        if umlClass["@xmi:id"] in self.profileInfo:
            _cls["profiles"] = self.profileInfo[umlClass["@xmi:id"]]

        self.YangInJson[umlClass["@xmi:id"]] = _cls
        print(json.dumps(self.YangInJson, indent=4))
        return

    def attributesHandler(self, attr):

        #! no implement yet
        return attr

    def umlAssoHandler(self, umlAsso) -> None:
        '''
        looking for association after we obtain the 
        comprehensive class information, which later
        on we can just simply connect them together
        '''
        #!unimplement
        print(json.dumps(umlAsso, indent=4))
        return

    def profileHandler(self, key, profiles) -> None:
        _, class_id, *item = profiles.values()

        if item == []:
            return

        [_, pType] = key.split(":")
        if class_id in profiles:
            self.profileInfo[class_id][pType] = item
        else:
            self.profileInfo[class_id] = {pType: item}
        print(json.dumps(self.profileInfo, indent=4))


if __name__ == "__main__":
    import pathlib
    path = pathlib \
        .Path().resolve()\
        .joinpath("..").joinpath("resources")\
        .joinpath("container1.uml")\

    mYj = makeYangInJson(path)
    # Json = mYj.xmlModel
    # pf = mYj.profileInfo
    # print(json.dumps(Json, indent=4))
    # print(json.dumps(pf, indent=4))
