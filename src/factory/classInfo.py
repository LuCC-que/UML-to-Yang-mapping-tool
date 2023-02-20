class classInfo:
    def __init__(self, name, id) -> None:
        self.className = name
        self.classId = id
        self.Associations = []
        self.content = {}

    def collectInfo(self, attribute, profiles):

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
                           "type": "undefined",
                           "mul": "0..1",
                           "defaultValue": None}

                if "type" in attribute:
                    if attribute["type"]["@xmi:type"] == "uml:PrimitiveType":
                        clsAttr["type"] = attribute["type"]["@href"].split(
                            "#")[-1]

                # if type(attribute["type"]) is dict:

                #     if attribute["type"]["@xmi:type"] == "uml:PrimitiveType":
                #         clsAttr["type"] = attribute["type"]["@href"].split(
                #             "#")[-1]

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
                        clsAttr["mul"] = attribute["ownedComment"]["body"]

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

                        else:
                            root = classInfo(pObj["@name"], self.classId + "_")

                            asso = {"to": self.classId,
                                    "type": "shared"}
                            root.Associations.append(asso)
                            root.content["RootElement"] = pObj["@multiplicity"]

                            if "@description" in pObj:
                                root.content["presence"] = pObj["@description"]

        return root
