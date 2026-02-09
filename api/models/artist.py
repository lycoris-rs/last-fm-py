from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ArtistImage(BaseModel):
    url: str = Field(alias="#text")
    size: Literal["small", "medium", "large", "extralarge", "mega"] | None

    @field_validator("size", mode="before")
    @classmethod
    def empty_size_to_none(cls, v: str) -> str | None:
        return v or None

    class Config:
        populate_by_name = True


class Artist(BaseModel):
    name: str
    listeners: int
    mbid: str | None
    url: str
    streamable: bool
    image: list[ArtistImage]

    @field_validator("listeners", mode="before")
    @classmethod
    def parse_listeners(cls, v: str | int) -> int:
        return int(v)

    @field_validator("mbid", mode="before")
    @classmethod
    def empty_mbid_to_none(cls, v: str) -> str | None:
        return v or None

    @field_validator("streamable", mode="before")
    @classmethod
    def parse_streamable(cls, v: str | int) -> bool:
        return bool(int(v))


class ArtistStats(BaseModel):
    listeners: int
    playcount: int

    @field_validator("listeners", "playcount", mode="before")
    @classmethod
    def parse_ints(cls, v: str | int) -> int:
        return int(v)


class SimilarArtist(BaseModel):
    name: str
    url: str
    image: list[ArtistImage]


class SimilarArtists(BaseModel):
    artist: list[SimilarArtist]


class ArtistTag(BaseModel):
    name: str
    url: str


class ArtistTags(BaseModel):
    tag: list[ArtistTag]


class ArtistBioLink(BaseModel):
    text: str = Field(alias="#text")
    rel: str
    link: str = Field(alias="href")


class ArtistBioLinks(BaseModel):
    link: ArtistBioLink


class ArtistBio(BaseModel):
    links: ArtistBioLinks
    published: str | None
    summary: str
    content: str


class ArtistDetail(BaseModel):
    name: str
    mbid: str | None
    url: str
    image: list[ArtistImage]
    streamable: bool
    ontour: bool
    stats: ArtistStats
    similar: SimilarArtists
    tags: ArtistTags
    bio: ArtistBio

    @field_validator("mbid", mode="before")
    @classmethod
    def empty_mbid_to_none(cls, v: str) -> str | None:
        return v or None

    @field_validator("streamable", mode="before")
    @classmethod
    def parse_streamable(cls, v: str | int) -> bool:
        return bool(int(v))


class ArtistMatches(BaseModel):
    artist: list[Artist]


class ArtistSearchResults(BaseModel):
    artistmatches: ArtistMatches


class ArtistSearchResponse(BaseModel):
    results: ArtistSearchResults


class ArtistDetailResponse(BaseModel):
    artist: ArtistDetail
