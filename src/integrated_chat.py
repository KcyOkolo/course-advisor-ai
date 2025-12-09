import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()


class RAGChat:
    """Chatbot that can answer syllabus questions, access student's grade info, and give grade advice"""
    
    def __init__(self, rag_system, grade_calculator, courses):
        self.rag = rag_system
        self.courses = courses
        self.calculator = grade_calculator
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.conversation_history = []

    def rewrite_query(self, user_message, courses):
    
        system_prompt = """
            You are a query rewriter agent for a RAG system. 
            Given a user's Chat history, Current query, and Course list, your goal is to return ONLY one valid JSON in this exact format:

            {
                "question": "rewritten query for RAG retrieval", #you will rewrite the user's current query
                "courses": ["course1", "course2"], #you will find courses from course list that are relevant to the current query
                "skip_RAG": false, #false by default
                "context_summary": "brief summary of relevant chat history for answering agent"
            }

            Ensure that the following keys are present in output!: ["question", "courses", "skip_RAG", "context_summary"]

            Rules For Query Rewriting:
            1. Resolve pronouns/references using chat history and course list (e.g, "it" or "that course" -> "CS316")
            2. Expand abbreviations using course list and chat history (e.g, "my psych class" -> "PSY277")
            3. Make course names explicit in the rewritten query when they were implied
            4. Set skip_RAG=true ONLY when:
            - Current query is completely ambiguous and cannot be resolved (e.g, "What's the policy?" with no context; "My psych class" but 
            user either has no psych classes or more than one psych class)
            - Current query is entirely off-topic (i.e unrelated to academic advise: "What's the weather?", "Help me plan a trip")

            Rules For Context Summary:
            1. Only include relevant context. Don't summarize entire conversation, just what's needed to answer current question
            2. Keep it brief - 1-3 sentences max, focus on facts not prose
            4. Set to empty string if no relevant history or make a note to the final LLM
            5. Don't repeat information that will be in RAG results

            EXAMPLES:

            Example 1 :
            Chat History: [
                {"role": "user", "content": "What's the CS316 late policy?"},
                {"role": "assistant", "content": "CS316 allows 2 late days..."}
            ]
            Current: "How about for CS372?"
            Courses: ["CS372", "CS316", "PSY277", "CS240"]
            Output: {
                "question": "What is the late submission policy for CS372?",
                "courses": ["CS372"],
                "skip_RAG": false,
                "context_summary": "User previously asked about CS316 late policy for comparison."
            }

            Example 2: 
            Chat History: [
                {"role": "user", "content": "I got 70% on CS240 midterm"},
                {"role": "assistant", "content": "That's below average..."},
            ]
            Current: "What if I get 85% on all remaining homework?"
            Courses: ["CS372", "CS240"]
            Output: {
                "question": "What is the grading polciy for CS240?",
                "courses": ["CS240"],
                "skip_RAG": false,
                "context_summary": "User got 70% on CS240 midterm and wants to calculate final grade possibilities."
            }

            Example 3 :
            Chat History: []
            Current: "What's CS240's attendance policy?"
            Courses: ["CS372"]
            Output: {
                "question": "What is CS240's attendance policy?",
                "courses": [],
                "skip_RAG": True,
                "context_summary": "User is asking about CS240 but it is not in their course list"
            }

            Example 4:
            Chat History: [
                {"role": "user", "content": "What's CS240's workload?"},
                {"role": "assistant", "content": "CS240 has weekly problem sets..."},
            ]
            Current: "What about for my other classes?"
            Courses: ["CS372", "CS316", "PSY277", "CS240"]
            Output: {
                "question": "What is CS240's drop policy and grading breakdown?",
                "courses": ["CS372", "CS316", "PSY277"],
                "skip_RAG": false,
                "context_summary": "User wants to know workload for their remaining classes. Asked about for CS240 previously."
            }
            """
        MAX_HISTORY_SIZE = 6
        if len(self.conversation_history) > MAX_HISTORY_SIZE:
            self.conversation_history = self.conversation_history[-MAX_HISTORY_SIZE:]

        user_prompt = f"""
        Chat History: {self.conversation_history}
        Current: {user_message}
        Courses: {courses}
        """

        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,  
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        json_text = response.content[0].text.strip()
        
        # AI generated: Claude (123-141)
        if json_text.startswith("```"):
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:].strip()
            json_text = json_text.rsplit("```", 1)[0].strip()
        
        try:
            final_prompt = json.loads(json_text)
            
        except json.JSONDecodeError as e:
            print(f"Agentic Query Rewriter Failed: {e}")
            return {
                "question": user_message,
                "courses": None,
                "skip_RAG": False,
                "context_summary": ""
            }
        return final_prompt

        
    
    def chat(self, user_message):
        retrieved_chunks = ""
        grade_summary = []
        for course in self.courses:
            grade_summary.append(self.calculator[course].get_summary())
        
        #for memory & history
        memory = self.rewrite_query(user_message, self.courses)
        rag_query = memory["question"]
        course_filters = memory["courses"] 

        print(f"{rag_query}")
        print(f"{course_filters}")
        print(f"{memory['context_summary']}")

        if not memory["skip_RAG"]:
            rag_results = self.rag.retrieve(rag_query, len(self.courses), course_filters, k=3)
            retrieved_chunks = "\n\n".join([r['chunk'] for r in rag_results])
        
        
        system_prompt =  """You are a friendly and helpful academic advisor for college students at Duke.
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

        
        # Building user prompt with context
        user_prompt = f"Syllabus contexts:{retrieved_chunks}"
        
        if grade_summary:
            user_prompt += f"\n Student's current grades: {json.dumps(grade_summary, indent=2)}"

        user_prompt += f"\n Past Chat Context: {memory['context_summary']} "
        
        user_prompt += f"\n Student question: {user_message}    Answer:"""
        

        # API call to claude
        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        print("got final response")
         

        answer = response.content[0].text

        print(f"{answer}")
        
        
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": answer})
        
        return answer


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    from src.extraction.pdf_to_text_chunks import process_syllabus
    from src.rag.rag_system import RAGSystem
    from src.utils.syllabus_parser import SyllabusParser
    from src.utils.grade_calculator import GradeCalculator
    
    # 1. Load and process syllabi into chunks and chunk metadata & parse grading_info 
    syllabus_dir = "data/duke_syllabi"
    pdfs = [f for f in os.listdir(syllabus_dir) if f.endswith('.pdf')]

    if not pdfs:
        print("No PDFs in data/duke_syllabi/")
        sys.exit(1)

    rag = RAGSystem()
    parser = SyllabusParser()
    num_courses = 0
    course_names = []
    calculators = {}

    print("\n 1. Processing syllabi into text chunks and chunk metadata + Parsing its grading_info + setting up seperate calculators per course")
    for pdf in pdfs:
        full_path = os.path.join(syllabus_dir, pdf)

        while True:
            course_name = input(f"\nWhat is the Course name for {pdf} (e.g. CS210): ").strip().upper()
            if course_name in course_names:
                print(f"{course_name} already exists!")
                continue
            if not course_name:
                print(f"Course name cannot be empty!")
                continue
                
            break

        course_names.append(course_name)
        result = process_syllabus(full_path)
        grading_info = parser.parse_grading_structure(result['text'])
        grading = grading_info["grading_breakdown"]
        counts = grading_info["assignment_counts"]
        calculators[course_name] = GradeCalculator(course_name, grading, counts)
        rag.add_course(course_name, result['chunks'])
        num_courses+=1


    print("\n 2. Creating embeddings for chunks and storing in FAISS")
    rag.index_chunks()

    
    print("\n 3. Adding some sample grades to cS316")
    calculators["CS316"].add_grade("homeworks", 85, 100)
    calculators["CS316"].add_grade("homeworks", 90, 100)
    calculators["CS316"].add_grade("gradiance_exercises", 95, 100)
    calculators["CS316"].add_grade("gradiance_exercises", 88, 100)

    
    print("\n 4. Creating Integrated Chat bot")
    chatbot = RAGChat(rag, calculators, course_names)
    
    print("\n 5. Testing the Integrated Chat bot: RAG retrieval + filtering") #, Query Rewriting & Summarization
    
    #set questions that test for each class, for multiple in one, on grades, on policy, on both, semi -related(make me study plan to achieve this grade) , off related
    questions = [
        "What is the late submission policy for CS240?",
        "What is the late submission policy for CS372?",
        "How are exams weighted in PSY277 and CS372?",
        "What's the attendance policy for CS316?",
        "Does CS372 allow collaboration on homework?",
    ]


    conversation =[
            "Tell me about CS240's grading system",
            "Now tell me about CS316's",
            "And CS372's",
            "And PSY277's",
            "Now compare all four", 
            "Which has the easiest grading?",
            "What was CS240's policy again?",
            "Which courses have group projects?",
            "How are they weighted in each?",
            "Which one values them more?",
            "What if I prefer working alone?",
            "Can I do them solo in any of these courses?",
            "I got 70% on the CS240 midterm and 65% on the CS316 midterm",
            "What grade am I heading towards in each?",
            "Which one should I focus on improving?",
            "If I ace all remaining assignments in that course, what would my final grade be?",
            "Is it worth it or should I focus on the other one?"
    ]
    
    for q in conversation:
        print(f"\nStudent: {q}")
        print("-" * 60)
        answer = chatbot.chat(q)
        print(f"Course Advisor: {answer}")
        print()

 