import os
from typing import Optional, Literal

from pydantic import Field
from pydantic_settings import BaseSettings


m_type = Literal["user", "assistant"]


class Settings(BaseSettings):
    openai_key: str
    openai_org: str
    openai_project: str
    prompt_message_1: str
    prompt_message_1_type: m_type = Field(default="user")
    prompt_message_2: Optional[str] = Field(default=None)
    prompt_message_2_type: m_type = Field(default="user")
    prompt_message_3: Optional[str] = Field(default=None)
    prompt_message_3_type: m_type = Field(default="user")
    prompt_message_4: Optional[str] = Field(default=None)
    prompt_message_4_type: m_type = Field(default="user")
    prompt_message_5: Optional[str] = Field(default=None)
    prompt_message_5_type: m_type = Field(default="user")


__SETTINGS = {
    "dev": Settings(_env_file="dev.env"),
}

settings = __SETTINGS.get(os.environ.get("MODE", "dev").lower())

