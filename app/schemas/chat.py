from typing import Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    model: Optional[str] = None
    temperature: Optional[float] = None