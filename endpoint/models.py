from typing import Optional, List
from pydantic import BaseModel


class Function(BaseModel):
    name: str
    description: str
    parameters: dict


class UserQuery(BaseModel):
    user_query: str
    functions: Optional[List[Function]] = []
