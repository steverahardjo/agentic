from typing import Union, List, Dict
from datetime import datetime
import os
import logging
import requests
from openai import OpenAI
from together import Together
import ollama
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# === Base Abstract Class for all Language Model Clients ===
class LanguageModel(ABC):
    """
    Abstract base class that defines the interface for language model clients.

    Subclasses must implement `get_result()` and `get_embedding_size()`.
    Optional: `get_embeddings()` if the provider supports embeddings.
    """

    def __init__(self, llm_inst_id: str, decoder_model: str, encoder_model: str):
        """
        Initialize a base language model instance.

        Args:
            llm_inst_id (str): Unique ID for the LLM instance.
            decoder_model (str): Model used for generation (e.g., GPT-4, Mixtral).
            encoder_model (str): Model used for embeddings (e.g., text-embedding-3-small).
        """
        self.llm_inst_id = llm_inst_id
        self.decoder = decoder_model
        self.encoder = encoder_model

    @abstractmethod
    def get_result(self, semantic: Union[str, Dict[str, str], List[Dict[str, str]]], temp: float = 0.6) -> str:
        """
        Generate a completion result based on input prompt.

        Args:
            semantic (Union[str, Dict, List[Dict]]): Input content (can be plain text or chat message format).
            temp (float): Temperature for randomness (default: 0.6).

        Returns:
            str: Generated text output.
        """
        pass

    def get_embeddings(self, semantic: Union[List[Dict[str, str]], str]):
        """
        Generate embeddings for a given text or structured prompt.

        Args:
            semantic (Union[List[Dict], str]): Text or list of role-content dicts.

        Raises:
            NotImplementedError: If not supported for this model.
        """
        raise NotImplementedError("Embedding not implemented for this model.")

    @abstractmethod
    def get_embedding_size(self) -> int:
        """
        Return the dimensionality of the encoder model embeddings.

        Returns:
            int: Embedding vector length.
        """
        pass

    def set_encoder(self, embed_model: str) -> None:
        """
        Set or change the encoder model.

        Args:
            embed_model (str): Model name for embedding.
        """
        self.encoder = embed_model

    def set_decoder(self, decoder_model: str) -> None:
        """
        Set or change the decoder (chat/completion) model.

        Args:
            decoder_model (str): Model name for decoding.
        """
        self.decoder = decoder_model

    def get_model_series(self) -> str:
        """
        Return the name or family of the decoder model.

        Returns:
            str: Decoder model identifier.
        """
        return self.decoder


# === Utility Function to Normalize Prompt Format ===
def normalize_prompt(semantic: Union[str, Dict[str, str], List[Dict[str, str]]]) -> List[Dict[str, str]]:
    """
    Convert input into the standard message list format expected by chat models.

    Args:
        semantic (Union[str, Dict, List[Dict]]): Input text or structured messages.

    Returns:
        List[Dict[str, str]]: Normalized list of messages with 'role' and 'content' keys.
    """
    if isinstance(semantic, str):
        return [{"role": "user", "content": semantic}]
    elif isinstance(semantic, dict):
        return [semantic]
    elif isinstance(semantic, list):
        return semantic
    else:
        raise ValueError("semantic must be str, dict, or list of dicts")


