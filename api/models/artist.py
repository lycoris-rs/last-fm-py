from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ArtistImage(BaseModel):
    """
    Represents an image associated with an artist.

    Attributes:
        url: The URL of the image.
        size: The size category of the image. One of "small", "medium", "large",
              "extralarge", or "mega". Optional.
    """

    url: str = Field(alias="#text")
    size: Literal["small", "medium", "large", "extralarge", "mega"] | None

    @field_validator("size", mode="before")
    @classmethod
    def empty_size_to_none(cls, v: str) -> str | None:
        return v or None

    class Config:
        populate_by_name = True


class Artist(BaseModel):
    """
    Basic information about an artist.

    Attributes:
        name: The artist's name.
        listeners: Number of listeners the artist has.
        mbid: The MusicBrainz ID for the artist. Optional.
        url: The URL to the artist's page.
        streamable: Whether the artist's content is streamable. (Not sure if this is correct.)
        image: List of associated ArtistImage objects.
    """

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
    """
    Statistical information about an artist.

    Attributes:
        listeners: Number of listeners.
        playcount: Total play count.
    """

    listeners: int
    playcount: int

    @field_validator("listeners", "playcount", mode="before")
    @classmethod
    def parse_ints(cls, v: str | int) -> int:
        return int(v)


class SimilarArtist(BaseModel):
    """
    Represents a similar artist to the queried artist.

    Attributes:
        name: The similar artist's name.
        url: URL to the similar artist's page.
        image: List of associated ArtistImage objects.
    """

    name: str
    url: str
    image: list[ArtistImage]


class SimilarArtists(BaseModel):
    """
    Container for a list of similar artists.

    Attributes:
        artist: List of SimilarArtist objects.
    """

    artist: list[SimilarArtist]


class ArtistTag(BaseModel):
    """
    Represents a tag associated with an artist.

    Attributes:
        name: Name of the tag.
        url: URL related to the tag.
    """

    name: str
    url: str


class ArtistTags(BaseModel):
    """
    Container for artist tags

    Attributes:
        tag: List of ArtistTag objects.
    """

    tag: list[ArtistTag]


class ArtistBioLink(BaseModel):
    """
    Link information within the artist's biography.

    Attributes:
        text: The display text of the link.
        rel: The relationship attribute of the link.
        link: The URL of the link.
    """

    text: str = Field(alias="#text")
    rel: str
    link: str = Field(alias="href")


class ArtistBioLinks(BaseModel):
    """
    Container for biography links.

    Attributes:
        link: An ArtistBioLink object.
    """

    link: ArtistBioLink


class ArtistBio(BaseModel):
    """
    Biography details for an artist.

    Attributes:
        links: Links related to the biography.
        published: Publication date of the biography.
        summary: A short summary of the biography.
        content: Full content of the biography.
    """

    links: ArtistBioLinks
    published: str
    summary: str
    content: str


class ArtistDetail(BaseModel):
    """
    Detailed information about an artist.

    Attributes:
        name: The artist's name.
        mbid: The MusicBrainz ID for the artist. Optional.
        url: URL to the artist's page.
        image: List of associated images.
        streamable: Whether the artist's content is streamable. (Not sure if this is correct.)
        ontour: Whether the artist is currently on tour.
        stats: Statistical information.
        similar: Similar Artists.
        tags: Tags associated with the artist.
        bio: biography details.
    """

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
    """
    Container for artist search matches.

    Attributes:
        artist: List of Artist objects representing matched artists.
    """

    artist: list[Artist]


class ArtistSearchResults(BaseModel):
    """
    Container for search results of artists.

    Attributes:
        artistmatches: An ArtistMatches object.
    """

    artistmatches: ArtistMatches


class ArtistSearchResponse(BaseModel):
    """
    Response model for artist search API calls.

    Attributes:
        results: An ArtistSearchResults object.
    """

    results: ArtistSearchResults


class ArtistDetailResponse(BaseModel):
    """
    Response model for artist detail API calls.

    Attributes:
        artist: An ArtistDetail object.
    """

    artist: ArtistDetail
