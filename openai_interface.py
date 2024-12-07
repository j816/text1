# project_root/openai_interface.py
import openai
from typing import List, Dict, Any

class OpenAIInterface:
    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        # Initialize the OpenAI client with the API key
        openai.api_key = api_key

    def refresh_models(self) -> List[str]:
        """Fetch available models from OpenAI API and filter for chat/GPT models."""
        try:
            # Get list of available models
            models = openai.models.list()
            # Filter models to include only GPT/chat models
            filtered = [
                m.id for m in models 
                if ("gpt" in m.id.lower() or "chat" in m.id.lower()) 
                and not any(x in m.id.lower() for x in ["realtime", "audio", "whisper"])
            ]
            return sorted(filtered)
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            # Return a default list if API call fails
            return ["gpt-4", "gpt-3.5-turbo"]

    def send_text(self, prompt: str) -> Dict[str, Any]:
        """Send text to OpenAI API using the chat completions endpoint."""
        try:
            # Create a system message to help guide the model
            messages = [
                {"role": "system", "content": "You are a helpful assistant analyzing text based on provided criteria."},
                {"role": "user", "content": prompt}
            ]
            
            # Make the API call using the chat completions endpoint
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                # Add reasonable max tokens limit
                max_tokens=2000
            )
            
            # Extract and return the response content
            if response.choices and len(response.choices) > 0:
                return {
                    "content": response.choices[0].message.content,
                    "finish_reason": response.choices[0].finish_reason,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            else:
                return {"error": "No response generated"}
                
        except Exception as e:
            return {"error": f"API Error: {str(e)}"}
