from openai import OpenAI
from typing import Optional, Dict, Any


class LLMClient:
    """Handles communication with the LLM API for translation and summarization."""

    def __init__(self, base_url: str, api_key: str, model: str, max_tokens: int = 16000, temperature: float = 0.3, timeout: int = 300):
        """
        Initialize LLM client.

        Args:
            base_url: API base URL
            api_key: API key for authentication
            model: Model name to use
            max_tokens: Maximum tokens for response
            temperature: Temperature for generation
            timeout: Request timeout in seconds
        """
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout
        )
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

    def _call_llm(self, prompt: str) -> Optional[str]:
        """
        Make a call to the LLM API.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Response text or None if failed
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                print("Error: No response from LLM")
                return None

        except Exception as e:
            print(f"Error calling LLM API: {str(e)}")
            return None

    def translate(self, content: str, prompt_template: str, output_language: str) -> Optional[str]:
        """
        Translate content using the LLM.

        Args:
            content: Text content to translate
            prompt_template: Prompt template with placeholders
            output_language: Target language for translation

        Returns:
            Translated text or None if failed
        """
        # Format the prompt with content and language
        prompt = prompt_template.format(
            content=content,
            output_language=output_language
        )

        return self._call_llm(prompt)

    def summarize(self, content: str, prompt_template: str, output_language: str) -> Optional[str]:
        """
        Summarize content using the LLM.

        Args:
            content: Text content to summarize
            prompt_template: Prompt template with placeholders
            output_language: Language for the summary

        Returns:
            Summary text or None if failed
        """
        # Format the prompt with content and language
        prompt = prompt_template.format(
            content=content,
            output_language=output_language
        )

        return self._call_llm(prompt)

    def process(self, content: str, task_type: str, prompt_template: str, output_language: str) -> Optional[str]:
        """
        Generic processing method that routes to appropriate handler.

        Args:
            content: Text content to process
            task_type: Type of task ("translate" or "summarize")
            prompt_template: Prompt template with placeholders
            output_language: Target language

        Returns:
            Processed text or None if failed
        """
        if task_type == "translate":
            return self.translate(content, prompt_template, output_language)
        elif task_type == "summarize":
            return self.summarize(content, prompt_template, output_language)
        else:
            print(f"Error: Unknown task type '{task_type}'")
            return None
