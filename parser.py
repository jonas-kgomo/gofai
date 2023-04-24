from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor, Node
from pprint import pprint
from nodes import AddNode, AndNode, NaturalNode, DiffNode, DivNode, \
     ElemNode, EqNode, ExistsNode, ExpNode, FnNode, ForallNode, GeqNode, \
     GtNode, IffNode, ImpliesNode, IntersectNode, LeqNode, LtNode, MulNode, \
     NotNode, NeqNode, OrNode, SubNode, SubsetNode, SubseteqNode, SupsetNode, \
     SupseteqNode, UnionNode, VarNode, BoolNode
from type import NumberType

# TODO: add \sum, \integral, \partial, derivative, subscripts (incl. braces)

statement = Grammar(
    r"""
    statement = existential / universal / neg_expression
    existential = "\\exists" space typed_var space statement?
    universal = "\\forall" space typed_var space statement?
    typed_var = var space ":" space number_type
    number_type = "\\mathbb{N}" / "\\mathbb{Z}" / "\\mathbb{Q}" / "\\mathbb{R}" / "\\mathbb{C}"
    neg_expression = ("\\neg" space)? expression
    expression = (and_expression space ("\\implies" / "\\leftrightarrow") space)* and_expression
    and_expression = (relation space ("\\wedge" / "\\vee") space)* relation
    relation = bool / elem_relation / subset_relation / alg_relation
    subset_relation = (set_expression space ("\\subseteq" / "\\subset" / "\\supseteq" / "\\supset") space)+ set_expression
    elem_relation = add_expression space "\\in" space set_expression
    set_expression = set_diff / set_union
    set_diff = set_union space "\\setminus" space set_union
    set_union = (set space ("\\cup" / "\\cap") space)* set
    set = set_paren / var
    set_paren = "(" set_expression ")"
    alg_relation = (add_expression space ("<" / ">" / "\\leq" / "\\geq" / "=" / "\\neq") space)? add_expression
    add_expression = (mult_expression space ("+" / "-") space)* mult_expression
    mult_expression = mult_expression1 / mult_expression2
    mult_expression1 = natural mult_expression2
    mult_expression2 = (exp_expression space ("*" / "/") space)* exp_expression
    exp_expression = terminal (space "^" space terminal)*
    terminal = paren_expression / fn_application / natural / var
    bool = ("True" / "False")
    paren_expression = "(" neg_expression ")"
    fn_application = name "(" (add_expression space "," space)* add_expression ")"
    natural = ~"[1-9][0-9]*" / ~"0"
    name = ~"[A-Za-z][a-z0-9_]*"
    var = ~"[A-Za-z_][A-Za-z0-9_]*" / "\\alpha" / "\\beta" / "\\gamma" / "\\delta" / "\\epsilon" / "\\zeta" / "\\eta" / "\\kappa" / "\\lambda" / "\\mu" / "\\nu" / "\\psi" / "\\rho" / "\\sigma" / "\\chi" / "\\omega" / "\\tau" / "\\psi" / "\\phi"
    space = ~"\s*"
    """)

node_dict = {
    "+" : AddNode,
    "-" : SubNode,
    "*" : MulNode,
    "/" : DivNode,
    "<" : LtNode,
    ">" : GtNode,
    "\\leq" : LeqNode,
    "\\geq" : GeqNode,
    "=" : EqNode,
    "\\neq" : NeqNode,
    "\\wedge" : AndNode,
    "\\vee" : OrNode,
    "\\implies" : ImpliesNode,
    "\\leftrightarrow" : IffNode,
    "\\cup" : UnionNode,
    "\\cap" : IntersectNode,
    "\\subset" : SubsetNode,
    "\\subseteq" : SubseteqNode,
    "\\supset" : SupsetNode,
    "\\supseteq" : SupseteqNode
}

def left_rec(L, v):
    """Turn a list L and final value v into a tree. Each element of the list
    will contain 4 items [v, _, op, _]. If L is empty only v is returned.
    """
    if hasattr(L, '__getitem__') and len(L) > 0:
        x = L.pop()
        Node = node_dict[x[2][0].text]
        return Node(left_rec(L, x[0]), v)
    else:
        return v

class StatementVisitor(NodeVisitor):
    def generic_visit(self, node, visited_children):
        """ Generic visit method. """
        return visited_children or node
    def visit_statement(self, node, visited_children):
        return visited_children[0]
    def visit_universal(self, node, visited_children):
        expr = visited_children[4]
        if expr:
            return ForallNode(visited_children[2], expr[0])
        else:
            return ForallNode(visited_children[2], None)
    def visit_existential(self, node, visited_children):
        expr = visited_children[4]
        if isinstance(expr, Node):
            return ExistsNode(visited_children[2], None)
        else:
            return ExistsNode(visited_children[2], expr[0])
    def visit_typed_var(self, node, visited_children):
        visited_children[0].type = visited_children[4]
        return visited_children[0]
    def visit_number_type(self, node, visited_children):
        return NumberType(node.text)
    def visit_relation(self, node, visited_children):
        return visited_children[0]
    def visit_subset_relation(self, node, visited_children):
        expr = visited_children[1]
        return left_rec(visited_children[0], expr)
    def visit_set_expression(self, node, visited_children):
        return visited_children[0]
    def visit_elem_relation(self, node, visited_children):
        return ElemNode(visited_children[0], visited_children[4])
    def visit_set_diff(self, node, visited_children):
        return DiffNode(visited_children[0], visited_children[4])
    def visit_set_union(self, node, visited_children):
        expr = visited_children[1]
        return left_rec(visited_children[0], expr)
    def visit_set(self, node, visited_children):
        return visited_children[0]
    def visit_set_paren(self, node, visited_children):
        return visited_children[1]
    def visit_neg_expression(self, node, visited_children):
        L = visited_children[0]
        expr = visited_children[1]
        if hasattr(L, '__getitem__'):
            return NotNode(expr)
        else:
            return expr
    def visit_expression(self, node, visited_children):
        expr = visited_children[1]
        return left_rec(visited_children[0], expr)
    def visit_and_expression(self, node, visited_children):
        expr = visited_children[1]
        return left_rec(visited_children[0], expr)
    def visit_alg_relation(self, node, visited_children):
        expr = visited_children[1]
        return left_rec(visited_children[0], expr)
    def visit_add_expression(self, node, visited_children):
        expr = visited_children[1]
        return left_rec(visited_children[0], expr)
    def visit_mult_expression(self, node, visited_children):
        return visited_children[0]
    def visit_mult_expression1(self, node, visited_children):
        return MulNode(visited_children[0], visited_children[1])
    def visit_mult_expression2(self, node, visited_children):
        expr = visited_children[1]
        return left_rec(visited_children[0], expr)
    def visit_var(self, node, visited_children):
        return VarNode(node.text)
    def visit_terminal(self, node, visited_children):
        return visited_children[0]
    def visit_paren_expression(self, node, visited_children):
        return visited_children[1]
    def visit_fn_application(self, node, visited_children):
        args = []
        for v in visited_children[2]:
            args.append(v[0])
        args.append(visited_children[3])
        return FnNode(visited_children[0], args)
    def visit_name(self, node, visited_children):
        return node.text
    def visit_exp_expression(self, node, visited_children):
        res = visited_children[0]
        for v in visited_children[1]:
            res = ExpNode(res, v[3])
        return res
    def visit_natural(self, node, visited_children):
        return NaturalNode(node.text)
    def visit_bool(self, node, visited_children):
        value = True if node.text == "True" else False
        return BoolNode(value)
