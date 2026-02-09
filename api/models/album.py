from typing import Literal
from pydantic import BaseModel, Field, field_validator


class AlbumImage(BaseModel):
    url: str = Field(alias="#text")
    size: Literal["small", "medium", "large", "extralarge", "mega"] | None

    @field_validator("size", mode="before")
    @classmethod
    def empty_size_to_none(cls, v: str) -> str | None:
        return v or None

    class Config:
        populate_by_name = True


class Album(BaseModel):
    name: str
    artist: str
    url: str
    image: list[AlbumImage]
    streamable: bool
    mbid: str | None

    @field_validator("streamable", mode="before")
    @classmethod
    def parse_streamable(cls, v: str | int) -> bool:
        return bool(int(v))

    @field_validator("mbid", mode="before")
    @classmethod
    def empty_mbid_to_none(cls, v: str) -> str | None:
        return v or None


class AlbumTag(BaseModel):
    url: str
    name: str


class AlbumTags(BaseModel):
    tag: list[AlbumTag]


class AlbumTrackStreamable(BaseModel):
    fulltrack: bool
    text: str = Field(alias="#text")

    @field_validator("fulltrack", mode="before")
    @classmethod
    def parse_fulltrack(cls, v: str | int) -> bool:
        return bool(int(v))


class AlbumTrackIndex(BaseModel):
    index: int = Field(alias="rank")


class AlbumTrackArtist(BaseModel):
    name: str
    url: str
    mbid: str | None

    @field_validator("mbid", mode="before")
    @classmethod
    def empty_mbid_to_none(cls, v: str) -> str | None:
        return v or None


class AlbumTrackWiki(BaseModel):
    published: str
    summary: str | None
    content: str | None


class AlbumTrack(BaseModel):
    streamable: AlbumTrackStreamable
    duration: int | None
    url: str
    name: str
    index: AlbumTrackIndex = Field(alias="@attr")
    artist: AlbumTrackArtist


class AlbumTracks(BaseModel):
    track: list[AlbumTrack]

    @field_validator("track", mode="before")
    @classmethod
    def normalize_track(cls, v):
        return v if isinstance(v, list) else [v]


class AlbumDetail(BaseModel):
    artist: str
    mbid: str | None
    listeners: int
    playcount: int
    userplaycount: int | None = None
    tags: AlbumTags | None
    image: list[AlbumImage]
    tracks: AlbumTracks
    wiki: AlbumTrackWiki | None = None

    @field_validator("listeners", "playcount", mode="before")
    @classmethod
    def parse_ints(cls, v: str | int) -> int:
        return int(v)


class AlbumMatches(BaseModel):
    album: list[Album]


class AlbumSearchResults(BaseModel):
    albummatches: AlbumMatches


class AlbumSearchResponse(BaseModel):
    results: AlbumSearchResults


class AlbumDetailResponse(BaseModel):
    album: AlbumDetail
