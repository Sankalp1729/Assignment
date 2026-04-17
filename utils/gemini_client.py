"""
Clean, reusable Gemini API client.
Loads API key securely from environment.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠ google-generativeai not installed. Run: pip install google-generativeai")


class GeminiClient:
    """Simple, reusable Gemini API wrapper."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: API key (defaults to GOOGLE_API_KEY env var)
            model: Model name (default: gemini-2.0-flash)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. "
                "Please set it in .env file or pass as parameter."
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
    
    def ask(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Send prompt to Gemini and get response.
        
        Args:
            prompt: The prompt to send
            temperature: Model temperature (0-1, default 0.3 for consistency)
            
        Returns:
            Response text from Gemini
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                ),
            )
            return response.text.strip()
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def ask_json(self, prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """
        Ask Gemini for JSON response and parse it CLEANLY.
        
        Handles messy Gemini output by extracting valid JSON.
        
        Args:
            prompt: Prompt requesting JSON output
            temperature: Model temperature (lower = more consistent JSON)
            
        Returns:
            Parsed JSON as dictionary, or error dict if parsing fails
        """
        response_text = self.ask(prompt, temperature=temperature)
        
        # Try multiple extraction strategies
        json_str = None
        
        # Strategy 1: Look for markdown JSON blocks
        if "```json" in response_text:
            try:
                json_str = response_text.split("```json")[1].split("```")[0].strip()
            except:
                pass
        
        # Strategy 2: Look for any markdown code blocks
        if not json_str and "```" in response_text:
            try:
                parts = response_text.split("```")
                for part in parts:
                    if part.strip().startswith("{"):
                        json_str = part.strip()
                        break
            except:
                pass
        
        # Strategy 3: Find first { and last } in response
        if not json_str:
            try:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end].strip()
            except:
                pass
        
        # Strategy 4: Use entire response if it looks like JSON
        if not json_str and response_text.strip().startswith("{"):
            json_str = response_text.strip()
        
        # Try to parse the extracted JSON
        if json_str:
            try:
                # Clean up any trailing commas or other issues
                cleaned = json_str.rstrip().rstrip(",")
                parsed = json.loads(cleaned)
                return parsed
            except json.JSONDecodeError as e:
                print(f"  ⚠ JSON parse error: {e}")
                print(f"    Attempted to parse: {json_str[:100]}...")
                return {
                    "error": "JSON parse failed",
                    "raw_response": response_text[:200],
                    "parse_error": str(e)
                }
        else:
            # No JSON found
            return {
                "error": "No JSON found in response",
                "raw_response": response_text[:200]
            }
    
    def ask_json_with_retry(
        self, 
        prompt: str, 
        max_retries: int = 2,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Ask for JSON with automatic retry on parse failure.
        
        Args:
            prompt: Prompt requesting JSON
            max_retries: Number of retries (default 2)
            temperature: Model temperature
            
        Returns:
            Parsed JSON or error dictionary
        """
        for attempt in range(max_retries + 1):
            result = self.ask_json(prompt, temperature=temperature)
            
            # Success if no error key
            if "error" not in result:
                return result
            
            # Retry with clarification
            if attempt < max_retries:
                prompt += "\n\nPrevious attempt failed. Please ensure valid JSON format."
        
        return result  # Return last attempt result


def get_gemini_client(api_key: Optional[str] = None) -> Optional[GeminiClient]:
    """
    Factory function to get Gemini client.
    Returns None if Gemini not available or key not set.
    
    Args:
        api_key: Optional API key override
        
    Returns:
        GeminiClient instance or None
    """
    if not GEMINI_AVAILABLE:
        print("⚠ Gemini not available")
        return None
    
    try:
        return GeminiClient(api_key=api_key)
    except ValueError as e:
        print(f"⚠ Gemini setup failed: {e}")
        return None


# Convenient singleton-like access
_client: Optional[GeminiClient] = None

def init_gemini(api_key: Optional[str] = None) -> bool:
    """
    Initialize global Gemini client.
    
    Args:
        api_key: Optional API key override
        
    Returns:
        True if successful, False otherwise
    """
    global _client
    _client = get_gemini_client(api_key)
    return _client is not None


def ask_gemini(prompt: str) -> str:
    """
    Quick function to ask Gemini using global client.
    
    Args:
        prompt: The prompt
        
    Returns:
        Response text
    """
    global _client
    if _client is None:
        if not init_gemini():
            return "ERROR: Gemini not initialized"
    return _client.ask(prompt)


def ask_gemini_json(prompt: str) -> Any:
    """
    Quick function to ask Gemini for JSON using global client.
    
    Args:
        prompt: Prompt requesting JSON
        
    Returns:
        Parsed JSON list
    """
    global _client
    if _client is None:
        if not init_gemini():
            return []
            
    response_text = _client.ask(prompt)
    print("RAW GEMINI RESPONSE:", response_text)  # DEBUG
    
    try:
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        json_text = response_text[start:end]
        
        return json.loads(json_text)
    except Exception as e:
        print("JSON parsing failed:", e)
        return []
