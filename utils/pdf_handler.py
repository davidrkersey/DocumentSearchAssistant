import PyPDF2

def extract_pdf_text(file_path):
    """Extract text from PDF file and return dictionary of page numbers and text content"""
    text_by_page = {}
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text_by_page[page_num] = page.extract_text()
                
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")
    
    return text_by_page
