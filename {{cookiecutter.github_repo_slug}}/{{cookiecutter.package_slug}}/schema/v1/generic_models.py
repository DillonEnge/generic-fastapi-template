from typing import List, Optional

from pydantic import BaseModel


class FilterPayload(BaseModel):
    ids: Optional[List[str]] = None
