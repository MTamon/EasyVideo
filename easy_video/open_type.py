from typing import Literal
from typing_extensions import TypeAlias

VideoIOMode: TypeAlias = Literal["w", "r"]

OpenReadMode: TypeAlias = Literal["r"]
OpenWriteMode: TypeAlias = Literal["w"]

# TODO: Add support for append mode
OpenAppendMode: TypeAlias = Literal["a"]
