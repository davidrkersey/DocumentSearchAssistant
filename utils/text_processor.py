import nltk
from nltk.tokenize import sent_tokenize
import re
import unicodedata
import os

# Create NLTK data directory if it doesn't exist
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)

# Download required NLTK data with error handling
try:
    nltk.download('punkt', quiet=True, raise_on_error=True)
except Exception as e:
    # Try downloading to the specific directory
    nltk.download('punkt', download_dir=nltk_data_dir, quiet=True)

def normalize_text(text):
    """Normalize text for consistent comparison"""
    # Convert to lowercase
    text = text.lower()

    # Remove accents
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

    # Remove special characters but keep spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)

    # Normalize whitespace
    text = ' '.join(text.split())

    return text

def get_context(text, term, context_size=200):
    """Extract context around a term"""
    term_pos = normalize_text(text).lower().find(normalize_text(term).lower())
    if term_pos == -1:
        return None

    start = max(0, term_pos - context_size)
    end = min(len(text), term_pos + len(term) + context_size)

    # Extend to complete sentences
    context = text[start:end]
    try:
        sentences = sent_tokenize(context)
    except LookupError:
        # Fallback if tokenization fails
        sentences = [context]

    if len(sentences) > 1:
        return ' '.join(sentences)
    return context

def search_terms(text_by_page, term):
    """Search for terms in text and return page numbers and contexts"""
    results = {}
    normalized_term = normalize_text(term)

    for page_num, page_text in text_by_page.items():
        normalized_text = normalize_text(page_text)

        if normalized_term in normalized_text:
            contexts = []
            term_positions = [m.start() for m in re.finditer(normalized_term, normalized_text)]

            for pos in term_positions:
                context = get_context(page_text, term)
                if context:
                    contexts.append(context)

            if contexts:
                results[page_num] = contexts

    return results

def generate_summary(text, max_length=150):
    """Generate a brief summary of the context"""
    try:
        sentences = sent_tokenize(text)
    except LookupError:
        # Fallback if tokenization fails
        sentences = [text]

    if not sentences:
        return ""

    summary = sentences[0]
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."

    return summary