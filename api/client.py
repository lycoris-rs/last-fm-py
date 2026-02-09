from typing import Any, Final, Self

import aiohttp
from aiohttp_client_cache import CacheBackend
import anyio
from aiohttp_client_cache.backends.sqlite import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from loguru import logger

from .exceptions import LastFMException, LastFMErrorResponse
from .models import (
    Artist,
    ArtistSearchResponse,
    ArtistDetail,
    ArtistDetailResponse,
    Album,
    AlbumSearchResponse,
    AlbumDetail,
    AlbumDetailResponse,
)

__all__ = ("LastFMApi",)

CACHE_PATH = anyio.Path("./.cache/lastfm")


class LastFMApi:
    """The main class to interact with the last.fm API

    Args:
        api_key: Your personal Last.fm API Key. Required.
                 Visit https://www.last.fm/api/authentication for instructions.
        cache_ttl: The time-to-live for the cached data in seconds, defaults to 3600. Optional.
        headers: Dictionary of headers to include in the requests. Optional.
        session: If you have an existing aiohttp.ClientSession to use, set it here. If None,
                 a new CachedSession will be created. Optional
        cache_backend: A CacheBackend instance for caching. If None, a SQLite backend
                       will be used with a default path. Optional.
    """

    BASE_URL: Final[str] = "http://ws.audioscrobbler.com/2.0"

    def __init__(
        self,
        *,
        api_key: str,
        cache_ttl: int = 3600,
        headers: dict[str, Any] | None = None,
        session: aiohttp.ClientSession | None = None,
        cache_backend: CacheBackend | None = None,
    ) -> None:
        self.api_key = api_key
        self.cache_ttl = cache_ttl

        self._using_custom_session = session is not None
        self._session = session
        self._cache = cache_backend or SQLiteBackend(
            "./.cache/lastfm/aiohttp-cache.db", expire_after=cache_ttl
        )
        self._headers = headers or {"User-Agent": "last-fm-py"}

    async def __aenter__(self) -> Self:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def _request(
        self, *, params: dict[str, Any], use_cache: bool
    ) -> dict[str, Any]:
        """Make an asynchronous request to the specified API endpoint.

        Args:
            params: The parameters to supply the API with. Required.
            use_cache: Whether to allow the request to be served from cache.
                       Defaults to True. Optional.

        Raises:
            LastFMException: If the Last.fm API returns an error response.
            RuntimeError: If the client session has not been initialized.
        """
        if self._session is None:
            msg = f"Call `{self.__class__.__name__}.start` before making requests."
            raise RuntimeError(msg)

        params = {
            **{k: v for k, v in params.items() if v is not None},
            "api_key": self.api_key,
            "format": "json",
        }

        logger.debug(f"Requesting {self.BASE_URL} with params={params}")

        if not use_cache and isinstance(self._session, CachedSession):
            async with self._session.disabled():
                async with self._session.get(self.BASE_URL, params=params) as resp:
                    data: dict[str, Any] = await resp.json()
        else:
            async with self._session.get(self.BASE_URL, params=params) as resp:
                data: dict[str, Any] = await resp.json()

        if "error" in data:
            err = LastFMErrorResponse.model_validate(data)
            raise LastFMException(err.error, err.message)

        return data

    async def start(self) -> None:
        """Initialize the internal aiohttp session.

        Must be called before making any API requests if not using `async with`.
        """
        self._session = self._session or CachedSession(
            headers=self._headers, cache=self._cache
        )

    async def close(self) -> None:
        """Close the internal aiohttp session.

        Should be called to release resources if not using `async with`.
        """
        if self._session is not None and not self._using_custom_session:
            await self._session.close()

    async def album_search(
        self,
        album: str,
        limit: int = 30,
        page: int = 1,
        use_cache: bool = True,
    ) -> list[Album]:
        """Search for an album.

        Returns:
            A list of matching albums.

        Args:
            album: The name of the album. Required.
            limit: The amount of albums to return. Defaults to 30. Optional.
            page: The page to return the results from. Defaults to 1. Optional.
            use_cache: Whether to allow the response to be served from cache.
                       Defaults to True. Optional.
        """
        params = {
            "method": "album.search",
            "album": album,
            "limit": limit,
            "page": page,
        }
        data = await self._request(
            params=params,
            use_cache=use_cache,
        )
        parsed = AlbumSearchResponse.model_validate(data)
        return parsed.results.albummatches.album

    async def album_get_info(
        self,
        artist: str,
        album: str,
        mbid: str | None = None,
        lang: str | None = None,
        username: str | None = None,
        autocorrect: bool = True,
        use_cache: bool = True,
    ) -> AlbumDetail:
        """Fetch details about a specific album.

        Returns:
            An AlbumDetail object.

        Args:
            artist: The artist of the album. Required, unless mbid is supplied.
            album: The name of the album. Required, unless mbid is supplied.
            mbid: The musicbrainz id for the album. Optional.
            lang: The language to return the biography in.
                  Expressed as an ISO 639 alpha-2 code. Optional.
            username: The username for the context of the request.
                      If supplied, the user's playcount for this
                      album is included in the response. Optional.
            autocorrect: Tries to transform the artist name into the correct artist.
                         This is best-effort and may not work for all artists.
                         For reliable results, prefer supplying an MBID if available. Optional.
            use_cache: Whether to allow the response to be served from cache.
                       Defaults to True. Optional.
        """
        params = {
            "method": "album.getinfo",
            "artist": artist,
            "album": album,
            "mbid": mbid,
            "lang": lang,
            "username": username,
            "autocorrect": int(autocorrect),
        }
        data = await self._request(params=params, use_cache=use_cache)
        parsed = AlbumDetailResponse.model_validate(data)
        return parsed.album

    async def artist_search(
        self,
        artist: str,
        limit: int = 30,
        page: int = 1,
        use_cache: bool = True,
    ) -> list[Artist]:
        """Search for an artist.

        Returns:
            A list of matching artists.

        Args:
            artist: The name of the artist. Required.
            limit: The amount of artists to return. Defaults to 30. Optional.
            page: The page to return the results from. Defaults to 1. Optional.
            use_cache: Whether to allow the response to be served from cache.
                       Defaults to True. Optional.
        """
        params = {
            "method": "artist.search",
            "artist": artist,
            "limit": limit,
            "page": page,
        }
        data = await self._request(
            params=params,
            use_cache=use_cache,
        )
        parsed = ArtistSearchResponse.model_validate(data)
        return parsed.results.artistmatches.artist

    async def artist_get_info(
        self,
        artist: str,
        mbid: str | None = None,
        lang: str | None = None,
        username: str | None = None,
        autocorrect: bool = True,
        use_cache: bool = True,
    ) -> ArtistDetail:
        """Fetch details about a specific artist.

        Args:
            artist: The name of the artist. Required, unless mbid is supplied.
            mbid: The musicbrainz id for the artist. Optional.
            lang: The language to return the biography in. Optional.
                  Expressed as an ISO 639 alpha-2 code.
            username: The username for the context of the request.
                      If supplied, the user's playcount for this
                      artist is included in the response. Optional.
            autocorrect: Tries to transform the artist name into the correct artist.
                         This is best-effort and may not work for all artists.
                         For reliable results, prefer supplying an MBID if available. Optional.
            use_cache: Whether to allow the response to be served from cache.
                       Defaults to True. Optional.
        """
        params = {
            "method": "artist.getinfo",
            "artist": artist,
            "mbid": mbid,
            "lang": lang,
            "username": username,
            "autocorrect": int(autocorrect),
        }
        data = await self._request(
            params=params,
            use_cache=use_cache,
        )
        parsed = ArtistDetailResponse.model_validate(data)
        return parsed.artist
