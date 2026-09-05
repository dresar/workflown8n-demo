"""
AI Service Integration Module
Handles communication with Gemini AI and Groq AI APIs.
"""
import google.generativeai as genai
from groq import Groq
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """
    Wrapper for Google Gemini AI API.
    Supports text generation using various Gemini models.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini service with API key.
        
        Args:
            api_key: Google Gemini API key
        """
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.api_key = api_key
    
    def generate_text(self, prompt: str, model: str = "gemini-pro", 
                     temperature: float = 0.7, max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Generate text using Gemini AI.
        
        Args:
            prompt: The input prompt for text generation
            model: Model name (default: gemini-pro)
            temperature: Creativity control (0.0-1.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dict with 'success', 'text', and optional 'error' keys
        """
        try:
            # Initialize the model
            ai_model = genai.GenerativeModel(model)
            
            # Generate content
            response = ai_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            # Extract text from response
            if response.candidates:
                generated_text = response.text
                logger.info(f"Gemini generation successful. Length: {len(generated_text)}")
                
                return {
                    'success': True,
                    'text': generated_text,
                    'model': model,
                    'usage': {
                        'prompt_tokens': response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                        'completion_tokens': response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    }
                }
            else:
                error_msg = "No candidates in response"
                logger.warning(f"Gemini generation failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
        
        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def analyze_text(self, text: str, instruction: str = "Analyze this text") -> Dict[str, Any]:
        """
        Analyze text with specific instruction.
        
        Args:
            text: Text to analyze
            instruction: Analysis instruction
        
        Returns:
            Analysis result dictionary
        """
        prompt = f"{instruction}\n\nText to analyze:\n{text}"
        return self.generate_text(prompt)


class GroqService:
    """
    Wrapper for Groq AI API.
    Supports fast inference with various open-source models.
    """
    
    AVAILABLE_MODELS = [
        "mixtral-8x7b-32768",
        "llama2-70b-4096",
        "gemma-7b-it",
    ]
    
    def __init__(self, api_key: str):
        """
        Initialize Groq service with API key.
        
        Args:
            api_key: Groq API key
        """
        if not api_key:
            raise ValueError("Groq API key is required")
        
        self.client = Groq(api_key=api_key)
        self.api_key = api_key
    
    def generate_text(self, prompt: str, model: str = "mixtral-8x7b-32768",
                     temperature: float = 0.7, max_tokens: int = 1024,
                     system_message: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate text using Groq AI.
        
        Args:
            prompt: The input prompt for text generation
            model: Model name (default: mixtral-8x7b-32768)
            temperature: Creativity control (0.0-2.0)
            max_tokens: Maximum tokens to generate
            system_message: Optional system message for context
        
        Returns:
            Dict with 'success', 'text', and optional 'error' keys
        """
        try:
            # Prepare messages
            messages = []
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract response text
            if response.choices:
                generated_text = response.choices[0].message.content
                logger.info(f"Groq generation successful. Length: {len(generated_text)}")
                
                return {
                    'success': True,
                    'text': generated_text,
                    'model': model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens,
                    }
                }
            else:
                error_msg = "No choices in response"
                logger.warning(f"Groq generation failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }
        
        except Exception as e:
            error_msg = f"Groq API error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def chat(self, messages: list, model: str = "mixtral-8x7b-32768",
             temperature: float = 0.7, max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Have a conversation using Groq AI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Creativity control
            max_tokens: Maximum tokens to generate
        
        Returns:
            Response dictionary
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            if response.choices:
                return {
                    'success': True,
                    'text': response.choices[0].message.content,
                    'model': model,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens,
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from API'
                }
        
        except Exception as e:
            error_msg = f"Groq chat error: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }


class AIServiceFactory:
    """
    Factory class to create AI service instances based on provider.
    """
    
    @staticmethod
    def create(provider: str, api_key: str):
        """
        Create an AI service instance.
        
        Args:
            provider: 'gemini' or 'groq'
            api_key: API key for the service
        
        Returns:
            GeminiService or GroqService instance
        
        Raises:
            ValueError: If provider is not supported
        """
        provider = provider.lower()
        
        if provider == 'gemini':
            return GeminiService(api_key)
        elif provider == 'groq':
            return GroqService(api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

