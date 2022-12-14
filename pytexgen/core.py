# AUTOGENERATED! DO NOT EDIT! File to edit: ../latex_gen.ipynb.

# %% ../latex_gen.ipynb 1
from __future__ import annotations
from IPython.display import Markdown, display
import os, re
from dataclasses import dataclass
from typing import Union, Optional, Any, Collection, Iterable, TypeVar

from nbdev.export import nb_export

# %% auto 0
__all__ = ['TNS', 'to_node', 'TexBase', 'TexNotMath', 'TexNode', 'TexAtom', 'TexText', 'TexSequence', 'TexPow', 'TexMul',
           'TexFrac', 'TexColored', 'TexParen', 'TexTuple', 'TexAdd', 'jointex', 'TexEq', 'Mathcal', 'TexSub',
           'TexSetQuant', 'TexD', 'wrap_tex_if_needed', 'TexTextConcat', 'TexEnvironment', 'TexEnvList', 'TexAlign',
           'TexList', 'Prob', 'TexMatrix', 'multiply_matrices', 'TexRoot']

# %% ../latex_gen.ipynb 5
def to_node(x: TNS) -> TexNode:
    """
    Converts a raw string to a TexAtom
    Returns a TexNode unaltered
    """
    if isinstance(x, str):
        return TexAtom(x)
    else:
        return x

class TexBase:
    @property
    def tex(self) -> str:
        raise NotImplementedError("Children should implement this")


    def display(self) -> None:
        display(Markdown("$$" + self.tex + "$$"))


class TexNotMath(TexBase):
    pass

class TexNode(TexBase):
    # Methods to mimic arithmetic
    # TODO parenthesize objects as needed.
    # Maybe by having that as a property of each object
    # and making a tex_p property that adds parens if needed
    def __init__(self, need_paren: bool=False) -> None:
        super().__init__()
        self.need_paren = need_paren

    # Use self + other
    def __add__(self, other: TexNode) -> TexAdd:
        return TexAdd([self, other])

    # Use self ** other
    def __pow__(self, other: TexNode) -> TexPow:
        return TexPow(self, other)

    # Use self / other
    def __truediv__(self, other: TexNode) -> TexFrac:
        return TexFrac(self, other)


    def __mul__(self, other: TexNode) -> TexMul:
        return TexMul([self, other])

    def __rshift__(self, other: TNS) -> TexSequence:
        return TexSequence((self, other))

    @property
    def texp(self) -> str:
        """
        Wraps tex with parens, if needed
        Call this when you may want to parenthesize this
        eg when taking a product
        """
        if self.need_paren:
            return TexParen(self).tex
        else:
            return self.tex
            
TNS = TypeVar("TNS", bound=Union[str,TexNode])

    
class TexAtom(TexNode):
    s: str
    def __init__(self, s: str, need_paren: bool = False) -> None:
        super().__init__(need_paren=need_paren)
        self.s = s

    @property
    def tex(self) -> str:
        return self.s


#| export
class TexText(TexNode):
    """\\text{not math}"""
    def __init__(self, s: str, need_paren: bool = False) -> None:
        super().__init__(need_paren)
        self.s = s

    @property
    def tex(self) -> str:
        return "\\text{" + str(self.s) + "}"



class TexSequence(TexNode):
    """Holds a tuple of children. Displays them with a space separation by default."""
    children: tuple[TexNode, ...]
    def __init__(self, children: Collection[TexNode], sep: str = " ") -> None:
        need_paren = len(children) > 1
        super().__init__(need_paren=need_paren)
        self.children =  tuple([to_node(c) for c in children])
        self.sep = sep
    
    @property
    def tex(self) -> str:
        return self.sep.join([c.tex for c in self.children])

class TexPow(TexNode):
    base: TexNode
    exp: TexNode
    def __init__(self, base: TNS, exp: TNS) -> None:
        super().__init__()
        self.base = to_node(base)
        self.exp = to_node(exp)
    
    @property
    def tex(self) -> str:
        return self.base.tex + "^{" + self.exp.tex + "}"

class TexMul(TexNode):
    def __init__(self, children: Collection[TNS], prod_symbol: str = "\\cdot") -> None:
        super().__init__(need_paren=False)
        self.children = tuple([to_node(c) for c in children])
        self.prod_symbol = prod_symbol
    
    @property
    def tex(self) -> str:
        sep = " " + self.prod_symbol + " "
        return sep.join([c.texp for c in self.children])

