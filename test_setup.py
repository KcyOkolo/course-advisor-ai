import sys

def test_imports():
    print("Testing imports...")
    packages = {
        'openai': 'openai',
        'sentence_transformers': 'sentence-transformers',
        'fitz': 'PyMuPDF',
        'pdfplumber': 'pdfplumber',
        'pandas': 'pandas'
    }
    all_good = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            all_good = False
    return all_good

def test_api_keys():
    print("\nChecking API keys...")
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        key = os.getenv("OPENAI_API_KEY")
        if key and key != "your_key_here":
            print("✅ OpenAI API key found")
        else:
            print("⚠️  OpenAI API key not set")
    except Exception as e:
        print(f"⚠️  {e}")

if __name__ == "__main__":
    print("🔍 Course Advisor AI - Setup Verification\n")
    if test_imports():
        test_api_keys()
        print("\n✅ Setup complete!")
    else:
        print("\n❌ Install packages: pip install -r requirements.txt")
        sys.exit(1)
