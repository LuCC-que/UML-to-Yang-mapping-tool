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

        count = 0
        for cls in classes:

            if len(cls) < 3:
                '''
                this is some noisy class information
                normally created because there are 
                multiple deletions occured
                '''
                continue

            if cls["@xmi:type"] == "uml:Class":

                clsYang = classInfo(cls["@name"], cls["@xmi:id"])
                if "ownedAttribute" in cls:

                    root = clsYang.collectInfo(
                        cls["ownedAttribute"],
                        self.ProfileInfo)

                self.Graph.append(clsYang)

                if root is not None:
                    self.Graph.append(root)

                self.Record[cls["@xmi:id"]] = count
                count += 1

                if len(self.indAttriRepo) > 0:

                    for i in list(range(len(self.indAttriRepo))):
                        is_insert = self.indAttriHandler(self.indAttriRepo[i])
                        if is_insert is True:
                            self.indAttriRepo.pop(i)

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
                    nextNodeName = nextNode["to"]
                    nextNodeIdx = self.Record[nextNodeName]
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
