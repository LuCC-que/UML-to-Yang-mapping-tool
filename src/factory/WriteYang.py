import json
import re


class WriteYang:

    def __init__(self, renderArray, roots) -> None:

        self.renderMap = {}
        self.roots = roots
        self.pending = []
        self.output = ""
        self._config(renderArray)

        while (len(roots) > 0):
            root = roots.pop()
            self.writeYang(root)

    def _config(self, renderArray):

        for cls in renderArray:
            self.renderMap[cls.classId] = cls

        print("done")

    def writeYang(self, root, level=1, top=True):

        # start writting yang
        self.output += "\t" * (level - 1)
        cls = self.renderMap[root]

        if "RootElement" not in cls.content:
            self.output += "grouping"
        elif cls.content["RootElement"] == "1":

            self.output += "container"

        elif cls.content["RootElement"] == "0":
            self.output += "grouping"

        else:
            self.output += "list"

        self.output += " " + cls.className + " {"
        self.output += "\n"

        # render the attributes first
        if "attributes" in cls.content:
            attributes = cls.content["attributes"]
            for attribute in attributes:

                if attribute["type"] == "enumeration":

                    self.output += "\t" * level
                    self.output += "leaf "
                    self.output += attribute["name"] + "{"

                    self.output += "\n"
                    self.output += "\t" * (level + 1)
                    self.output += "type enumeration {"

                    for value in attribute["value"]["ownedLiteral"]:
                        self.output += "\n"
                        self.output += "\t" * (level + 2)
                        self.output += "enum "
                        self.output += value
                        self.output += ";"

                    self.output += "\n"
                    self.output += "\t" * (level + 1)
                    self.output += "}"

                    self.additionalValues(attribute, level)

                    self.output += "\n"
                    self.output += "\t" * level
                    self.output += "}"

                else:

                    self.output += "\t" * level

                    if attribute["mul"] == "0..1" or attribute["mul"] == "1":
                        self.output += "leaf "

                    else:
                        self.output += "leaf-list "

                    self.output += attribute["name"] + "{"
                    self.output += "\n"
                    self.output += "\t" * (level + 1)
                    self.output += "type " + attribute["type"] + ";"

                    if attribute["mul"] == "1":
                        self.output += "\n"
                        self.output += "\t" * (level + 1)
                        self.output += "mandatory true" + ";"

                    elif re.match(r"^.+\.\..+$", attribute["mul"]):
                        parts = attribute["mul"].split("..")
                        minVal, maxVal = parts
                        if minVal.isdigit() and minVal != "0":
                            self.output += "\n"
                            self.output += "\t" * (level + 1)
                            self.output += "min-elements " + minVal + ";"
                        if maxVal.isdigit() and maxVal != "1":
                            self.output += "\n"
                            self.output += "\t" * (level + 1)
                            self.output += "max-elements " + maxVal + ";"

                    # checking additional value here
                    self.additionalValues(attribute, level)

                    self.output += "\n" + "\t" * level + "}"

                self.output += "\n"

        if "presence" in cls.content:
            self.output += "\t" * level
            self.output += "presence "
            self.output += '"' + cls.content["presence"] + '"'
            self.output += ";"
            self.output += "\n"

        if len(cls.Associations) > 0:

            assotiations = cls.Associations
            for assotiation in assotiations:
                targetId = assotiation["to"]
                if assotiation["type"] == 'shared':
                    self.output += "\t" * level
                    self.output += "uses "
                    self.output += self.renderMap[targetId].className
                    self.output += ";"
                    self.output += "\n"

                    if targetId not in self.pending:
                        self.pending.append(targetId)
                # may be repeatly rendering
                else:
                    self.writeYang(targetId, level + 1, False)

        self.output += "\t" * (level - 1) + "}"
        self.output += "\n"

        if cls.classId in self.roots:
            self.roots.remove(cls.classId)

        # if cls.classId in self.renderMap:
        #     del self.renderMap[cls.classId]

        if top == True:
            while (len(self.pending) > 0):
                cls = self.pending.pop()
                self.writeYang(cls, level, False)

            # for cls in self.pending:
            #     self.writeYang(cls, level, False)

        print("debug")

    def additionalValues(self, attribute, level):
        if attribute["defaultValue"] != None:
            self.output += "\n"
            self.output += "\t" * (level + 1)
            self.output += "default "
            self.output += attribute["defaultValue"]
            self.output += ";"
        if "@isInvariant" in attribute:
            self.output += "\n"
            self.output += "\t" * (level + 1)
            self.output += "config "
            self.output += "false"
            self.output += ";"
