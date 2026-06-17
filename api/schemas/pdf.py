from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    template_id: str = Field(alias="templateId")
    resume: dict

    model_config = {"populate_by_name": True}


class ExportResponse(BaseModel):
    message: str
