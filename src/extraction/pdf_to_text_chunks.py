import pymupdf
import os

def extract_text_from_pdf(pdf_path):
    """Extracts text from PDF file"""
    try:
        text = ""
        doc = pymupdf.open(pdf_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def chunk_text(text, chunk_size=600, overlap=50):
    """Splits text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)

    return chunks

def process_syllabus(pdf_path):
    """Main processing function: Pdf -> text -> chunks"""
    print(f"\nProcessing {pdf_path}:")
    
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None
    
    chunks = chunk_text(text)

    
    return {
        'text': text,
        'chunks': chunks,
        'filename': os.path.basename(pdf_path)
    }

if __name__ == "__main__":
    import sys
    
    syllabus_dir = "data/duke_syllabi"
    pdfs = [f for f in os.listdir(syllabus_dir) if f.endswith('.pdf')]
    
    # Ensure I have syllabis in folder
    if not pdfs:
        print("No PDFs in data/duke_syllabi/")
        sys.exit(1)

    for pdf in pdfs: 
        full_path = os.path.join(syllabus_dir, pdf)
        result = process_syllabus(full_path)
        
        if result:
            print(f"\nSuccesfully Processed {pdf}!")
            print(f"Extracted {len(result['text'])} characters & Created {len(result['chunks'])} chunks")
            print(f"\nSnippet of first chunk:")
            print(result['chunks'][0][:300]+"...")
