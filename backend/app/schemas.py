from pydantic import BaseModel, Field


class TranslationOptions(BaseModel):
    endpoint: str = Field(..., min_length=1)
    model: str = Field(default="deepseek-v4-flash", min_length=1)
    api_key: str = ""
    source_language: str = "Chinese (Simplified)"
    target_language: str = "English"
    batch_size: int = Field(default=12, ge=1, le=100)
    max_workers: int = Field(default=3, ge=1, le=16)
    retry: int = Field(default=3, ge=1, le=10)
    translation_style: str = "Balanced"
    prompt_template: str = (
        "Translate from {source_language} to {target_language}.\n"
        "Terminology:\n{terminology}\n\nText:\n{text}"
    )
    terminology: dict[str, str] = Field(default_factory=dict)
    force_terminology_replace: bool = True

