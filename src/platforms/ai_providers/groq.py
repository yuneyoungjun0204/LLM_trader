"""Groq API Client - High-speed LLM inference."""

from typing import Optional, Dict, Any, List, TypedDict, cast
from src.platforms.ai_providers.base import BaseApiClient
from src.utils.decorators import retry_api_call


class ResponseDict(TypedDict, total=False):
    """Type for API responses."""
    error: str


class GroqClient(BaseApiClient):
    """Client for handling Groq API requests (OpenAI-compatible)."""

    @retry_api_call(max_retries=3, initial_delay=1, backoff_factor=2, max_delay=30)
    async def chat_completion(self, model: str, messages: list, model_config: Dict[str, Any]) -> Optional[ResponseDict]:
        """Send a chat completion request to the Groq API.

        Args:
            model: Model identifier (e.g., "llama-3.3-70b-versatile")
            messages: List of message dicts with 'role' and 'content'
            model_config: Configuration for the model (temperature, max_tokens, etc.)

        Returns:
            API response dict or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": messages,
            **model_config
        }

        url = f"{self.base_url}/chat/completions"
        response = await self._make_post_request(url, headers, payload, model, timeout=120)

        return cast(ResponseDict, response) if response else None

    async def stream_chat_completion(self, model: str, messages: list, model_config: Dict[str, Any]):
        """Stream chat completion from Groq API (not used in current implementation)."""
        raise NotImplementedError("Streaming not implemented for Groq client")
