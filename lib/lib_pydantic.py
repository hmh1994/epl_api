from pydantic import BaseModel, Field
from typing import Any, Optional
from datetime import datetime

class MapperItem(BaseModel):
    
    author_kr: Optional[Any] = Field(None, alias="authoKr")
    author_en: Optional[Any] = Field(None, alias="authoEn")
    content_en: Optional[Any] = Field(None, alias="contentEn")
    content_kr: Optional[Any] = Field(None, alias="contentKr")
    thumbnail_url: Optional[Any] = Field(None, alias="newsImg")
    title_en: Optional[Any] = Field(None, alias="titleEn")
    title_kr: Optional[Any] = Field(None, alias="titleKr")
    source_id: Optional[Any] = Field(None, alias="sourceid")
    ###################################
    player_id: Optional[Any] = Field(None, alias="playerid")
    player_name_en: Optional[Any] = Field(None, alias="playerNameEn")

    #team_id: Any = Field(..., alias="teamid")
    #goals_per_match: Any = Field(..., alias="goalPerMatch")
    #team_logo: Any = Field(..., alias="teamLogo")

    class Config:
        populate_by_name = True
        extra = "allow"

