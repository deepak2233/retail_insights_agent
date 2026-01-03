"""
Custom LangChain-compatible wrapper for OpenRouter API
"""
from typing import Any, List, Optional
import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration


# Free models to try in order of preference
OPENROUTER_FALLBACK_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "openchat/openchat-7b:free",
]


class OpenRouterLLM(BaseChatModel):
    """
    Custom ChatModel wrapper for OpenRouter API using direct HTTP requests
    with automatic fallback to other free models on rate limits
    """
    
    def __init__(self, **kwargs):
        super().__init__()
        
        # Store parameters
        self._model_name = kwargs.get('model', "google/gemini-2.0-flash-exp:free")
        self._temperature = kwargs.get('temperature', 0.1)
        self._max_tokens = kwargs.get('max_tokens', 2000)
        self._api_key = kwargs.get('api_key')
        self._base_url = kwargs.get('base_url', 'https://openrouter.ai/api/v1')
    
    def _make_request(self, model: str, openai_messages: List[dict], stop: Optional[List[str]] = None) -> requests.Response:
        """Make a single API request"""
        payload = {
            "model": model,
            "messages": openai_messages,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        if stop:
            payload["stop"] = stop
        
        return requests.post(
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
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat completion with automatic fallback on rate limits"""
        
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
        
        # Try primary model first
        models_to_try = [self._model_name] + [m for m in OPENROUTER_FALLBACK_MODELS if m != self._model_name]
        last_error = None
        
        for model in models_to_try:
            try:
                response = self._make_request(model, openai_messages, stop)
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    message = AIMessage(content=content)
                    generation = ChatGeneration(message=message)
                    
                    if model != self._model_name:
                        # Log that we used a fallback
                        try:
                            import streamlit as st
                            st.info(f"✅ Used fallback model: {model}")
                        except:
                            pass
                    
                    return ChatResult(generations=[generation])
                
                elif response.status_code == 429:
                    # Rate limited, try next model
                    last_error = f"Rate limited on {model}"
                    try:
                        import streamlit as st
                        st.warning(f"⚠️ {model} rate limited, trying next...")
                    except:
                        pass
                    continue
                else:
                    last_error = f"OpenRouter API error: {response.status_code} - {response.text}"
                    continue
                    
            except Exception as e:
                last_error = str(e)
                continue
        
        # All models failed
        raise Exception(f"All models failed. Last error: {last_error}")
    
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
