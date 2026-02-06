from typing import Union
from .primitive.paragraph import *
from .primitive.table import *

ElementModel = Union[ParagraphModel, TableModel]
