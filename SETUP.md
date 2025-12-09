# Installation Instructions for COURSE-ADVISOR-AI

Prerequisites:
The following must be installed before hand:
- Python 3.9+
- pip
- Git

Installation Steps

1. Clone repository:
git clone https://github.com/KcyOkolo/course-assistant-ai.git
cd course-assistant-ai

2. Create virtual environment to isolate project dependencies: 
python3 -m venv venv
source venv/bin/activate

3. Install all dependencies: 
pip install -r requirements.txt

This will install:
gradio - Used to build the UI
anthropic - Claude API Client
sentence-transformers - Text embedding models
faiss-cpu - Indexing and Vector similarity search
pyumupdf - PDF processing

To verify installation: 
python test_setup.py


4. Set Up API Key:
Go to console.anthropic.com
Sign up and navigate to "API Keys"
Create a new key and copy it
Create `.env` file in root directory and define ANTHROPIC_API_KEY= your copied key 

Note on API Key: Please reach out to me at kyo3@duke.edu for access to my claude key 

5. Sample Syllabi :
I have included sample syllabi in data/duke_syllabi
These syllabi were not used to train. No training or finetuning was done in this project
They are only for testing/providing input to RAG when system runs
Feel free to add your own syllabi to the path specified above