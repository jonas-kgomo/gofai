from copy import deepcopy
from nodes import ForallNode, ExistsNode, ImpliesNode, VarNode, EqNode, \
     NeqNode, LtNode, GtNode, LeqNode, GeqNode, OrNode, AndNode, NotNode, \
     FnNode, LRNode
from unification import unify, subst
from editor import edit

def new_result(screen, tl):
    tlist0 = tl.tlist0
    tlist1 = tl.tlist1
    tlist2 = tl.tlist2
    pad0 = screen.pad0.pad
    pad1 = screen.pad1.pad
    pad2 = screen.pad2.pad
    tlist0.data = []
    pad0[0] = ''
    n = len(tlist1.data)
    for i in range(0, n):
        del tlist1.data[n - i - 1]
        pad1[i] = ''
    n = len(tlist2.data)
    for i in range(0, n):
        del tlist2.data[n - i - 1]
        pad2[i] = ''
    screen.pad2.refresh()
    screen.pad1.refresh()
    screen.pad0.refresh()
    screen.focus = screen.pad0
    tl.focus = tl.tlist0

def library_export(screen, tl):
    library = open("library.dat", "a")
    title = edit(screen, "Title: ", 7)
    tags = edit(screen, "Tags: ", 6)
    library.write("\n")
    library.write(title+"\n")
    library.write(tags+"\n")
    tlist0 = tl.tlist0.data
    tlist1 = tl.tlist1.data
    tlist2 = tl.tlist2.data
    if tlist0:
        library.write(repr(tlist0[0])+"\n")
    library.write("------------------------------\n")
    for hyp in tlist1:
        library.write(repr(hyp)+"\n")
    library.write("------------------------------\n")
    for tar in tlist2:
        library.write(repr(tar)+"\n")
    library.close()
    screen.focus.refresh()

def complement_tree(tree):
    
    def complement(tree):
        if isinstance(tree, EqNode):
            return NeqNode(tree.left, tree.right)
        elif isinstance(tree, NeqNode):
            return EqNode(tree.left, tree.right)
        elif isinstance(tree, LtNode):
            return GeqNode(tree.left, tree.right)
        elif isinstance(tree, GtNode):
            return LeqNode(tree.left, tree.right)
        elif isinstance(tree, LeqNode):
            return GtNode(tree.left, tree.right)
        elif isinstance(tree, GeqNode):
            return LtNode(tree.left, tree.right)
        elif isinstance(tree, AndNode):
            return OrNode(complement(tree.left), complement(tree.right))
        elif isinstance(tree, OrNode):
            return AndNode(complement(tree.left), complement(tree.right))
        elif isinstance(tree, NotNode):
            return tree.left
        else:
            return NotNode(tree)

    return complement(deepcopy(tree))

def select_hypothesis(screen, tl, second):
    window = screen.win1
    pad = screen.pad1
    tlist = tl.tlist1
    window.refresh()
    forward = True

    while True:
        c = screen.stdscr.getkey()
        if c == 'KEY_UP':
            if pad.scroll_line > 0 or pad.cursor_line > 0:
                pad.cursor_up()
                pad.refresh()
        elif c == 'KEY_DOWN':
            if pad.scroll_line + pad.cursor_line < tlist.len():
                pad.cursor_down()
                pad.refresh()
        elif second and c == '\t': # TAB = switch hypotheses/targets, forward/backward
            pad = screen.pad2 if forward else screen.pad1
            window = screen.win2 if forward else screen.win1
            tlist = tl.tlist2 if forward else tl.tlist1
            forward = not forward
            pad.refresh()
        elif c == '\x1b': # ESC = cancel
            return -1
        elif c == '\n':
            return forward, pad.scroll_line + pad.cursor_line

def modus_ponens(screen, tl):
    forward, line1 = select_hypothesis(screen, tl, False)
    if line1 == -1: # Cancelled
        return
    forward, line2 = select_hypothesis(screen, tl, True)
    if line2 == -1: # Cancelled
        return
    tlist1 = tl.tlist1
    tlist2 = tl.tlist2
    tree1 = tlist1.data[line1]
    tree2 = tlist1.data[line2] if forward else tlist2.data[line2]
    if not isinstance(tree1, ImpliesNode): # no implication after quantifiers
        return 
    qP1 = tree1.left if forward else tree1.right
    qP2 = tree2
    unifies, assign = unify(qP1, qP2)
    if not unifies:
        return # does not unify, bogus selection
    if forward:
        n = tlist1.len()
        tlist1.data.append(substitute(tree1.right, assign))
        screen.pad1[n] = str(tlist1.data[n])# make substitutions
    else:
        n = tlist2.len()
        tlist2.data.append(substitute(tree1.left, assign))
        screen.pad2[n] = str(tlist2.data[n])
    # update windows
    screen.pad1.refresh()
    screen.pad2.refresh()
    screen.focus.refresh()

