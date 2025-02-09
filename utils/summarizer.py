import os
from openai import OpenAI
from typing import Optional

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
class TextSummarizer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def summarize_text(self, text: str, max_tokens: int = 150) -> Optional[str]:
        """Generate a concise summary of the provided text"""
        if not os.getenv("OPENAI_API_KEY"):
            return "OpenAI API key not found. Please provide a valid API key to enable summarization."

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise document summarizer. Create a concise summary that captures the key points."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following text:\n\n{text}"
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e)
            print(f"Error in summarization: {error_msg}")
            if "rate limit" in error_msg.lower():
                return "OpenAI API rate limit reached. Please try again in a few moments."
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                return "OpenAI API quota exceeded. Please ensure your account has available credits and billing is set up correctly."
            elif "invalid" in error_msg.lower() and "api" in error_msg.lower():
                return "Invalid OpenAI API key. Please provide a valid API key."
            return f"Error generating summary: {error_msg}"

    def summarize_search_results(self, results: list) -> Optional[str]:
        """Generate a summary of search results"""
        if not results:
            return None

        if not os.getenv("OPENAI_API_KEY"):
            return "OpenAI API key not found. Please provide a valid API key to enable summarization."

        # Prepare context from results
        context = "\n".join([
            f"Document: {r['Document']}\n"
            f"Term: {r['Search Term']}\n"
            f"Context: {r['Excerpt']}\n"
            for r in results[:5]  # Limit to first 5 results for conciseness
        ])

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Create a brief summary of the search results, highlighting key findings and patterns."
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize these search results:\n\n{context}"
                    }
                ],
                max_tokens=200,
                temperature=0.5
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e)
            print(f"Error in search results summarization: {error_msg}")
            if "rate limit" in error_msg.lower():
                return "OpenAI API rate limit reached. Please try again in a few moments."
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                return "OpenAI API quota exceeded. Please ensure your account has available credits and billing is set up correctly."
            elif "invalid" in error_msg.lower() and "api" in error_msg.lower():
                return "Invalid OpenAI API key. Please provide a valid API key."
            return f"Error generating summary: {error_msg}"