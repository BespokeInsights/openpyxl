#Autogenerated schema
from .LineSer import *

from openpyxl.descriptors.serialisable import Serialisable
from openpyxl.descriptors import (
    Typed,
    Set,
    Integer,
    NoneSet,
    Bool,
    String,
    Float,)


class PieSer(Serialisable):

    explosion = Typed(expected_type=UnsignedInt, allow_none=True)
    dPt = Typed(expected_type=DPt, allow_none=True)
    dLbls = Typed(expected_type=DLbls, allow_none=True)
    cat = Typed(expected_type=AxDataSource, allow_none=True)
    val = Typed(expected_type=NumDataSource, allow_none=True)
    extLst = Typed(expected_type=ExtensionList, allow_none=True)

    def __init__(self,
                 explosion=None,
                 dPt=None,
                 dLbls=None,
                 cat=None,
                 val=None,
                 extLst=None,
                ):
        self.explosion = explosion
        self.dPt = dPt
        self.dLbls = dLbls
        self.cat = cat
        self.val = val
        self.extLst = extLst
