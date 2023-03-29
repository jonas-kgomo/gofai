type_name = {"\\mathbb{N}" : "Natural",
             "\\mathbb{Z}" : "Integer",
             "\\mathbb{R}" : "Real",
             "\\mathbb{C}" : "Complex"}

type_repr = {"Natural" : "\\mathbb{N}",
              "Integer" : "\\mathbb{Z}",
              "Real"    : "\\mathbb{R}",
              "Complex" : "\\mathbb{C}"}

type_str = {"Natural" : "\u2115",
              "Integer" : "\u2124",
              "Real"    : "\u211d",
              "Complex" : "\u2102"}

class NumberType:
    def __init__(self, name):
        self.name = type_name[name]

    def __repr__(self):
        return type_repr[self.name]

    def __str__(self):
        return type_str[self.name]
