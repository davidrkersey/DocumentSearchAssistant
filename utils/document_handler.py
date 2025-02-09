import docx
import PyPDF2
from typing import Dict, Optional
import os
import re

class DocumentHandler:
    """Base class for document handlers"""
    def extract_text(self) -> Dict[int, str]:
        """Extract text from document and return dict of page numbers and text content"""
        raise NotImplementedError("Must be implemented by subclass")

    def clean_text(self, text: str) -> str:
        """Clean text by removing problematic characters"""
        if not text:
            return ""
        # Remove NUL characters and other control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

class PDFHandler(DocumentHandler):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> Dict[int, str]:
        """Extract text from PDF file"""
        text_by_page = {}

        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    # Clean the extracted text
                    text_by_page[page_num] = self.clean_text(page.extract_text())

        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

        return text_by_page

class WordHandler(DocumentHandler):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> Dict[int, str]:
        """Extract text from Word document"""
        text_by_page = {}

        try:
            doc = docx.Document(self.file_path)

            # Word documents don't have explicit pages, so we'll group paragraphs
            # into virtual pages of roughly 3000 characters each
            current_page = []
            current_length = 0
            page_num = 0

            for para in doc.paragraphs:
                para_text = self.clean_text(para.text)
                if para_text:
                    current_page.append(para_text)
                    current_length += len(para_text)

                    # Start a new page after ~3000 characters
                    if current_length >= 3000:
                        text_by_page[page_num] = '\n'.join(current_page)
                        current_page = []
                        current_length = 0
                        page_num += 1

            # Add any remaining text as the last page
            if current_page:
                text_by_page[page_num] = '\n'.join(current_page)

        except Exception as e:
            raise Exception(f"Error processing Word document: {str(e)}")

        return text_by_page

class TextHandler(DocumentHandler):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> Dict[int, str]:
        """Extract text from plain text file"""
        text_by_page = {}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                content = self.clean_text(content)

                # Split into virtual pages of roughly 3000 characters
                chars_per_page = 3000
                pages = [content[i:i + chars_per_page] 
                        for i in range(0, len(content), chars_per_page)]

                for i, page_content in enumerate(pages):
                    text_by_page[i] = page_content.strip()

        except Exception as e:
            raise Exception(f"Error processing text file: {str(e)}")

        return text_by_page

def create_document_handler(file_path: str) -> Optional[DocumentHandler]:
    """Factory method to create appropriate document handler based on file extension"""
    ext = os.path.splitext(file_path)[1].lower()

    handlers = {
        '.pdf': PDFHandler,
        '.docx': WordHandler,
        '.doc': WordHandler,
        '.txt': TextHandler
    }

    handler_class = handlers.get(ext)
    if handler_class:
        return handler_class(file_path)

    raise ValueError(f"Unsupported file format: {ext}")