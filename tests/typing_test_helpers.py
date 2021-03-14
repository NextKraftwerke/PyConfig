from sys import version_info
from typing import NamedTuple, Tuple, List, FrozenSet, Set, Dict

_python_minor = version_info.minor


class CollectionTypeHolder(NamedTuple):
    tuple: type
    list: type
    frozenset: type
    set: type
    dict: type


_typing_collections = CollectionTypeHolder(
    tuple=Tuple,
    list=List,
    frozenset=FrozenSet,
    set=Set,
    dict=Dict,
)

if _python_minor < 9:
    collection_type_holders = (_typing_collections,)
else:
    _builtin_collections = CollectionTypeHolder(
        tuple=tuple,
        list=list,
        frozenset=frozenset,
        set=set,
        dict=dict,
    )
    collection_type_holders = (_typing_collections, _builtin_collections)
