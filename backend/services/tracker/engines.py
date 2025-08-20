"""
LLM Engine adapters for tracking citations and answers
Based on technical specification section 6.1 LM SEO
"""

import asyncio
import httpx
import json
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime

from backend.common.config import get_settings

settings = get_settings()


@dataclass
class Answer:
    """Structured answer response from an AI engine"""
    raw_text: str
    citations: List[str]  # List of URLs
    confidence: Optional[float] = None
    answer_length: int = 0
    featured_position: bool = False
    timestamp: datetime = None
    engine_version: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.answer_length == 0:
            self.answer_length = len(self.raw_text)


class BaseEngine(ABC):
    """Base class for AI engine adapters"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def query(self, prompt: str, **kwargs) -> Answer:
        """Query the engine with a prompt and return structured answer"""
        pass
    
    def extract_citations(self, text: str) -> List[str]:
        """Extract URLs from answer text using regex patterns"""
        # Common URL patterns in AI responses
        url_patterns = [
            r'https?://[^\s\]]+',  # Basic HTTP URLs
            r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown links
            r'Source:\s*(https?://[^\s]+)',  # Source: format
            r'Reference:\s*(https?://[^\s]+)',  # Reference: format
        ]
        
        urls = []
        for pattern in url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Markdown link format
                    urls.append(match[1])
                else:
                    urls.append(match)
        
        # Clean and validate URLs
        clean_urls = []
        for url in urls:
            url = url.strip('.,;!?)"\'')
            if self._is_valid_url(url):
                clean_urls.append(url)
        
        return list(set(clean_urls))  # Remove duplicates
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if string is a proper URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def normalize_domain(self, url: str) -> str:
        """Extract normalized domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return ""


class PerplexityEngine(BaseEngine):
    """Perplexity AI engine adapter"""
    
    def __init__(self):
        super().__init__("perplexity")
        self.base_url = "https://www.perplexity.ai"
    
    async def query(self, prompt: str, **kwargs) -> Answer:
        """Query Perplexity via web scraping (respecting robots.txt)"""
        # Note: This is a placeholder implementation
        # In production, we'd use official API or browser automation
        
        # Simulate response for development
        await asyncio.sleep(1)  # Simulate network delay
        
        mock_response = f"Based on the query '{prompt}', here are the key findings: [Mock answer content]. Sources: https://example.com/source1, https://example.com/source2"
        
        citations = self.extract_citations(mock_response)
        
        return Answer(
            raw_text=mock_response,
            citations=citations,
            confidence=0.85,
            engine_version="perplexity-2024"
        )


class GeminiEngine(BaseEngine):
    """Google Gemini engine adapter"""
    
    def __init__(self):
        super().__init__("gemini", settings.google_api_key)
        self.model = "gemini-1.5-pro"
    
    async def query(self, prompt: str, **kwargs) -> Answer:
        """Query Gemini via official API"""
        if not self.api_key:
            raise ValueError("Google API key not configured")
        
        # Placeholder implementation - would use Google's Generative AI SDK
        await asyncio.sleep(1.5)
        
        mock_response = f"Gemini analysis for '{prompt}': [Mock comprehensive answer]. References: https://scholar.google.com/source1, https://research.google.com/source2"
        
        citations = self.extract_citations(mock_response)
        
        return Answer(
            raw_text=mock_response,
            citations=citations,
            confidence=0.92,
            engine_version=self.model
        )


class BingCopilotEngine(BaseEngine):
    """Microsoft Bing Copilot engine adapter"""
    
    def __init__(self):
        super().__init__("bing_copilot")
        self.base_url = "https://www.bing.com/chat"
    
    async def query(self, prompt: str, **kwargs) -> Answer:
        """Query Bing Copilot via web interface"""
        # Placeholder implementation
        await asyncio.sleep(2.0)
        
        mock_response = f"Bing Copilot response to '{prompt}': [Mock detailed answer with citations]. Sources: https://microsoft.com/source1, https://docs.microsoft.com/source2"
        
        citations = self.extract_citations(mock_response)
        
        return Answer(
            raw_text=mock_response,
            citations=citations,
            confidence=0.88,
            featured_position=True,
            engine_version="copilot-2024"
        )


class ChatGPTEngine(BaseEngine):
    """OpenAI ChatGPT engine adapter (with browsing)"""
    
    def __init__(self):
        super().__init__("chatgpt", settings.openai_api_key)
        self.model = "gpt-4"
    
    async def query(self, prompt: str, **kwargs) -> Answer:
        """Query ChatGPT with browsing capability"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        # Placeholder implementation
        await asyncio.sleep(1.2)
        
        mock_response = f"ChatGPT analysis (with browsing) for '{prompt}': [Mock answer with web sources]. Sources: https://openai.com/source1, https://help.openai.com/source2"
        
        citations = self.extract_citations(mock_response)
        
        return Answer(
            raw_text=mock_response,
            citations=citations,
            confidence=0.90,
            engine_version=self.model
        )


class ClaudeEngine(BaseEngine):
    """Anthropic Claude engine adapter"""
    
    def __init__(self):
        super().__init__("claude", settings.anthropic_api_key)
        self.model = "claude-3-sonnet-20240229"
    
    async def query(self, prompt: str, **kwargs) -> Answer:
        """Query Claude via official API"""
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")
        
        # Placeholder implementation
        await asyncio.sleep(1.8)
        
        mock_response = f"Claude's response to '{prompt}': [Mock thoughtful analysis]. References: https://anthropic.com/source1, https://docs.anthropic.com/source2"
        
        citations = self.extract_citations(mock_response)
        
        return Answer(
            raw_text=mock_response,
            citations=citations,
            confidence=0.89,
            engine_version=self.model
        )


class EngineManager:
    """Manager for all AI engines"""
    
    def __init__(self):
        self.engines = {
            "perplexity": PerplexityEngine(),
            "gemini": GeminiEngine(),
            "bing_copilot": BingCopilotEngine(),
            "chatgpt": ChatGPTEngine(),
            "claude": ClaudeEngine(),
        }
    
    def get_engine(self, name: str) -> BaseEngine:
        """Get engine by name"""
        if name not in self.engines:
            raise ValueError(f"Engine '{name}' not supported. Available: {list(self.engines.keys())}")
        return self.engines[name]
    
    def list_engines(self) -> List[str]:
        """List all available engines"""
        return list(self.engines.keys())
    
    async def query_engine(self, engine_name: str, prompt: str, **kwargs) -> Answer:
        """Query specific engine"""
        engine = self.get_engine(engine_name)
        return await engine.query(prompt, **kwargs)
    
    async def query_all_engines(self, prompt: str, **kwargs) -> Dict[str, Answer]:
        """Query all engines concurrently"""
        tasks = []
        for name, engine in self.engines.items():
            tasks.append(self._query_with_name(name, engine, prompt, **kwargs))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        answers = {}
        for i, result in enumerate(results):
            engine_name = list(self.engines.keys())[i]
            if isinstance(result, Exception):
                print(f"Error querying {engine_name}: {result}")
                continue
            answers[engine_name] = result
        
        return answers
    
    async def _query_with_name(self, name: str, engine: BaseEngine, prompt: str, **kwargs) -> Answer:
        """Helper to query engine with name tracking"""
        try:
            return await engine.query(prompt, **kwargs)
        except Exception as e:
            print(f"Error in {name}: {e}")
            raise


# Global engine manager instance
engine_manager = EngineManager()