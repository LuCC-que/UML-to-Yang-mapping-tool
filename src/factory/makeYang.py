import xmltodict
import json
import re
import pathlib
from operator import itemgetter


class makeYangInJson:

    def __init__(self, filePath=None, xml=None, cfg={}) -> None:
        self.filePath = filePath
        self.xml = xml

        if (self.filePath == None and self.xml == None):
            raise Exception("No availble xml file")
        elif ((self.filePath != None and self.xml != None)):
            raise Exception("Two different files")

        self.xmlModel = None
        self.profiles = None
        self.profileInfo = {}
        self.Classes = {}
        self.Associations = {}
        self.toXmlModel()
        self.toGrappingInfo()

    def toXmlModel(self) -> None:
        data_dict = {}
        if (self.filePath != None):
            with open(self.filePath) as xml_file:
                data_dict = xmltodict.parse(xml_file.read())
        else:
            data_dict = xmltodict.parse(self.xml)

        # print(json.dumps(data_dict, indent=4))

        # take the xml element
        self.xmlModel = data_dict["xmi:XMI"]["uml:Model"]
        del data_dict["xmi:XMI"]["uml:Model"]

        # take the profile info
        self.profiles = data_dict["xmi:XMI"]

    def toGrappingInfo(self) -> None:

        # collect all the profiles info first
        for key in self.profiles:
            if re.fullmatch(r'\b\w*_Profile:\w*\b', key):
                self.profileHandler(key, self.profiles[key])
        # print(json.dumps(self.profileInfo, indent=4))

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
        # self.Class[umlClass["@xmi:id"]] = {}
        # print(json.dumps(umlClass, indent=4))
        _cls = {
            "name": umlClass["@name"],
            "profiles": [],
            "attributes": self.attributesHandler(umlClass["ownedAttribute"], umlClass["@xmi:id"], {})
        }

        if umlClass["@xmi:id"] in self.profileInfo:
            _cls["profiles"] = self.profileInfo[umlClass["@xmi:id"]]

        self.Classes[umlClass["@xmi:id"]] = _cls
        # print(json.dumps(self.Class, indent=4))
        return

    def attributesHandler(self, attrs, cur_id, attrsDist={}) -> dict:
        if type(attrs) is dict:
            attr_id = attrs["@xmi:id"]

            if attr_id in self.profileInfo:
                profile = self.profileInfo[attr_id]

                # assign the profile
                attrsDist[attrs["@name"]] = profile

                # assign the name
                [_, tp] = attrs["type"]["@href"].split("#")
                attrsDist[attrs["@name"]]["type"] = tp

            elif "@association" in attrs:
                self.Associations[cur_id] = {
                    "type": attrs["@aggregation"], "to": attrs["@type"]}

            return attrsDist

        for attr in attrs:
            attrsDist = self.attributesHandler(attr, cur_id, attrsDist)

        return attrsDist

    def umlAssoHandler(self, umlAsso) -> None:
        '''
        looking for association after we obtain the 
        comprehensive class information, which later
        on we can just simply connect them together
        '''
        #!unimplement
        # print(json.dumps(umlAsso, indent=4))
        return

    def profileHandler(self, key, profiles) -> None:
        if type(profiles) is dict:
            _, class_id, *items = profiles.values()
            _, _, *keys = profiles.keys()

            if keys == []:
                return

            print(profiles)
            [_, pType] = key.split(":")
            for key, item in zip(keys, items):
                if class_id in self.profileInfo:
                    print(key)
                    if pType not in self.profileInfo[class_id]:
                        self.profileInfo[class_id][pType] = {key: item}
                    else:
                        self.profileInfo[class_id][pType] = {
                            **self.profileInfo[class_id][pType], key: item}
                else:
                    self.profileInfo[class_id] = {pType: {key: item}}

            return

        elif type(profiles) is list:
            for profile in profiles:
                self.profileHandler(key, profile)