# === OpenAI Implementation ===
class OpenAIClient(LanguageModel):
    """
    Client for interacting with OpenAI's API.
    Supports chat completions and embeddings.
    """

    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str, api_key: str = None):
        """
        Args:
            llm_inst_id (str): Instance identifier for tracking.
            encoder_model (str): Embedding model name.
            decoder_model (str): Chat/completion model name.
            api_key (str, optional): API key (defaults to OPENAI_API_KEY env var).
        """
        super().__init__(llm_inst_id, decoder_model, encoder_model)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing OpenAI API key")
        self.client = OpenAI(api_key=self.api_key)

    def get_result(self, semantic, temp: float = 0.6) -> str:
        """
        Send a chat completion request to OpenAI.

        Args:
            semantic (Union[str, Dict, List[Dict]]): Prompt text or structured message(s).
            temp (float): Temperature for randomness (default: 0.6).

        Returns:
            str: The generated completion text.
        """
        messages = normalize_prompt(semantic)
        response = self.client.chat.completions.create(
            model=self.decoder,
            messages=messages,
            temperature=temp
        )
        result = response.choices[0].message.content
        log = self._parse_log(messages, result, response.usage, self.decoder)
        # LoggingStream.log_json(log.dict())  # Optional logging hook
        return result

    def get_embeddings(self, semantic):
        """
        Create embeddings for the given text.

        Args:
            semantic (Union[str, List[Dict]]): Input text or structured content.

        Returns:
            List[float]: The embedding vector.
        """
        response = self.client.embeddings.create(
            model=self.encoder,
            input=semantic,
            encoding_format="float"
        )
        return response.data[0].embedding

    def get_embedding_size(self) -> int:
        """Test embedding dimension using a sample string."""
        emb = self.get_embeddings("hello world")
        logger.info(f"Embedding size = {len(emb)}")
        return len(emb)

    def get_model_series(self) -> str:
        return "OpenAI"

    def _parse_log(self, messages, result, usage, model: str):
        """
        Construct a structured log entry for model activity.

        Args:
            messages (List[Dict]): Prompt messages.
            result (str): Model output.
            usage: API usage object (contains token counts).
            model (str): Model name.

        Returns:
            LLMLogOutput: Structured log object.
        """
        from utils.logging import LLMLogOutput
        return LLMLogOutput(
            provider_id="openai",
            llm_instructions=messages[0]["content"] if messages else "",
            model=model,
            date=datetime.now(),
            input=messages[0]["content"] if messages else "",
            inp_token=usage.prompt_tokens,
            response=result,
            out_token=usage.completion_tokens,
            app_name="llm_router"
        )


# === Together AI Implementation ===
class TogetherClient(LanguageModel):
    """
    Client for Together.ai API.
    Supports chat completions and embeddings.
    """

    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str, api_key: str = None):
        """
        Args:
            llm_inst_id (str): Instance ID for tracking.
            encoder_model (str): Embedding model name.
            decoder_model (str): Generation model name.
            api_key (str, optional): API key (defaults to TOGETHER_API_KEY env var).
        """
        super().__init__(llm_inst_id, decoder_model, encoder_model)
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing Together API key.")
        self.client = Together(api_key=self.api_key)

    def get_result(self, semantic, temp: float = 0.6) -> str:
        """
        Request a completion from Together API.

        Args:
            semantic (Union[str, Dict, List[Dict]]): Prompt content.
            temp (float): Sampling temperature.

        Returns:
            str: Model-generated output.
        """
        messages = normalize_prompt(semantic)
        response = self.client.chat.completions.create(model=self.decoder, messages=messages, temperature=temp)
        result = response.choices[0].message.content
        log = self._parse_log(messages, result, response.usage, self.decoder)
        # LoggingStream.log_json(log.dict())
        return result

    def get_embeddings(self, semantic):
        """
        Generate embeddings for input text.

        Args:
            semantic (Union[str, List[Dict]]): Input text.

        Returns:
            List[float]: Embedding vector.
        """
        response = self.client.embeddings.create(model=self.encoder, input=semantic)
        return response.data[0].embedding

    def get_embedding_size(self) -> int:
        """Get embedding vector size using test input."""
        emb = self.get_embeddings("hello world")
        logger.info(f"Embedding size = {len(emb)}")
        return len(emb)

    def get_model_series(self) -> str:
        return "TogetherAI"

    def _parse_log(self, messages, result, usage, model: str):
        """Format Together API log output."""
        from utils.logging import LLMLogOutput
        return LLMLogOutput(
            provider_id="together",
            llm_instructions=messages[0]["content"] if messages else "",
            model=model,
            date=datetime.now(),
            input=messages[0]["content"] if messages else "",
            inp_token=usage.prompt_tokens,
            response=result,
            out_token=usage.completion_tokens,
            app_name="llm_router"
        )


