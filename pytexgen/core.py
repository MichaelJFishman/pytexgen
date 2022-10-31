# AUTOGENERATED! DO NOT EDIT! File to edit: ../latex_gen.ipynb.

# %% ../latex_gen.ipynb 1
from __future__ import annotations
from IPython.display import Markdown, display
import os, re
from dataclasses import dataclass
from typing import Union, Optional, Any, Collection, Iterable, TypeVar

from nbdev.export import nb_export

# %% auto 0
__all__ = ['TNS', 'to_node', 'TexBase', 'TexNode', 'TexAtom', 'TexSequence', 'TexPow', 'TexProd', 'TexFrac', 'TexColored',
           'jointex', 'TexEnvironment', 'TexList', 'TexAlign', 'TexParen', 'Prob', 'TexMatrix', 'multiply_matrices',
           'TexRoot']

# %% ../latex_gen.ipynb 4
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

class TexNode(TexBase):
    # Methods to mimic arithmetic
    # TODO parenthesize objects as needed.
    # Maybe by having that as a property of each object
    # and making a tex_p property that adds parens if needed
    
    # Use self + other
    def __add__(self, other: TexNode) -> TexSequence:
        return TexSequence((self, to_node(other)))

    # Use self ** other
    def __pow__(self, other: TexNode) -> TexPow:
        return TexPow(self, other)

    # Use self / other
    def __truediv__(self, other: TexNode) -> TexFrac:
        return TexFrac(self, other)


    def __mul__(self, other: TexNode) -> TexFrac:
        return TexProd(self, other)
    
class TexAtom(TexNode):
    s: str
    def __init__(self, s: str) -> None:
        super().__init__()
        self.s = s
    
    @property
    def tex(self) -> str:
        return self.s


TNS = TypeVar("TNS", bound=str|TexNode)

class TexSequence(TexNode):
    children: tuple[TexNode, ...]
    def __init__(self, children: Collection[TexNode]) -> None:
        super().__init__()
        self.children = tuple(children)
    
    @property
    def tex(self) -> str:
        return " ".join([c.tex for c in self.children])

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

class TexProd(TexNode):
    def __init__(self, l: TNS, r: TNS) -> None:
        super().__init__()
        self.l, self.r = to_node(l), to_node(r)

    @property
    def tex(self) -> str:
        return self.l.tex + " \\cdot " + self.r.tex

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
    

# %% ../latex_gen.ipynb 5
def jointex(sep: str,  children: Collection[TexNode]) -> TexAtom:
    s = ""
    for i, c in enumerate(children):
        s += c.tex
        if i < len(children) - 1:
            s += sep
    return TexAtom(s)

# %% ../latex_gen.ipynb 6
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

class TexList(TexEnvironment):
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
class TexAlign(TexList):
    def __init__(self, children: Collection[TNS]) -> None:
        super().__init__("align", children)


class TexParen(TexNode):
    def __init__(self, child: TNS) -> None:
        super().__init__()
        self.child = to_node(child)
        
    @property
    def tex(self) -> str:
        return "\\left( " + self.child.tex + " \\right)"

# %% ../latex_gen.ipynb 12
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

# %% ../latex_gen.ipynb 15
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

# %% ../latex_gen.ipynb 18
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
