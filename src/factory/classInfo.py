from re import split
from itertools import zip_longest


class classInfo:
    def __init__(self, name, id) -> None:
        self.className = name
        self.classId = id
        self.Associations = []
        self.content = {}
        self.status = "raw"
        self.contain_uniqueSet = False

    def collectInfo(self, attribute, profiles):

        additional_classes = []

        if type(attribute) is list:
            for attribute in attribute:
                self.collectInfo(attribute, profiles)

        else:
            if "@association" in attribute:
                # association case
                asso = {"to": attribute["@type"],
                        "type": attribute["@aggregation"],
                        "assoId": attribute["@association"]}
                if "lowerValue" not in attribute and "upperValue" not in attribute:
                    asso["mul"] = "1"

                elif "lowerValue" not in attribute and "upperValue" in attribute:
                    _, upper = self.findlu(None, attribute["upperValue"])
                    asso["mul"] = upper

                elif "lowerValue" in attribute and "upperValue" in attribute:

                    lower, upper = self.findlu(
                        attribute["lowerValue"], attribute["upperValue"])

                    asso["mul"] = lower + \
                        ".." + upper

                elif "lowerValue" in attribute and "upperValue" not in attribute:
                    lower, _ = self.findlu(attribute["lowerValue"], None)
                    asso["mul"] = lower

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
                if "lowerValue" not in attribute and "upperValue" not in attribute:

                    clsAttr["mul"] = "1"

                elif "lowerValue" not in attribute and "upperValue" in attribute:
                    _, upper = self.findlu(None, attribute["upperValue"])
                    clsAttr["mul"] = upper

                elif "lowerValue" in attribute and "upperValue" in attribute:

                    lower, upper = self.findlu(
                        attribute["lowerValue"], attribute["upperValue"])

                    clsAttr["mul"] = lower + \
                        ".." + upper

                elif "lowerValue" in attribute and "upperValue" not in attribute:
                    lower, _ = self.findlu(attribute["lowerValue"], None)
                    clsAttr["mul"] = lower

                # RMOVED

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
                                    if key == "uniqueSet":
                                        self.contain_uniqueSet = True
                                    attr[key] = attrObj[key]

        return additional_classes

    def post_process(self):
        classes = []
        if self.contain_uniqueSet == True:
            classes = [*classes, self.unique_set()]

        return classes

    def unique_set(self):
        unq_cls = classInfo(self.className, self.classId + "-_-")
        asso = {"to": self.classId, "type": "shared"}
        unq_cls.Associations.append(asso)
        unq_cls.content["RootElement"] = "2"

        partOfObject = {"name": "none",
                        "id":  "_",
                        "type": "key",
                        }
        unq_cls.content["attributes"] = []

        unique_list = []
        for attr in self.content["attributes"]:
            if "uniqueSet" in attr:
                if type(attr["uniqueSet"]) is not list:
                    attr["uniqueSet"] = [attr["uniqueSet"]]

                for index in attr["uniqueSet"]:
                    if len(unique_list) < int(index):
                        unique_list.append(attr["name"])
                    else:
                        unique_list[int(index) - 1] += " " + attr["name"]

            if "@partOfObjectKey" in attr:
                if attr["@partOfObjectKey"] == "1":
                    partOfObject["name"] = attr["name"]

        unq_cls.content["attributes"].append(partOfObject)

        for unique_attr in unique_list:

            unq_cls_uni = {"name": unique_attr,
                           "id": unique_attr + "_q",
                           "type": "unique",
                           }
            unq_cls.content["attributes"].append(unq_cls_uni)

        return unq_cls

    def findlu(self, lowerDict, upperDict):

        lower = None
        upper = None

        if lowerDict != None:
            if len(lowerDict) < 3:
                lower = "0"

            else:
                lower = lowerDict["@value"]

        if upperDict != None:
            upper = upperDict["@value"]

        return lower, upper
