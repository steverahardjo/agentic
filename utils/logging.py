import logging
import json
import asyncio
from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel


class LLMLogOutput(BaseModel):
    provider_id: str
    llm_instructions: str
    model: str
    date: datetime
    input: str
    inp_token: int
    response: str
    out_token: int
    app_name: str

    latency_ms: Optional[int] = None
    temperature: Optional[float] = None
    user_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return f"[{self.date}] ({self.app_name}) {self.model} => {self.inp_token}/{self.out_token} tokens"

    def dict_json(self) -> str:
        return self.json()


class LoggingStream:
    enabled: bool = True
    _logger: Optional[logging.Logger] = None

    @classmethod
    def init(cls, filename: str = "global.log") -> logging.Logger:
        if not cls.enabled:
            return

        if cls._logger is None:
            cls._logger = logging.getLogger("LLMLogger")
            cls._logger.setLevel(logging.INFO)

            if not cls._logger.handlers:
                handler = logging.FileHandler(filename, encoding="utf-8")
                formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M")
                handler.setFormatter(formatter)
                cls._logger.addHandler(handler)

        return cls._logger

@classmethod
async def log(cls, message: str | dict | BaseModel):
    if not cls.enabled:
        return

    logger = logging.getLogger("LLMLogger")

    if isinstance(message, BaseModel):
        # Convert Pydantic model to dict with datetime serialized
        message = json.loads(message.model_dump_json())
    elif isinstance(message, dict):
        # Manually convert datetime fields in dict to ISO strings
        def convert(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        message = json.loads(json.dumps(message, default=convert))

    # Run logging in thread-safe async way
    await asyncio.to_thread(logger.info, json.dumps(message, ensure_ascii=False))


    @classmethod
    def log_json(cls, log_obj: Union[LLMLogOutput, dict]):
        """Sync logging fallback for external systems that don't await."""
        if not cls.enabled:
            return

        logger = cls._logger or cls.init()

        if isinstance(log_obj, BaseModel):
            logger.info(log_obj.json())
        elif isinstance(log_obj, dict):
            logger.info(json.dumps(log_obj))
        else:
            logger.info(str(log_obj))
