# AI generated: Claude Code"

"""
Quick test script to verify your Course Assistant setup
"""

import os
import sys

def check_file(path, description):
    """Check if a file exists"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_import(module_name, description):
    """Check if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {e}")
        return False

def main():
    print("=" * 60)
    print("🔍 Course Assistant AI - Setup Verification")
    print("=" * 60)
    
    all_good = True
    
    # Check files
    print("\n📁 Checking project structure...")
    files_to_check = [
        ("gradio_app.py", "Main Gradio app"),
        ("requirements.txt", "Requirements file"),
        (".env", "Environment file (.env)"),
        ("src/integrated_chat.py", "Chat integration"),
        ("src/extraction/pdf_to_text_chunks.py", "PDF processor"),
        ("src/rag/rag_system.py", "RAG system"),
        ("src/utils/syllabus_parser.py", "Syllabus parser"),
        ("src/utils/grade_calculator.py", "Grade calculator"),
    ]
    
    for path, desc in files_to_check:
        if not check_file(path, desc):
            all_good = False
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    dependencies = [
        ("gradio", "Gradio"),
        ("anthropic", "Anthropic SDK"),
        ("sentence_transformers", "Sentence Transformers"),
        ("faiss", "FAISS"),
        ("fitz", "PyMuPDF"),
        ("dotenv", "python-dotenv"),
    ]
    
    for module, desc in dependencies:
        if not check_import(module, desc):
            all_good = False
    
    # Check API key
    print("\n🔑 Checking API key...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if api_key:
            print(f"✅ ANTHROPIC_API_KEY is set (length: {len(api_key)})")
        else:
            print("❌ ANTHROPIC_API_KEY not found in .env file")
            all_good = False
    except Exception as e:
        print(f"⚠️  Error checking API key: {e}")
        all_good = False
    
    # Final verdict
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All checks passed! You're ready to run:")
        print("   python gradio_app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create .env file with: ANTHROPIC_API_KEY=your_key_here")
        print("  - Ensure src/ folder structure matches SETUP.md")
    print("=" * 60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())