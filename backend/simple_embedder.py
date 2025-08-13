import hashlib
import numpy as np
from agno.embedder.base import Embedder

class SimpleEmbedder(Embedder):
    """Simple embedder that creates basic embeddings without external dependencies"""
    
    def __init__(self, dimensions: int = 768):
        self.dimensions = dimensions
    
    def get_embedding(self, text: str) -> list[float]:
        """Create a simple embedding based on text hash"""
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to a list of numbers
        numbers = []
        for i in range(0, len(text_hash), 2):
            if len(numbers) >= self.dimensions:
                break
            hex_pair = text_hash[i:i+2]
            numbers.append(int(hex_pair, 16) / 255.0)  # Normalize to 0-1
        
        # Pad or truncate to required dimensions
        while len(numbers) < self.dimensions:
            numbers.append(0.0)
        
        return numbers[:self.dimensions]
    
    def get_embedding_and_usage(self, text: str) -> tuple[list[float], dict]:
        """Get embedding and usage info"""
        embedding = self.get_embedding(text)
        usage = {"tokens": len(text.split()), "model": "simple_embedder"}
        return embedding, usage
