"""The one thing the rest of TrustDesk needs from a language model."""

from typing import Protocol


class LLMClient(Protocol):
    def complete(self, system: str, prompt: str) -> str:
        """Send an instruction (`system`) and a request (`prompt`); return the model's text reply."""
        ...
