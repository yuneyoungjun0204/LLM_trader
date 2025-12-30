"""
Ollama API client for local LLM inference.

Ollama provides OpenAI-compatible API endpoints for running local models.
This client supports multiple models optimized for different tasks:
- Qwen2.5 14B: Main trading analysis (general purpose)
- Qwen2-Math 7B: Technical indicator calculations and math
- DeepSeek-R1 7B: Pattern reasoning and strategic analysis
- Llama 3.1 8B: Fast news summarization

API Compatibility: Uses OpenAI Chat Completions format
Default URL: http://localhost:11434/v1
"""

import asyncio
import json
from typing import Optional, Dict, Any, cast

import aiohttp

from src.logger.logger import Logger
from src.platforms.ai_providers.base import BaseApiClient
from src.platforms.ai_providers.openrouter import ResponseDict
from src.utils.decorators import retry_api_call


class OllamaClient(BaseApiClient):
    """Client for handling Ollama API requests with OpenAI-compatible endpoints."""

    def __init__(self, base_url: str, logger: Logger) -> None:
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL (e.g., http://localhost:11434/v1)
            logger: Logger instance for logging
        """
        # Ollama doesn't require an API key
        super().__init__(api_key="ollama-local", base_url=base_url, logger=logger)
        self.logger.info(f"Initialized Ollama client with base URL: {base_url}")

    @retry_api_call(max_retries=3, initial_delay=1, backoff_factor=2, max_delay=30)
    async def chat_completion(self, model: str, messages: list, model_config: Dict[str, Any]) -> Optional[ResponseDict]:
        """
        Send a chat completion request to the Ollama API.

        Args:
            model: Model identifier (e.g., qwen2.5:14b, deepseek-r1:7b)
            messages: List of message dictionaries with 'role' and 'content'
            model_config: Configuration parameters (temperature, top_p, max_tokens, etc.)

        Returns:
            Response dictionary or None if request fails
        """
        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            **model_config
        }

        url = f"{self.base_url}/chat/completions"
        response = await self._make_post_request(url, headers, payload, model, timeout=2000)  # 20 minutes for large models

        return cast(ResponseDict, response) if response else None

    @retry_api_call(max_retries=3, initial_delay=1, backoff_factor=2, max_delay=30)
    async def stream_chat_completion(self, model: str, messages: list, model_config: Dict[str, Any],
                                    callback=None) -> Optional[ResponseDict]:
        """
        Send a streaming chat completion request to the Ollama API.

        Args:
            model: Model identifier (e.g., qwen2.5:14b)
            messages: List of message dictionaries
            model_config: Configuration parameters
            callback: Optional callback function for streaming chunks

        Returns:
            Complete response dictionary after streaming finishes
        """
        session = self._ensure_session()

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,  # Enable streaming
            **model_config
        }

        try:
            self.logger.debug(f"Sending streaming request to Ollama API with model: {model}")
            complete_response = {"choices": [{"message": {"content": "", "role": "assistant"}}]}

            # Use ClientTimeout for aiohttp requests (20 minutes for large models)
            client_timeout = aiohttp.ClientTimeout(total=2000)
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=client_timeout
            ) as response:
                if response.status != 200:
                    error_response = await self._handle_error_response(response, model)
                    return cast(ResponseDict, error_response)

                # Iterate through streaming response chunks
                async for chunk in response.content:
                    if not chunk:
                        continue

                    try:
                        chunk_text = chunk.decode('utf-8').strip()

                        # Skip empty chunks and non-data lines
                        if not chunk_text or not chunk_text.startswith('data: '):
                            continue

                        # Remove 'data: ' prefix
                        chunk_text = chunk_text[6:].strip()

                        # Check for the end of the stream
                        if chunk_text == '[DONE]':
                            break

                        # Parse JSON chunk
                        chunk_data = json.loads(chunk_text)
                        delta_content = chunk_data.get('choices', [{}])[0].get('delta', {}).get('content', '')

                        if delta_content:
                            # Update complete response content
                            complete_response["choices"][0]["message"]["content"] += delta_content

                            # Call callback with new content if provided
                            if callback:
                                await callback(delta_content)
                    except json.JSONDecodeError:
                        self.logger.warning(f"Failed to decode chunk as JSON: {chunk_text}")
                    except Exception as e:
                        self.logger.error(f"Error processing streaming chunk: {e}")

            self.logger.debug("Streaming response from Ollama completed")
            return cast(ResponseDict, complete_response)

        except asyncio.TimeoutError as e:
            self.logger.error(f"Timeout error when requesting streaming from Ollama: {e}")
            return cast(ResponseDict, {"error": "timeout", "details": str(e)})
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error in streaming request: {type(e).__name__} - {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in streaming request: {type(e).__name__} - {e}")
            return None

    async def console_stream(self, model: str, messages: list, model_config: Dict[str, Any]) -> Optional[ResponseDict]:
        """
        Stream model output directly to console with real-time updates.

        Args:
            model: Model identifier
            messages: List of message dictionaries
            model_config: Configuration parameters

        Returns:
            Complete response dictionary after streaming completes
        """

        async def print_chunk(chunk):
            """Print chunk to console without line breaks."""
            print(chunk, end='', flush=True)

        print(f"\n[Streaming response from Ollama model: {model}]\n")
        response = await self.stream_chat_completion(
            model, messages, model_config, callback=print_chunk
        )
        print("\n\n[Stream completed]")
        return response

    async def check_model_availability(self, model: str) -> bool:
        """
        Check if a specific model is available in Ollama.

        Args:
            model: Model identifier to check

        Returns:
            True if model is available, False otherwise
        """
        try:
            session = self._ensure_session()

            # Ollama has a /api/tags endpoint to list available models
            tags_url = self.base_url.replace('/v1', '/api/tags')

            async with session.get(tags_url) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    available_models = [m.get('name', '') for m in models]

                    if model in available_models:
                        self.logger.debug(f"Model {model} is available in Ollama")
                        return True
                    else:
                        self.logger.warning(f"Model {model} not found in Ollama. Available: {available_models}")
                        return False
                else:
                    self.logger.error(f"Failed to check Ollama models: HTTP {response.status}")
                    return False
        except Exception as e:
            self.logger.error(f"Error checking Ollama model availability: {e}")
            return False