class TexFrac(TexNode):
    def __init__(self, num: TNS, den: TNS) -> None:
        super().__init__()
        self.num = to_node(num)
        self.den = to_node(den)

    @property
    def tex(self) -> str:
        return "\\frac{" + self.num.tex + "}" + "{" + self.den.tex + "}"

class TexColored(TexNode):
    child: TexNode
    color: str
    def __init__(self, child: TNS, color: str) -> None:
        super().__init__()
        child = to_node(child)
        self.child = child
        self.color = color
    
    @property
    def tex(self) -> str:
        return "{\\color{" + self.color + "}" + self.child.tex + "}"
    

class TexParen(TexNode):
    """Wraps parens around child"""
    def __init__(self, child: TNS, parens: tuple[str,str] = ("(", ")")) -> None:
        super().__init__()
        self.parens = parens
        self.child = to_node(child)
        
    @property
    def tex(self) -> str:
        return f"\\left{self.parens[0]} " + self.child.tex + f" \\right{self.parens[1]}"

class TexTuple(TexNode):
    """Holds a tuple, comma separated and with parens"""
    def __init__(self, children: Collection[TNS], parens: tuple[str,str] = ("(", ")")) -> None:
        super().__init__()
        self.children = tuple([to_node(c) for c in children])
        self.parens = parens
    @property
    def tex(self) -> str:
        return TexParen(jointex(", ", self.children), self.parens).tex



class TexAdd(TexNode):
    """a + b"""
    def __init__(self, children: Collection[TNS]) -> None:
        need_paren = len(children) > 1
        super().__init__(need_paren=need_paren)
        self.children = tuple([to_node(c) for c in children])
    
    @property
    def tex(self) -> str:
        return " + ".join([c.tex for c in self.children])

def jointex(sep: str,  children: Collection[TexNode]) -> TexAtom:
    s = ""
    for i, c in enumerate(children):
        s += c.tex
        if i < len(children) - 1:
            s += sep
    return TexAtom(s)


class TexEq(TexSequence):
    """a = b"""
    def __init__(self, children: Collection[TNS]) -> None:
        super().__init__(children, " = ")

class Mathcal(TexNode):
    def __init__(self, child: TNS) -> None:
        self.child = to_node(child)
        super().__init__(need_paren = self.child.need_paren)
    @property
    def tex(self) -> str:
        return "\\mathcal{" + self.child.tex + "}"


class TexSub(TexNode):
    """Subscript"""
    def __init__(self, base: TNS, sub: TNS) -> None:
        super().__init__()
        self.base = to_node(base)
        self.sub = to_node(sub)
    
    @property
    def tex(self) -> str:
        return self.base.texp + "_{" + self.sub.tex + "}"
        

# %% ../latex_gen.ipynb 6
class TexSetQuant(TexParen):
    """{x^2 | x \in X}"""
    def __init__(self, left: TNS, filter: TNS) -> None:
        seq = TexSequence([left, "\\mid", filter])
        super().__init__(seq, parens=("\\{", "\\}"))


# %% ../latex_gen.ipynb 8
class TexD(TexBase):
    """Wrapper to tell TexTexConcat to use display mode"""
    def __init__(self, child: TNS) -> None:
        super().__init__()
        self.child = to_node(child)
    
    @property
    def tex(self) -> str:
        return self.child.tex
    

def wrap_tex_if_needed(x: TNS) -> str:
    """
    Wraps TexD in $$, TexNode in $, and returns strings unchanged.
    """
    if isinstance(x, TexD):
        return "$$" + x.tex + "$$"
    elif isinstance(x, TexNotMath):
        return x.tex
    elif isinstance(x, TexBase):
        return "$" + x.tex + "$"
    else:
        return x


class TexTextConcat(TexNotMath):
    """
    Holds tex and text and whatnot and concatenates it properly
    """
    def __init__(self, *args: list[Union[str, TexBase]]) -> None:
        self.children = args
    
    def to_markdown(self) -> str:
        pieces = [wrap_tex_if_needed(c) for c in self.children]
        return "".join(pieces)

    def display(self) -> None:
        display(Markdown(self.to_markdown()))

    @property
    def tex(self) -> str:
        return self.to_markdown()

