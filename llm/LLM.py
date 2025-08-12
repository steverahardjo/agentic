from abc import ABC, abstractmethod
from typing import Union, List, Dict
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
import requests
from openai import OpenAI
from together import Together
from utils.logging import LLMLogOutput
from utils.logging import LoggingStream
from agentic.prompt_constructor import PromptConstructor
from agentic.tools.code_runner import CodeRunner
import ollama

# Load environment variables
load_dotenv(override=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageModel(ABC):
    def __init__(self, llm_inst_id: str, decoder_model: str, encoder_model: str):
        self.llm_inst_id = llm_inst_id
        self.decoder = decoder_model
        self.encoder = encoder_model

    @abstractmethod
    def get_result(self, semantic: PromptConstructor, temp: float = 0.6) -> str:
        pass

    def get_embeddings(self, semantic: Union[List[Dict[str, str]], str]):
        raise NotImplementedError("Embedding not implemented for this model.")

    @abstractmethod
    def get_embedding_size(self) -> int:
        pass

    def set_encoder(self, embed_model: str) -> None:
        self.encoder = embed_model

    def set_decoder(self, decoder_model: str) -> None:
        self.decoder = decoder_model

    def get_model_series(self):
        return self.decoder

class OpenAIClient(LanguageModel):
    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str, api_key: str = None):
        super().__init__(llm_inst_id, decoder_model, encoder_model)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing OpenAI API key")
        self.client = OpenAI(api_key=self.api_key)
  
    def get_embeddings(self, semantic: Union[str, List[Dict[str, str]]]) -> List[float]:
        response = self.client.embeddings.create(
            model=self.encoder,
            input=semantic,
            encoding_format="float"
        )
        return response.data[0].embedding

    def get_embedding_size(self) -> int:
        emb = self.get_embeddings("hello world")
        logger.info(f"Embedding size = {len(emb)}")
        return len(emb)

    def get_model_series(self) -> str:
        return "OpenAI"

    def _parse_log(self, messages, result, usage, model: str) -> LLMLogOutput:
        return LLMLogOutput(
            provider_id="openai",
            llm_instructions=messages[0]["content"],
            model=model,
            date=datetime.now(),
            input=messages[0]["content"],
            inp_token=usage.prompt_tokens,
            response=result,
            out_token=usage.completion_tokens,
            app_name="llm_router"
        )

class TogetherClient(LanguageModel):
    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str, api_key: str = None):
        super().__init__(llm_inst_id, decoder_model, encoder_model)
        self.api_key = api_key or os.environ.get("TOGETHER_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing Together API key.")
        self.client = Together(api_key=self.api_key)

    def get_result(self, semantic: PromptConstructor, temp: float = 0.6) -> str:
        messages = semantic
        response = self.client.chat.completions.create(model=self.decoder, messages=messages, temperature=temp)
        result = response.choices[0].message.content
        log = self._parse_log(messages, result, response.usage, self.decoder)
        LoggingStream.log_json(log.dict())
        return result

    def get_embeddings(self, semantic: Union[str, List[Dict[str, str]]]) -> List[float]:
        response = self.client.embeddings.create(model=self.encoder, input=semantic)
        return response.data[0].embedding

    def get_embedding_size(self) -> int:
        emb = self.get_embeddings("hello world")
        logger.info(f"Embedding size = {len(emb)}")
        return len(emb)

    def get_model_series(self) -> str:
        return "TogetherAI"

    def _parse_log(self, messages, result, usage, model: str) -> LLMLogOutput:
        return LLMLogOutput(
            provider_id="together",
            llm_instructions=messages[0]["content"],
            model=model,
            date=datetime.now(),
            input=messages[0]["content"],
            inp_token=usage.prompt_tokens,
            response=result,
            out_token=usage.completion_tokens,
            app_name="llm_router"
        )

class OpenRouterClient(LanguageModel):
    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str, api_key: str = None, referer: str = None, title: str = None):
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

    def get_result(self, semantic: PromptConstructor, temp: float = 0.6) -> str:
        messages = semantic
        payload = {"model": self.decoder, "messages": messages, "temperature": temp}

        res = requests.post(self.url, headers=self.header, json=payload)
        res.raise_for_status()
        result_text = res.json()["choices"][0]["message"]["content"]
        log = self._parse_log(messages, result_text, self.decoder)
        LoggingStream.log_json(log.dict())
        return result_text

    def get_embedding_size(self) -> int:
        raise NotImplementedError("Embedding not supported for OpenRouter.")

    def get_model_series(self) -> str:
        return "OpenRouter"

    def _parse_log(self, messages, result, model: str) -> LLMLogOutput:
        return LLMLogOutput(
            provider_id="openrouter",
            llm_instructions=messages[0]["content"],
            model=model,
            date=datetime.now(),
            input=messages[0]["content"],
            inp_token=0,
            response=result,
            out_token=0,
            app_name="llm_router"
        )
class OllamaClient(LanguageModel):
    def __init__(self, llm_inst_id: str, encoder_model: str, decoder_model: str):
        super().__init__(llm_inst_id, decoder_model, encoder_model)


    def get_result(self, semantic: PromptConstructor, temp: float = 0.6) -> str:
        injection = ""
        reply = ollama.chat(model = self.decoder_model, messages=injection)
        return reply
