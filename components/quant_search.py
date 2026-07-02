import os
import streamlit.components.v1 as components

_FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "quant_search_frontend")

_component = components.declare_component(
    "quant_search",
    path=_FRONTEND_DIR,
)


def quant_search(current_ticker, popular, key=None):
    """Renders the symbol search bar + live dropdown (popular list / filtered
    matches / free-text entry, with keyboard nav and click-to-select).

    Returns the newly selected ticker string the moment the user picks one
    (click or Enter) — None otherwise. The returned value persists across
    reruns until a new selection is made, so callers should dedupe against
    the last value they've already acted on (see components/search.py).
    """
    return _component(
        current_ticker=current_ticker,
        popular=popular,
        key=key,
        default=None,
    )
