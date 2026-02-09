from pydantic import BaseModel


class LastFMException(Exception):
    def __init__(self, error: int, message: str):
        self.error = error
        self.message = message
        super().__init__(f"Last.fm error {error}: {message}")


class LastFMErrorResponse(BaseModel):
    error: int
    message: str
