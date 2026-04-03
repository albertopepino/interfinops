from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DashboardConfigUpdate(BaseModel):
    config_json: dict[str, Any]


class DashboardConfigResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    config_json: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


__all__ = ["DashboardConfigUpdate", "DashboardConfigResponse"]
