from pydantic import BaseModel, Field


class Tag(BaseModel):
    name: str
    url: str


class AlbumTagMeta(BaseModel):
    artist: str
    album: str


class AlbumTags(BaseModel):
    tag: list[Tag]
    attr: AlbumTagMeta = Field(alias="@attr")


class AlbumTagResponse(BaseModel):
    tags: AlbumTags
