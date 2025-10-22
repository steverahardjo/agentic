import numpy as np
from typing import List, Union
from enum import Enum
from pydantic import BaseModel


# ---- Vector Entry ----

class VectorEntry(BaseModel):
    text: str
    embedding: np.ndarray
    payload: Union[str, List[str], int, float, Enum, None] = None

    class Config:
        arbitrary_types_allowed = True


class BasicVectorDB:
    def __init__(self, model_instance, db_id: str, model_name: str, usage: str):
        self.model_name = model_name
        self.dimension = model_instance.get_embedding_size(model_name)
        self.model_instance = model_instance
        self.db_id = db_id
        self.usage = usage
        self.entries: List[VectorEntry] = []

    def add(self, texts: List[str], payload):
        for text in texts:
            emb = self.model_instance.get_embeddings(text, self.model_name)
            emb = np.array(emb).squeeze()

            if emb.ndim != 1:
                raise ValueError(f"Invalid embedding shape for: {text} → shape={emb.shape}")
            if emb.shape[0] != self.dimension:
                raise ValueError(f"Embedding dimension mismatch for: {text} → got {emb.shape[0]}, expected {self.dimension}")

            self.entries.append(VectorEntry(text=text, embedding=emb, payload=payload))



    def search(self, query: str, top_k: int = 3) -> List[VectorEntry]:
        query_embedding = self.model_instance.get_embeddings(query, self.model_name)
        if not self.entries:
            return []

        all_embeddings = np.stack([e.embedding for e in self.entries])
        sims = np.dot(all_embeddings, query_embedding) / (
            np.linalg.norm(all_embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-8
        )
        top_indices = sims.argsort()[-top_k:][::-1]
        return [self.entries[i] for i in top_indices]

    def __str__(self):
        return f"This Database || ID: {self.db_id} with Usage: {self.usage}"


class Router:
    def __init__(self, session_name: str, model_inst, model_name: str):
        self.session_name = session_name
        self.model_inst = model_inst
        self.db = BasicVectorDB(model_inst, db_id=session_name, model_name=model_name, usage="router")


    def add_route(self, utterances:List[str], route_name:str|Enum)->None:
        self.db.add(utterances, route_name)

    def diversify_upgrade(self, base_command: str, decoder_model: Union[str, List[str]]):
        prompt = (
            "You are a helpful language model tasked with generating natural, diverse rephrasings "
            "of a given example. The goal is to create multiple unique, high-quality variants that preserve "
            "the original meaning but differ in tone, phrasing, or structure.\n\n"
            f"Semantic List:\n{[e.text for e in self.db.entries]}\n\n"
            f"Base command:\n{base_command}\n\n"
            "Generate at least 5 diverse rephrasings of the command."
        )

        result = self.model_inst.get_result(semantic=prompt)
        if isinstance(result, str):
            result = [result]

        return result

    def similarity_search(self, query: str) -> str|Enum:
        top_1= self.db.search(query, 3)[0]
        return top_1.payload