# %% ../latex_gen.ipynb 10
class TexEnvironment(TexBase):
    def __init__(self, nm: str) -> None:
        super().__init__()
        self.nm = nm
    
    @property
    def begin_tex(self) -> str:
        return "\\begin{" + self.nm + "}"
    
    @property
    def end_tex(self) -> str:
        return "\\end{" + self.nm + "}"

class TexEnvList(TexEnvironment):
    # Should nm instead be a class-level attribute?
    def __init__(self,nm: str, children: Collection[TNS]) -> None:
        super().__init__(nm)
        self.children  = tuple([to_node(c) for c in children])

    @property
    def tex(self) -> str:
        lines = jointex("\\\\\n", self.children)
        s = self.begin_tex + "\n" + lines.tex + "\n" + self.end_tex
        return s


# Should we have special consideration for alignment with & ?
class TexAlign(TexEnvList):
    def __init__(self, children: Collection[TNS]) -> None:
        super().__init__("align", children)


class TexList(TexNotMath):
    """BUG Katex doesn't have the itemize environment, so we use markdown for this :/"""
    def __init__(self, children: Collection[TNS], numbered: bool = False) -> None:
        self.children = children
        self.numbered = numbered

    @property
    def list_starter(self) -> str:
        if self.numbered:
            return "1. "
        else:
            return "- "

    @property
    def tex(self) -> str:
        pieces = [self.list_starter + wrap_tex_if_needed(c) for c in self.children]
        return "\n".join(pieces)

    def display(self) -> None:
        display(Markdown(self.tex))
    

# %% ../latex_gen.ipynb 17
class Prob(TexNode):
    cond: Optional[TexNode]
    def __init__(self, event: Union[str, TexNode], cond: Optional[Union[str, TexNode]] = None) -> None:
        super().__init__()
        self.event = to_node(event)
        if cond is None:
            self.cond = None
        else:
            self.cond = to_node(cond)

    @property
    def tex(self) -> str:
        s = "\\mathrm{P}\\left( " + self.event.tex
        if self.cond is not None:
            s += "\\mid " + self.cond.tex
        s +=  " \\right)"
        return s

# %% ../latex_gen.ipynb 20
class TexMatrix(TexNode):
    def __init__(self, els: Collection[Collection[TNS]]) -> None:
        super().__init__()
        self.els = tuple([tuple([to_node(x) for x in row]) for row in els])
    @property
    def tex(self) -> str:
        s = "\\begin{bmatrix}\n"
        lines = [jointex(" & ", row) for row in self.els]
        s_content = jointex("\\\\\n", lines)
        s += s_content.tex
        s += "\n\\end{bmatrix}"
        return s
    @property
    def n_rows(self) -> int:
        return len(self.els)
    
    @property
    def n_cols(self) -> int:
        return len(self.els[0])

def multiply_matrices(m0: TexMatrix, m1: TexMatrix) -> TexMatrix:
    # Check that this multiplication is defined
    if m0.n_cols != m1.n_rows:
        raise ValueError(f"When multiplying matrices A x B, A.n_cols must equal B.n_rows. {m0.n_cols} != {m1.n_rows}")
    n_rows = m0.n_rows
    n_cols = m1.n_cols
    els_out = [[None for _ in range(n_cols)] for _ in range(n_rows)]
    for r in range(n_rows):
        for c in range(n_cols):
            terms = []
            for r2 in range(m1.n_rows):
                for c2 in range(m0.n_cols):
                    terms.append(m0.els[r][c2] * m1.els[r2][c])
            node = jointex(" + ", terms)
            els_out[r][c] = node
    m_out = TexMatrix(els_out)
    return m_out

# %% ../latex_gen.ipynb 23
class TexRoot(TexNode):
    def __init__(self, child: TNS, power: Optional[TNS] = None) -> None:
        super().__init__()
        self.child = to_node(child)
        if power is None:
            self.power = None
        else:
            self.power = to_node(power)
    @property
    def tex(self) -> str:
        s = "\\sqrt"
        if self.power is not None:
            s += "[" + self.power.tex + "]"
        s += "{" + self.child.tex + "}"
        return s
