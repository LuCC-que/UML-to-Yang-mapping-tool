class classInfo:
    def __init__(self, name, classContent) -> None:
        self.Associations = []
        self.classContent = classContent
        self.className = name

    def addAsso(self, name):
        self.Associations.append(name)
