import xmltodict
import copy
from .classInfo import classInfo
from random import uniform


class BuildYang:

    def __init__(self, path) -> None:

        self.Graph = []
        self.Record = {}
        self.ClassInfo = None
        self.ProfileInfo = None

        self.RenderStart = []

        self.indAttriRepo = []

        self.DataTypeRepo = []

        self.constraint = []

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

            elif cls["@xmi:type"] == "uml:Constraint":
                self.constraint.append(cls)

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

        self.classPostProcessing()
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

    def classPostProcessing(self):

        if len(self.constraint) > 0:
            for cons in self.constraint:
                if cons["specification"]["@value"] == "xor":
                    self.XORconstraintHandler(cons)

        # a general post processing of
        # assotiations
        for node in self.Graph:
            if len(node.Associations) < 1:
                continue

            asso_index = 0
            for asso in node.Associations:

                for to_node in self.Graph:
                    if to_node.classId == asso["to"]:
                        if to_node.status == "raw":

                            _, new_asso = self.assoHandler(
                                to_node, asso)

                            if new_asso != None:
                                node.Associations[asso_index] = new_asso
            asso_index += 1

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

    def assoHandler(self, node, asso):
        if len(asso) < 3:
            return None, None

        new_node = None
        rootMul = None
        new_asso = None
        if asso["mul"] == "*" or asso["mul"] == "0..*":
            # list
            rootMul = "2"
        elif asso["mul"] == "1":
            # container
            rootMul = "1"
        else:
            # grouping
            rootMul = "0"

        if node.status == "raw":
            node.content["RootElement"] = rootMul
            node.status == "processed"

        else:
            new_node = node.copy()
            new_node.classId += asso["mul"] + "_" + uniform(0.0, 100.0)
            new_node["RootElement"] = rootMul
            new_node.status == "processed"

            self.Graph.append(new_node)
            self.Record[new_node.classId] = len(self.Record)

            new_asso = {"to": new_node.classId, "type": asso["type"]}
        print(node.className, asso["mul"])
        return new_node, new_asso

    def XORconstraintHandler(self, constraint):

        # find the class it belongs to

        rootNode = None
        AssoList = {}

        for consELe in constraint["constrainedElement"]:
            if consELe["@xmi:type"] == "uml:Class":
                for node in self.Graph:
                    if node.classId == consELe["@href"][1:]:
                        rootNode = node

            if consELe["@xmi:type"] == "uml:Association":

                for toNode in self.Graph:
                    for toNode_asso in toNode.Associations:
                        if toNode_asso["assoId"] == consELe["@href"][1:]:

                            for asso_node in self.Graph:
                                if asso_node.classId == toNode_asso["to"]:
                                    AssoList[asso_node.classId] = asso_node
        choicesNode = classInfo(
            constraint["@name"], "choices_" + str(uniform(0.0, 100.0)))
        choicesNode.status = "choice-constraint"

        AssotoRemove = []
        asso_index = 0
        case_index = 1
        for asso in rootNode.Associations:
            if asso["to"] in AssoList:
                AssotoRemove.append(asso_index)
                caseNode = classInfo(
                    "alt-" + str(case_index),
                    "case_"
                    + str(case_index)
                    + str(uniform(0.0, 100.0)))

                newNode = copy.deepcopy(AssoList[asso["to"]])

                newNode.classId += "case_" + \
                    str(case_index) + str(uniform(0.0, 100.0))

                caseAsso = {"to": asso["to"], "type": "shared"}
                newNode.Associations.append(caseAsso)

                choicesAsso = {"to": caseNode.classId,
                               "type": "composed"}

                choicesNode.Associations.append(choicesAsso)

                self.Graph.append(caseNode)
                self.Graph.append(newNode)

                self.Record[caseNode.classId] = len(self.Record)
                self.Record[newNode.classId] = len(self.Record)

                del newNode.content["attributes"]

        self.Graph.append(choicesNode)
        self.Record[choicesNode.classId] = len(self.Record)

        for assoidx in AssotoRemove:
            rootNode.Associations.pop(assoidx)

        return
