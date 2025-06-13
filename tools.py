from crewai_tools import (
    FileReadTool,
    ScrapeWebsiteTool,
    MDXSearchTool,
    SerperDevTool,
    PDFSearchTool
)
import PyPDF2
import os
import tempfile

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file using PyPDF2"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def convert_pdf_to_text_file(pdf_path):
    """Convert PDF to text file and return the text file path"""
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        # Create temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(text)
            return tmp_file.name
    except Exception as e:
        print(f"Error converting PDF to text: {e}")
        return None

def get_resume_tools(resume_path):
    """Initialize and return resume tools with the provided resume path"""
    file_extension = os.path.splitext(resume_path)[1].lower()
    
    if file_extension == '.pdf':
        # For PDF files, use PDFSearchTool and convert to text for FileReadTool
        pdf_search_tool = PDFSearchTool(pdf=resume_path)
        
        # Convert PDF to text file for FileReadTool compatibility
        text_file_path = convert_pdf_to_text_file(resume_path)
        if text_file_path:
            read_resume = FileReadTool(file_path=text_file_path)
            return read_resume, pdf_search_tool
        else:
            # Fallback: use PDF search tool for both operations
            return pdf_search_tool, pdf_search_tool
    
    elif file_extension in ['.md', '.txt']:
        # For text/markdown files, use the original approach
        read_resume = FileReadTool(file_path=resume_path)
        if file_extension == '.md':
            semantic_search_resume = MDXSearchTool(mdx=resume_path)
        else:
            # For .txt files, we'll use a generic search approach
            semantic_search_resume = FileReadTool(file_path=resume_path)
        return read_resume, semantic_search_resume
    
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: .pdf, .md, .txt")

def get_resume_tools_advanced(resume_path):
    """Enhanced version using only PyPDF2 for PDF processing"""
    file_extension = os.path.splitext(resume_path)[1].lower()
    
    if file_extension == '.pdf':
        try:
            # Try CrewAI's PDFSearchTool first
            pdf_search_tool = PDFSearchTool(pdf=resume_path)
            
            # Extract text using PyPDF2
            text = extract_text_from_pdf(resume_path)
            
            if text and text.strip():
                # Create temporary text file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                    tmp_file.write(text)
                    text_file_path = tmp_file.name
                
                read_resume = FileReadTool(file_path=text_file_path)
                return read_resume, pdf_search_tool
            else:
                # If text extraction fails, use PDF search tool for both
                print("Warning: PDF text extraction yielded empty content, using PDFSearchTool for both operations")
                return pdf_search_tool, pdf_search_tool
                
        except Exception as e:
            print(f"Error with PDF tools: {e}")
            # Try basic PDF reading as fallback
            text = extract_text_from_pdf(resume_path)
            if text and text.strip():
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                    tmp_file.write(text)
                    text_file_path = tmp_file.name
                read_resume = FileReadTool(file_path=text_file_path)
                return read_resume, read_resume
            else:
                raise Exception("Failed to extract text from PDF using PyPDF2")
    
    elif file_extension in ['.md', '.txt']:
        read_resume = FileReadTool(file_path=resume_path)
        if file_extension == '.md':
            semantic_search_resume = MDXSearchTool(mdx=resume_path)
        else:
            semantic_search_resume = FileReadTool(file_path=resume_path)
        return read_resume, semantic_search_resume
    
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Supported formats: .pdf, .md, .txt")