# === OpenRouter Implementation ===
class OpenRouterClient(LanguageModel):
    """
    Client for OpenRouter API.
    Only supports chat completions (no embeddings).
    """

    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str, api_key: str = None, referer: str = None, title: str = None):
        """
        Args:
            llm_inst_id (str): Unique instance identifier.
            encoder_model (str): Placeholder (not supported).
            decoder_model (str): Chat model name.
            api_key (str, optional): API key (defaults to OPENROUTER_API_KEY).
            referer (str, optional): HTTP referer header.
            title (str, optional): Display title for client.
        """
        super().__init__(llm_inst_id, decoder_model, encoder_model)
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OpenRouter API key")

        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.header = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": referer or "",
            "X-Title": title or "llm-router",
            "Content-Type": "application/json"
        }

    def get_result(self, semantic, temp: float = 0.6) -> str:
        """
        Send a completion request to OpenRouter.

        Args:
            semantic (Union[str, Dict, List[Dict]]): Input prompt.
            temp (float): Temperature for generation.

        Returns:
            str: Model output text.
        """
        messages = normalize_prompt(semantic)
        payload = {"model": self.decoder, "messages": messages, "temperature": temp}

        res = requests.post(self.url, headers=self.header, json=payload)
        res.raise_for_status()
        result_text = res.json()["choices"][0]["message"]["content"]
        log = self._parse_log(messages, result_text, self.decoder)
        # LoggingStream.log_json(log.dict())
        return result_text

    def get_embeddings(self, semantic):
        raise NotImplementedError("Embedding not supported for OpenRouter.")

    def get_embedding_size(self) -> int:
        raise NotImplementedError("Embedding size not supported for OpenRouter.")

    def get_model_series(self) -> str:
        return "OpenRouter"

    def _parse_log(self, messages, result, model: str):
        """Construct log entry for OpenRouter interactions."""
        from utils.logging import LLMLogOutput
        return LLMLogOutput(
            provider_id="openrouter",
            llm_instructions=messages[0]["content"] if messages else "",
            model=model,
            date=datetime.now(),
            input=messages[0]["content"] if messages else "",
            inp_token=0,
            response=result,
            out_token=0,
            app_name="llm_router"
        )


# === Ollama Local LLM Implementation ===
class OllamaClient(LanguageModel):
    """
    Client wrapper for local Ollama models.
    Uses local inference for chat completions only.
    """

    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str):
        """
        Args:
            llm_inst_id (str): Unique instance ID.
            encoder_model (str): Placeholder encoder (not used).
            decoder_model (str): Ollama model name (e.g., llama3, mistral).
        """
        super().__init__(llm_inst_id, decoder_model, encoder_model)

    def get_result(self, semantic, temp: float = 0.6) -> str:
        """
        Generate a response using a local Ollama model.

        Args:
            semantic (Union[str, Dict, List[Dict]]): Input text or message list.
            temp (float): Unused (for compatibility).

        Returns:
            str: Generated response text.
        """
        messages = normalize_prompt(semantic)
        reply = ollama.chat(model=self.decoder, messages=messages)
        return reply

    def get_embeddings(self, semantic):
        raise NotImplementedError("Embedding not implemented for Ollama.")

    def get_embedding_size(self) -> int:
        raise NotImplementedError("Embedding size not supported for Ollama.")

    def get_model_series(self) -> str:
        return "Ollama"

    def _parse_log(self, messages, result, model: str):
        """Format structured Ollama log."""
        from utils.logging import LLMLogOutput
        return LLMLogOutput(
            provider_id="ollama",
            llm_instructions=messages[0]["content"] if messages else "",
            model=model,
            date=datetime.now(),
            input=messages[0]["content"] if messages else "",
            inp_token=0,
            response=result,
            out_token=0,
            app_name="llm_router"
        )
