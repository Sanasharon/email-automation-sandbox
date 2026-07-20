from typing import Any, Dict, Generic, Type, TypeVar, List, Optional, Union
from pydantic import BaseModel
import datetime
import uuid

DataT = TypeVar("DataT")

class APIResponse(BaseModel, Generic[DataT]):
    success: bool
    message: str = "Success"
    data: Optional[DataT] = None
    request_id: Optional[str] = None
    timestamp: str = ""
    version: str = "v1"

class APIErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class APIErrorResponse(BaseModel):
    success: bool = False
    error: APIErrorDetail
    request_id: Optional[str] = None
    timestamp: str = ""
    version: str = "v1"

def success_response(
    data: Any = None, 
    message: str = "Success", 
    request_id: Optional[str] = None
) -> APIResponse[Any]:
    return APIResponse(
        success=True,
        message=message,
        data=data,
        request_id=request_id or str(uuid.uuid4()),
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

def error_response(
    code: str, 
    message: str, 
    details: Optional[Dict[str, Any]] = None, 
    request_id: Optional[str] = None
) -> APIErrorResponse:
    return APIErrorResponse(
        success=False,
        error=APIErrorDetail(code=code, message=message, details=details),
        request_id=request_id or str(uuid.uuid4()),
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