def modus_tollens(screen, tl):
    forward, line1 = select_hypothesis(screen, tl, False)
    if line1 == -1: # Cancelled
        return
    forward, line2 = select_hypothesis(screen, tl, True)
    if line2 == -1: # Cancelled
        return
    tlist1 = tl.tlist1
    tlist2 = tl.tlist2
    tree1 = tlist1.data[line1]
    tree2 = tlist1.data[line2] if forward else tlist2.data[line2]
    if not isinstance(tree1, ImpliesNode): # no implication after quantifiers
        return 
    qP1 = complement_tree(tree1.right) if forward else \
          complement_tree(tree1.left)
    qP2 = tree2
    unifies, assign = unify(qP1, qP2)
    if not unifies:
        return # does not unify, bogus selection
    if forward:
        n = tlist1.len()
        tlist1.data.append(complement_tree(substitute(tree1.left, assign)))
        screen.pad1[n] = str(tlist1.data[n])# make substitutions
    else:
        n = tlist2.len()
        tlist2.data.append(complement_tree(substitute(tree1.right, assign)))
        screen.pad2[n] = str(tlist2.data[n])
    # update windows
    screen.pad1.refresh()
    screen.pad2.refresh()
    screen.focus.refresh()

def substitute(tree, assign):
   for (var, val) in assign:
       tree = subst(tree, var, val)
   return tree

def skolemize(screen, tl):
    tl0 = tl.tlist0.data # quantifier zone
    tl1 = tl.tlist1.data # hypotheses
    tl2 = tl.tlist2.data # targets
    deps = []
    sk = []
    qz = []
    mv = []
    if tl0:
        sq, deps, sk = skolemize_quantifiers(tl0[0], deps, sk)
        if sq:
            tl.tlist0.data[0] = sq
            screen.pad0[0] = str(tl.tlist0.data[0])
        else:
            del tl.tlist0.data[0]
            screen.pad0[0] = ''

    d = len(deps)
    s = len(sk)

    def rollback():
        while len(deps) > d:
            deps.pop()
        while len(sk) > s:
            sk.pop()

    for i in range(0, len(tl1)):
        tl1[i] = skolemize_statement(tl1[i], deps, sk, qz, mv, False)
        rollback()
        screen.pad1[i] = str(tl1[i])
    for i in range(0, len(tl2)):
        tl2[i] = skolemize_statement(tl2[i], deps, sk, qz, mv, True)
        rollback()
        screen.pad2[i] = str(tl2[i])
    
    if qz:
        if tl0:
            t = tl0[0]
            while t.left:
                t = t.left
            r = range(0, len(qz))
        else:
            tl0.append(qz[0])
            t = qz[0]
            r = range(1, len(qz))
        for i in r:
            t.left = qz[i]
            t = t.left
        t.left = None
        screen.pad0[0] = str(tl.tlist0.data[0])

    screen.focus.cursor_adjust()
    screen.pad0.refresh()
    screen.pad1.refresh()
    screen.pad2.refresh()
    screen.focus.refresh()

def skolemize_quantifiers(tree, deps, sk):
    if isinstance(tree, ExistsNode):
        sk.append((tree.var.name, len(deps)))
        deps.append(tree.var)
        return skolemize_quantifiers(tree.left, deps, sk)
    elif isinstance(tree, ForallNode):
        deps.append(tree.var)
        tree.left, deps, sk = skolemize_quantifiers(tree.left, deps, sk)
        return tree, deps, sk
    else:
        return tree, deps, sk

def skolemize_statement(tree, deps, sk, qz, mv, positive):
    d = len(deps)
    s = len(sk)

    def rollback():
        while len(deps) > d:
            deps.pop()
        while len(sk) > s:
            sk.pop()
 
    if isinstance(tree, ForallNode):
        if positive:
            deps.append(tree.var)
            qz.append(tree)
        else:
            deps.append(tree.var)
            mv.append(tree.var.name)
        tree.left = skolemize_statement(tree.left, deps, sk, qz, mv, positive)
        rollback()
        return tree.left
    elif isinstance(tree, ExistsNode):
        sk.append((tree.var.name, len(deps)))
        if positive:
            mv.append(tree.var.name)
        else:
            deps.append(tree.var)
            qz.append(ForallNode(tree.var, None))
        tree.left = skolemize_statement(tree.left, deps, sk, qz, mv, positive)
        rollback()
        return tree.left
    elif isinstance(tree, LRNode):
        tree.left = skolemize_statement(tree.left, deps, sk, qz, mv, positive)
        tree.right = skolemize_statement(tree.right, deps, sk, qz, mv, positive)
        rollback()
        return tree
    elif isinstance(tree, VarNode):
        is_meta = False
        if tree.name in mv:
            is_meta = True
            tree.is_metavar = True
        n = skolem_deps(tree.name, sk)
        if n == -1: # not a skolem variable
            return tree
        else:
            fn_args = [VarNode(deps[i].name, deps[i].type) \
                    for i in range(0, n)]
            fn = FnNode(tree.name, fn_args)
            fn.is_skolem = True
            if is_meta:
                fn.is_metavar = True
            return fn
    elif isinstance(tree, FnNode):
        for i in range(0, len(tree.args)):
            tree.args[i] = skolemize_statement(tree.args[i], deps, sk, qz, mv, positive)
            rollback()
        return tree
    else:
        return tree
        
def skolem_deps(name, sk):
    for (v, n) in sk:
        if v == name:
            return n
    return -1
