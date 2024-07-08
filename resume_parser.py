import os
import json
import logging
import re
from io import BytesIO
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTImage, LTFigure
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFPageAggregator
from nltk.tokenize import sent_tokenize

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    Handles both text-based and image-based PDFs using pdfminer.
    """
    resource_manager = PDFResourceManager()
    fake_file_handle = BytesIO()
    converter = PDFPageAggregator(resource_manager, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
            layout = converter.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    fake_file_handle.write(lt_obj.get_text().encode('utf-8'))
                elif isinstance(lt_obj, LTImage) or isinstance(lt_obj, LTFigure):
                    # Handle images in PDF if needed
                    pass

    text = fake_file_handle.getvalue().decode()
    fake_file_handle.close()

    return text

def parse_resume_text(text):
    """
    Parse the extracted resume text to identify sections and their content.
    """
    sections = {
        'personal_info': [],
        'summary': [],
        'experience': [],
        'education': [],
        'skills': [],
        'projects': [],
        'certifications': [],
        'languages': [],
        'interests': []
    }

    # Split text into sentences for better section identification
    sentences = sent_tokenize(text)

    current_section = None
    section_keywords = {
        'personal_info': ['name', 'address', 'email', 'phone', 'contact'],
        'summary': ['summary', 'objective', 'profile'],
        'experience': ['experience', 'work', 'employment'],
        'education': ['education', 'academic'],
        'skills': ['skills', 'expertise'],
        'projects': ['projects', 'portfolio'],
        'certifications': ['certifications', 'courses'],
        'languages': ['languages', 'fluency'],
        'interests': ['interests', 'hobbies']
    }

    # Function to identify section based on keywords
    def identify_section(sentence):
        for key, keywords in section_keywords.items():
            for keyword in keywords:
                if re.search(r'\b{}\b'.format(keyword), sentence, re.IGNORECASE):
                    return key
        return None

    # Iterate through sentences to identify sections
    for sentence in sentences:
        section = identify_section(sentence)
        if section:
            current_section = section
        if current_section:
            sections[current_section].append(sentence.strip())

    # Convert sections to JSON format
    return json.dumps(sections, indent=4)

def parse_resume_pdf(pdf_path):
    """
    Parse a PDF resume into structured JSON format.
    """
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)

        # Parse extracted text into sections
        parsed_data = parse_resume_text(text)

        return parsed_data

    except Exception as e:
        logger.error(f"Error parsing resume PDF: {e}")
        return None

if __name__ == '__main__':
    # Example usage
    pdf_path = r"C:\Users\Saiab\Desktop\Desktop  2\docs\Jarvis E19CSE425 Resume - September 2022.pdf"
    parsed_resume = parse_resume_pdf(pdf_path)
    if parsed_resume:
        print(parsed_resume)
    else:
        print("Failed to parse the resume PDF.")
