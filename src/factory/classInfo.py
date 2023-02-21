from re import split
from itertools import zip_longest


class classInfo:
    def __init__(self, name, id) -> None:
        self.className = name
        self.classId = id
        self.Associations = []
        self.content = {}

    def collectInfo(self, attribute, profiles):

        additional_classes = []

        if type(attribute) is list:
            for attribute in attribute:
                self.collectInfo(attribute, profiles)

        else:
            if "@association" in attribute:
                # association case
                asso = {"to": attribute["@type"],
                        "type": attribute["@aggregation"]}
                self.Associations.append(asso)
            else:

                clsAttr = {"name": attribute["@name"],
                           "id": attribute["@xmi:id"],
                           "type": "undefined",
                           "mul": "0..1",
                           "defaultValue": None}

                if "type" in attribute:
                    if attribute["type"]["@xmi:type"] == "uml:PrimitiveType":
                        clsAttr["type"] = attribute["type"]["@href"].split(
                            "#")[-1]

                else:
                    clsAttr["type"] = attribute["@type"]

                if "defaultValue" in attribute:
                    clsAttr["defaultValue"] = attribute["defaultValue"]["@value"]

                '''
                [0..1] => no mapping needed; is leaf 
                default 
                [1] => mandatory substatement = true 
                leaf-list only: 
                “min-elements” and “max-elements” 
                substatements 
                [0..x] => no mapping needed; is leaf-list 
                default 
                [1..x] => min-elements substatement = 1 
                [0..3] => max-elements substatement = 3
                '''
                if "ownedComment" in attribute:
                    if "body" in attribute["ownedComment"]:

                        # the first is multiplacity
                        # the second is uniqueness
                        tags = ["mul", "unique"]
                        string = attribute["ownedComment"]["body"]
                        values = split("[\r\n]+", string)

                        # assign to the clsAttribute
                        for tag, value in zip_longest(tags, values):
                            if tag is None or value is None:
                                break
                            if tag == "unique":
                                unq_cls = classInfo(
                                    self.className, self.classId + "__")
                                asso = {"to": self.classId,
                                        "type": "shared"}
                                unq_cls.Associations.append(asso)
                                unq_cls.content["RootElement"] = "2"

                                unq_cls_key = {"name": attribute["@name"],
                                               "id": attribute["@xmi:id"] + "_",
                                               "type": "key",
                                               }

                                unq_cls_uni = {"name": attribute["@name"],
                                               "id": attribute["@xmi:id"] + "_q",
                                               "type": "unique",
                                               }
                                unq_cls.content["attributes"] = [
                                    unq_cls_key, unq_cls_uni]

                                additional_classes.append(unq_cls)
                                continue
                            clsAttr[tag] = value

                if "attributes" in self.content:
                    self.content["attributes"].append(clsAttr)
                else:
                    self.content["attributes"] = [clsAttr]

        root = None

        # profile
        for key, value in profiles.items():

            if key == "OpenInterfaceModel_Profile:RootElement":

                if type(value) is not list:
                    value = [value]
                # this might be additional root
                for pObj in value:

                    if len(pObj) < 3:
                        continue

                    if pObj["@base_Class"] == self.classId:
                        if "@name" not in pObj:
                            self.content["RootElement"] = pObj["@multiplicity"]

                        # root element class
                        else:
                            root = classInfo(pObj["@name"], self.classId + "_")

                            asso = {"to": self.classId,
                                    "type": "shared"}
                            root.Associations.append(asso)
                            root.content["RootElement"] = pObj["@multiplicity"]

                            if "@description" in pObj:
                                root.content["presence"] = pObj["@description"]

                            additional_classes.append(root)

            if key == "OpenModel_Profile:OpenModelAttribute":
                for attrObj in value:

                    if len(attrObj) < 3 or len(value) < 3:
                        continue

                    else:

                        for attr in self.content["attributes"]:
                            if attr["id"] == attrObj["@base_StructuralFeature"]:
                                keys_to_append = list(attrObj.keys())[2:]

                                # append all value beside first two into
                                # attr
                                for key in keys_to_append:
                                    attr[key] = attrObj[key]

        return additional_classes
