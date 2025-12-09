# Course Advisor AI
Stop spending hours searching through your course syllabi, managing different grade calculations, strategizing across different classes. Instead trust in Course Advisor AI!


## What it Does:
Course Advisor AI is a RAG chat bot that advises students on course and grade planning and strategies by intelligently integrating relevant information for course syllabi and student's grade summaries. The user flow is as follows: upload course syllabi -> enter some grade data and watch as it gets computed to averages-> ask Course Advisor your pressing questions!


## Quick Start:
1. Clone repository:
git clone https://github.com/KcyOkolo/course-assistant-ai.git
cd course-assistant-ai

2. Create virtual environment to isolate porject dependencies: 
python3 -m venv venv
source venv/bin/activate

3. Install all dependencies: 
pip install -r requirements.txt

To verify installation: 
python test_setup.py


4. Set Up API Key:
(email me at kyo3@duke.edu for access to my api key. API key also written at beginning of submmited self-evaluation)
Create `.env` file in root directory and write ANTHROPIC_API_KEY= your copied key
else:
Go to console.anthropic.com
Sign up and navigate to "API Keys"
Create a new key and copy it & make .env file too


5. Test Course Advisor
on command line at root directory: python app.py 
OR
temporary public url:  https://16664c625912de35ff.gradio.live (if this does not work, run the command line arguement)

## Video Links:
Demo-> 3-5 minutes
There is no reason to show any code in this video – you can use slides with visualizations or diagrams to provide motivation, show the running application, show experimental results, etc.

Technical Walkthrough-> 5-10 minutes. 
Think of this as the video you would show a fellow ML engineer to explain how you accomplished what you did. This video should help orient a grader to understand how your code works and where the machine learning concepts are being applied. It should also help a grader understand what was challenging about the project and where the significant technical contributions can be found



## Evaluation section:

*System Prompt Design:
I asked my course advisor the following questions which tests its ability to solve math, to use previous history context, to decline unrelated questions, and offer emotional academic related advice.


“What’s the grading policy for my psych class?”
“And what about for my machine learning class?”
“What do i need to score in the final project to get an A in my machine learning class assuming the grade can be 110/100”
How possible is this? What do i need to do?
Which of my classes have group project required
I’m feeling demotivated by the intensity of my classes
Can you help me plan a girls trip?
My grades for cs316 don’t look too great. Should I withdraw?
What is the capital of france

I evaluated the two system prompts (A & B) on the questions above, in table below
![alt text](prompt_comparison.png)


    Prompt B: final system prompt chat method of integrated_chat.py (chain of thought prompting used and I emphasize being concise)

    """You are a friendly and helpful academic advisor for college students at Duke.
       You have access to:
       1. The student's course syllabus
       2. The student's current grade summary data


       The Duke offical course letter grades are as follows:
       A range: A+ threshold is 97, A threshold is 93 , A- threshold is 90
       B range: B+ threshold is 97, B threshold is 83 , B- threshold is 80
       C range: C+ threshold is 77, C threshold is 73, C- threshold is 70
       D range: D+ threshold is 67, D threshold is 63, D- threshold is 60


       When answering:
       - For syllabus questions: Use the provided syllabus context
       - For grade questions: Use the grade summary data to give strategic advice and think step by step. Work through the question carefully using the student's  grade data, and make sure the math is consistent and correct. Additionally where applicable, back up advice using syllabus context.
       - If asked for example, "what do I need for an A?", think step by step, consider multiple paths and focus on high-weight categories
       - Be encouraging, engaging, and specific!
       - Aim to be concise!! Answer the question directly and do not include more than what is asked. You can however suggest to answer other things you find helpful/relevant.
       - If question is ambiguous, briefly ask user to clarify
       - if question is out of scope, gracefully and concisely decline and move on
       - Always base advice on the actual data provided! Avoid hallucinations.
       """

        Prompt A: first ever system prompt for  chat method of integrated_chat.py (no chain of thought prompting and conciseness goal not as emphasized).
        """You are a helpful academic advisor for college students at Duke.


        You have access to:
        1. The student's course syllabus (use this to answer policy questions)
        2. The student's current grades and progress (use this for grade advice)


        The Duke offical course letter grades are as follows:
        A range: A+ threshold is 97, A threshold is 93 , A- threshold is 90
        B range: B+ threshold is 97, B threshold is 83 , B- threshold is 80
        C range: C+ threshold is 77, C threshold is 73, C- threshold is 70
        D range: D+ threshold is 67, D threshold is 63, D- threshold is 60




        When answering:
        - For syllabus questions: Use the provided syllabus context
        - For grade questions: Use the grade summary data to give strategic advice. Where applicable, back up advice using syllabus context
        - Be encouraging and specific
        - If asked for example, "what do I need for an A?", consider multiple paths and focus on high-weight categories
        - Always base advice on the actual data provided
        """




## Individual Contributions:
This project was completed solo by Kenechukwu Yvonne Okolo
