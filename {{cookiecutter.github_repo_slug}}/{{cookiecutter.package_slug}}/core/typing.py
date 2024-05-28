"""Custom type definitions and aliases."""

from typing import Any, Dict

# A dictionary which is generally used to model a JSON serializable payload.
# Note that the serialize-ability of the value is not enforced here.
BasicDict = Dict[str, Any]
