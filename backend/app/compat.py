from __future__ import annotations

from typing import Any, ForwardRef, cast

import pydantic.typing as pydantic_typing


def patch_forward_ref_evaluation() -> None:
    signature = ForwardRef._evaluate.__code__.co_varnames  # type: ignore[attr-defined]
    if 'recursive_guard' in signature and 'type_params' in signature:
        def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Any) -> Any:  # type: ignore[name-defined]
            try:
                return cast(Any, type_)._evaluate(globalns, localns, None, recursive_guard=set())
            except TypeError:
                return cast(Any, type_)._evaluate(globalns, localns, set())

        pydantic_typing.evaluate_forwardref = evaluate_forwardref  # type: ignore[assignment]


patch_forward_ref_evaluation()
