"""
LLM utilities for agent system
"""
from typing import Optional, List, Any, Iterator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun

# Try to import Google Gemini, but make it optional
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    ChatGoogleGenerativeAI = None

from config import settings, get_secret


# Fallback models for Gemini (in order of preference)
# Using correct model names for Google AI API
GEMINI_FALLBACK_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest", 
    "gemini-1.5-pro-latest",
    "gemini-pro",
]


class GeminiFallbackLLM(BaseChatModel):
    """
    A wrapper LLM that automatically falls back to alternative Gemini models
    when rate limits (429) or other errors occur.
    Inherits from BaseChatModel for full LangChain compatibility.
    """
    
    primary_model: str = "gemini-2.0-flash"
    temperature: float = 0.1
    max_output_tokens: int = 2000
    api_key: str = ""
    current_model: str = ""
    _llm: Any = None
    
    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
    
    def __init__(self, primary_model: str, temperature: float, max_output_tokens: int, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.primary_model = primary_model
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.api_key = api_key
        self.current_model = primary_model
        self._create_llm(primary_model)
    
    @property
    def _llm_type(self) -> str:
        return "gemini-fallback"
    
    @property
    def _identifying_params(self) -> dict:
        return {
            "primary_model": self.primary_model,
            "current_model": self.current_model,
            "temperature": self.temperature,
        }
    
    def _create_llm(self, model: str):
        """Create a new LLM instance with the specified model."""
        self._llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            google_api_key=self.api_key
        )
        self.current_model = model
    
    def _get_fallback_models(self) -> List[str]:
        """Get list of fallback models to try (excluding current model)."""
        models = []
        for m in GEMINI_FALLBACK_MODELS:
            if m != self.current_model and m not in models:
                models.append(m)
        return models
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate chat response with automatic fallback on rate limit or model not found errors."""
        try:
            import streamlit as st
            has_streamlit = True
        except:
            has_streamlit = False
        
        def should_fallback(error_str: str) -> bool:
            """Check if error warrants trying a fallback model."""
            error_lower = error_str.lower()
            return (
                "429" in error_str or 
                "404" in error_str or
                "quota" in error_lower or 
                "rate" in error_lower or
                "not found" in error_lower or
                "not supported" in error_lower
            )
        
        # Try primary model first
        try:
            return self._llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        except Exception as e:
            error_str = str(e)
            # Check if it's a rate limit error (429), quota exceeded, or model not found (404)
            if should_fallback(error_str):
                if has_streamlit:
                    st.warning(f"⚠️ Error with {self.current_model}, trying fallback models...")
                
                # Try fallback models
                for fallback_model in self._get_fallback_models():
                    try:
                        if has_streamlit:
                            st.info(f"🔄 Trying fallback model: {fallback_model}")
                        self._create_llm(fallback_model)
                        result = self._llm._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
                        if has_streamlit:
                            st.success(f"✅ Successfully used fallback model: {fallback_model}")
                        return result
                    except Exception as fallback_error:
                        fallback_error_str = str(fallback_error)
                        if should_fallback(fallback_error_str):
                            if has_streamlit:
                                st.warning(f"⚠️ {fallback_model} also failed, trying next...")
                            continue
                        else:
                            raise fallback_error
                
                raise Exception(f"All Gemini models exhausted. Original error: {error_str}")
            else:
                raise e


def get_llm(temperature: Optional[float] = None, model: Optional[str] = None, use_fallback: bool = True):
    """
    Get LLM instance based on configuration
    
    Args:
        temperature: Model temperature (0.0 to 1.0)
        model: Model name (optional override)
        use_fallback: Whether to use fallback mechanism for Gemini (default: True)
        
    Returns:
        LLM instance
    """
    temp = temperature if temperature is not None else settings.temperature
    
    # Get provider dynamically (supports Streamlit secrets)
    provider = get_secret("LLM_PROVIDER", settings.llm_provider)
    
    if provider == "openai":
        from openai import OpenAI
        
        model_name = model or get_secret("OPENAI_MODEL", settings.openai_model)
        base_url = get_secret("OPENAI_BASE_URL", settings.openai_base_url)
        api_key = get_secret("OPENAI_API_KEY", settings.openai_api_key)
        
        # For OpenRouter, use custom wrapper that properly sets headers
        if base_url and 'openrouter' in base_url:
            from utils.openrouter_llm import OpenRouterLLM
            
            return OpenRouterLLM(
                model=model_name,
                temperature=temp,
                max_tokens=settings.max_tokens,
                api_key=api_key,
                base_url=base_url
            )
        else:
            return ChatOpenAI(
                model=model_name,
                temperature=temp,
                max_tokens=settings.max_tokens,
                api_key=api_key,
                base_url=base_url if base_url else None
            )
    elif provider == "google":
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "Google Gemini is not available. Install with: pip install langchain-google-genai"
            )
        # Get API key dynamically from Streamlit secrets or environment
        api_key = get_secret("GOOGLE_API_KEY")
        model_name = model or get_secret("GEMINI_MODEL", settings.gemini_model)
        
        if not api_key:
            raise ValueError(
                "Google API key not found. Set GOOGLE_API_KEY in environment or Streamlit secrets."
            )
        
        # Use fallback wrapper for automatic model switching on rate limits
        if use_fallback:
            return GeminiFallbackLLM(
                primary_model=model_name,
                temperature=temp,
                max_output_tokens=settings.max_tokens,
                api_key=api_key
            )
        else:
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temp,
                max_output_tokens=settings.max_tokens,
                google_api_key=api_key
            )
    elif provider == "groq":
        model_name = model or get_secret("GROQ_MODEL", settings.groq_model)
        api_key = get_secret("GROQ_API_KEY", settings.groq_api_key)
        
        if not api_key:
            raise ValueError(
                "Groq API key not found. Set GROQ_API_KEY in environment or Streamlit secrets."
            )
            
        return ChatOpenAI(
            model=model_name,
            temperature=temp,
            max_tokens=settings.max_tokens,
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def create_prompt_template(role: str, instructions: str) -> str:
    """
    Create a standardized prompt template
    
    Args:
        role: Agent role
        instructions: Specific instructions for the agent
        
    Returns:
        Formatted prompt template
    """
    return f"""You are a {role} for a Retail Insights Assistant.

{instructions}

Be precise, analytical, and focus on providing actionable insights.
"""
