"""
Custom LangChain-compatible wrapper for OpenRouter API
"""
from typing import Any, List, Optional
import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration


class OpenRouterLLM(BaseChatModel):
    """
    Custom ChatModel wrapper for OpenRouter API using direct HTTP requests
    """
    
    def __init__(self, **kwargs):
        super().__init__()
        
        # Store parameters
        self._model_name = kwargs.get('model', "mistralai/mistral-7b-instruct:free")
        self._temperature = kwargs.get('temperature', 0.1)
        self._max_tokens = kwargs.get('max_tokens', 2000)
        self._api_key = kwargs.get('api_key')
        self._base_url = kwargs.get('base_url', 'https://openrouter.ai/api/v1')
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat completion using direct HTTP requests"""
        
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
            elif isinstance(msg, AIMessage):
                role = "assistant"
            elif isinstance(msg, SystemMessage):
                role = "system"
            else:
                role = "user"
            
            openai_messages.append({
                "role": role,
                "content": msg.content
            })
        
        # Build request payload
        payload = {
            "model": self._model_name,
            "messages": openai_messages,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        if stop:
            payload["stop"] = stop
        
        # Make HTTP request directly
        response = requests.post(
            f"{self._base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "HTTP-Referer": "https://retail-insights.streamlit.app",
                "X-Title": "Retail Insights Assistant",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        # Convert response to LangChain format
        content = result['choices'][0]['message']['content']
        message = AIMessage(content=content)
        generation = ChatGeneration(message=message)
        
        return ChatResult(generations=[generation])
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM"""
        return "openrouter"
    
    @property
    def _identifying_params(self) -> dict:
        """Return identifying parameters"""
        return {
            "model_name": self._model_name,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens
        }
