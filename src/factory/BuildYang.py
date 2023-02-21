import xmltodict
from .classInfo import classInfo


class BuildYang:

    def __init__(self, path) -> None:

        self.Graph = []
        self.Record = {}
        self.ClassInfo = None
        self.ProfileInfo = None

        self.RenderStart = []

        self.indAttriRepo = []

        self.DataTypeRepo = []

        self.toXmlMode(path)
        self.findClasses()

    def toXmlMode(self, path):
        data_dict = {}

        with open(path) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())

        self.ClassInfo = data_dict["xmi:XMI"]["uml:Model"]
        del data_dict["xmi:XMI"]["uml:Model"]

        self.ProfileInfo = data_dict["xmi:XMI"]

    def findClasses(self):
        classes = self.ClassInfo["packagedElement"]
        if type(classes) is not list:
            classes = [classes]

        for cls in classes:

            if len(cls) < 3:
                '''
                this is some noisy class information
                normally created because there are 
                multiple deletions occured
                '''
                continue

            if cls["@xmi:type"] == "uml:Class" or cls["@xmi:type"] == "uml:DataType":

                clsYang = classInfo(cls["@name"], cls["@xmi:id"])
                if "ownedAttribute" in cls:

                    classes = clsYang.collectInfo(
                        cls["ownedAttribute"],
                        self.ProfileInfo)

                # if is datatype
                DA_result = False
                if cls["@xmi:type"] == "uml:DataType":
                    DA_result = self.DataTypeHandler(clsYang)

                    # the class is behind
                    if DA_result == False:
                        self.DataTypeRepo.append(clsYang)
                        break

                    else:
                        self.Record[clsYang.classId] = len(self.Record)
                        self.Graph.append(clsYang)
                        break

                self.Graph.append(clsYang)

                # post-processing
                classes = [*classes, *clsYang.post_process()]

                if len(classes) > 0:
                    for clss in classes:
                        self.Graph.append(clss)

                self.Record[cls["@xmi:id"]] = len(self.Record)

                if len(self.indAttriRepo) > 0:

                    for i in list(range(len(self.indAttriRepo))):
                        is_insert = self.indAttriHandler(self.indAttriRepo[i])
                        if is_insert is True:
                            self.indAttriRepo.pop(i)

                if len(self.DataTypeRepo) > 0:
                    for i in list(range(len(self.DataTypeRepo))):
                        is_insert = self.DataTypeHandler(self.DataTypeRepo[i])
                        if is_insert is True:
                            self.DataTypeRepo.pop(i)

            elif cls["@xmi:type"] == "uml:Enumeration":

                # process here
                Enum = {
                    "name": cls["@name"],
                    "to": cls["@xmi:id"],
                    "ownedLiteral": [],
                    "type": "enumeration"
                }

                if type(cls["ownedLiteral"]) is not list:
                    cls["ownedLiteral"] = [cls["ownedLiteral"]]

                for value in cls["ownedLiteral"]:
                    Enum["ownedLiteral"].append(value["@name"])

                is_insert = self.indAttriHandler(Enum)

                if is_insert is False:
                    self.indAttriRepo.append(Enum)

        print("done")

        self.findEntry()

    def findEntry(self):
        inorder_array = [0]*len(self.Graph)

        for node in self.Graph:
            if len(node.Associations) != 0:
                for nextNode in node.Associations:
                    nextNodeID = nextNode["to"]
                    nextNodeIdx = self.Record[nextNodeID]
                    inorder_array[nextNodeIdx] += 1

        # we take the first element that equals zero
        # as the entry
        # try:
        #     entryIdx = inorder_array.index(0)
        # except ValueError as e:
        #     raise Exception("cycle exisit in the array, all node > 0")

        for i in range(len(inorder_array)):
            if inorder_array[i] == 0:
                self.RenderStart.append(self.Graph[i].classId)

        # self.RenderStart = self.Graph[entryIdx].classId
        print("done")

    def indAttriHandler(self, indAttri):

        # there might be multiple of enum
        is_insert = False
        for node in self.Graph:
            if len(node.content["attributes"]) < 1:
                continue

            for attr in node.content["attributes"]:
                if type(attr["type"]) is not dict:

                    if attr["type"] == indAttri["to"]:

                        attr["value"] = indAttri
                        attr["type"] = indAttri["type"]

                        is_insert = True

        return is_insert

    def DataTypeHandler(self, dataType):

        # search in the graph
        # to check if the attribute
        is_find = False
        for node in self.Graph:
            if len(node.content["attributes"]) < 1:
                continue

            toRemoved = []
            for attr in node.content["attributes"]:

                if type(attr["type"]) is not dict:

                    if attr["type"] == dataType.classId:
                        is_find = True

                        new_cls = classInfo(attr["name"], attr["id"])

                        if attr["mul"] == "1..*":
                            new_cls.content["RootElement"] = "2"
                        if attr["mul"] == "1":
                            new_cls.content["RootElement"] = "1"

                        asso = {
                            "to": dataType.classId,
                            "type": "shared"
                        }
                        new_cls.Associations.append(asso)
                        new_cls.content["attributes"] = []

                        self.Record[attr["id"]] = len(self.Record)
                        self.Graph.append(new_cls)

                        asso = {
                            "to": new_cls.classId,
                            "type": "composed"
                        }
                        node.Associations.append(asso)

                        toRemoved.append(attr)

            if len(toRemoved) > 0:
                for remove in toRemoved:
                    for attr in node.content["attributes"]:
                        if attr["name"] == remove["name"]:
                            node.content["attributes"].remove(attr)
                            break

        return is_find
