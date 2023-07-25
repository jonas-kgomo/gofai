sig_name = {"\\mathbb{N}" : "Natural",
             "\\mathbb{Z}" : "Integer",
             "\\mathbb{Q}" : "Rational",
             "\\mathbb{R}" : "Real",
             "\\mathbb{C}" : "Complex",
             "\\N" : "Natural",
             "\\Z" : "Integer",
             "\\Q" : "Rational",
             "\\R" : "Real",
             "\\C" : "Complex"}

sig_repr = {"Natural" : "\\mathbb{N}",
              "Integer" : "\\mathbb{Z}",
              "Rational" : "\\mathbb{Q}",
              "Real"    : "\\mathbb{R}",
              "Complex" : "\\mathbb{C}"}

sig_str = {"Natural" : "\u2115",
              "Integer" : "\u2124",
              "Rational" : "\u211a",
              "Real"    : "\u211d",
              "Complex" : "\u2102"}

class Constraint:
    pass

class Subset(Constraint):
    def __init__(self, universe):
        self.sort = universe

    def __repr__(self):
        return "Set("+repr(self.universe)+")"
            
    def __str__(self):
        return "Set("+str(self.universe)+")"

class Function(Constraint):
    def __init__(self, domain, codomain):
         self.domain = domain
         self.codomain = codomain
         self.sort = TupleSort([domain.sort, codomain.sort])

    def __repr__(self):
         if self.domain == None:
             return repr(self.codomain)
         else:
             return repr(self.domain)+" \\to "+repr(self.codomain)

    def __str__(self):
         if self.domain == None:
             return str(self.codomain)
         else:
             return str(self.domain)+" \u2192 "+str(self.codomain)

class SetTuple(Constraint):
    def __init__(self, sets):
         self.sets = sets
         self.sort = TupleSort([v.sort for v in sets])

    def __repr__(self):
         n = len(self.sets)
         if n == 0:
             return "()"
         else:
             return "("+', '.join([repr(self.sets[i]) for i in range(0, n)])+")"
   
    def __str__(self):
         n = len(self.sets)
         if n == 0:
             return "()"
         else:
             return "("+', '.join([str(self.sets[i]) for i in range(0, n)])+")"

class SetSort(Constraint):
    def __init__(self):
        self.sort = self

    def __repr__(self):
        return "Set"

    def __str__(self):
        return "Set"

class Universum(SetSort):
    def __init__(self):
        self.sort = self

    def __repr__(self):
        return "\\mathcal{U}"

    def __str__(self):
        return "\u03a9"

class NumberSort(Constraint):
    def __init__(self, name):
        self._name = sig_name[name]
        self.sort = self

    def __repr__(self):
        return sig_repr[self._name]

    def __str__(self):
        return sig_str[self._name]

    def name(self):
        return self._name

class TupleSort(Constraint):
    def __init__(self, sets):
         self.sets = sets
         self.sort = self

    def __repr__(self):
         n = len(self.sets)
         if n == 0:
             return "()"
         else:
             return "("+', '.join([repr(self.sets[i]) for i in range(0, n)])+")"
   
    def __str__(self):
         n = len(self.sets)
         if n == 0:
             return "()"
         else:
             return "("+', '.join([str(self.sets[i]) for i in range(0, n)])+")"

class PredSort(Constraint):
    def __init__(self):
       self.sort = self

    def __repr__(self):
       return "Pred"

    def __str__(self):
       return "Pred"