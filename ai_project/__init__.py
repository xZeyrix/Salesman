__all__ = ["Salesman", "IncMsgStructure"]

_EXPORTS = {
    "Salesman": ("ai_project.ai_system.salesman", "Salesman"),
    "IncMsgStructure": ("ai_project.ai_system.type_helpers", "IncMsgStructure"),
}

from importlib import import_module
from typing import TYPE_CHECKING


def __getattr__(name: str):
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    
    module_path, attr_name = target
    module = import_module(module_path, package=__name__)
    value = module if attr_name is None else getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))


if TYPE_CHECKING:
    from .ai_system.salesman import Salesman
    from .ai_system.type_helpers import IncMsgStructure