from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from qdrant_client import QdrantClient, models
from llm.LLM import LanguageModel
import uuid
import os


class MemoryEngine(ABC):
    def __init__(self, memory_id: str, allowed_agent: List[str]):
        self.memory_id = memory_id
        self.allowed_agent = allowed_agent

    @abstractmethod
    def add(self, agent_id: str, item: Optional[str]) -> None:
        pass

    @abstractmethod
    def retrieve(self, agent_id: str, query: Optional[str]) -> List[str]:
        pass

    @abstractmethod
    def clear(self, agent_id: str) -> None:
        pass

    def is_agent_allowed(self, agent_id: str) -> bool:
        return agent_id in self.allowed_agent

    def __str__(self):
        return f"memory_id:{self.memory_id}, allowed_agent:{', '.join(self.allowed_agent)}"

class VectorMemory(MemoryEngine):
    def __init__(self, memory_id: str, allowed_agent: List[str], llm_model: LanguageModel, qdrant_url: str):
        super().__init__(memory_id, allowed_agent)
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = self.memory_id
        self.model = llm_model

    def add(self, agent_id: str, item: Optional[str]) -> None:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to write to memory: {self.memory_id}")

        embeddings = self.model.get_embeddings(item)

        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE)
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=uuid.uuid4().int >> 64,
                    payload={"text": item},
                    vector=embeddings
                )
            ]
        )

    def retrieve(self, agent_id: str, query: Optional[str]) -> List[str]:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to read from memory: {self.memory_id}")

        embeddings = self.model.get_embeddings(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=embeddings,
            limit=3
        )
        return [hit.payload['text'] for hit in results] or ""

    def clear(self, agent_id: str) -> None:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to clear memory: {self.memory_id}")
        self.client.delete_collection(collection_name=self.collection_name)

class InMemory(MemoryEngine):
    def __init__(self, memory_id: str, allowed_agent: List[str]):
        super().__init__(memory_id, allowed_agent)
        self.memory_store = {}

    def add(self, agent_id: str, item: Optional[str]) -> None:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to write to memory: {self.memory_id}")
        self.memory_store[uuid.uuid4().hex] = item

    def retrieve(self, agent_id: str, query: Optional[str]) -> List[str]:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to read from memory: {self.memory_id}")
        if not query:
            return list(self.memory_store.values())
        return [value for value in self.memory_store.values() if query.lower() in value.lower()] or ""

    def clear(self, agent_id: str) -> None:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to clear memory: {self.memory_id}")
        self.memory_store.clear()

class MdMemory(MemoryEngine):
    def __init__(self, memory_id: str, allowed_agent: List[str], md_path: str):
        super().__init__(memory_id, allowed_agent)
        self.md_path = md_path
        self.memory_log = []

        # Load existing log if exists
        if os.path.exists(self.md_path):
            with open(self.md_path, 'r') as f:
                self.memory_log = f.readlines()

    def add(self, agent_id: str, item: Optional[str]) -> None:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to write to memory: {self.memory_id}")
        entry = f"## ({agent_id} - {datetime.now()})\n{item}\n"
        self.memory_log.append(entry)
        with open(self.md_path, 'a') as f:
            f.write(entry + "\n")

    def retrieve(self, agent_id: str, query: Optional[str]) -> List[str]:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to read from memory: {self.memory_id}")

        if not query:
            return [line.strip() for line in self.memory_log]

        return [line.strip() for line in self.memory_log if query.lower() in line.lower()] or ""

    def clear(self, agent_id: str) -> None:
        if not self.is_agent_allowed(agent_id):
            raise PermissionError(f"Agent: {agent_id} not allowed to clear memory: {self.memory_id}")
        self.memory_log.clear()
        with open(self.md_path, 'w') as f:
            f.write(f"# Memory Log: {self.memory_id} (cleared by {agent_id})\n\n")





