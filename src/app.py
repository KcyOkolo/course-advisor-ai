import gradio as gr
from dotenv import load_dotenv
from extraction.pdf_to_text_chunks import process_syllabus
from rag.rag_system import RAGSystem
from utils.syllabus_parser import SyllabusParser
from utils.grade_calculator import GradeCalculator
from integrated_chat import RAGChat

load_dotenv()

parser = SyllabusParser()

def initialize_session():
    """Initialize session-specific data"""
    return {
        'rag_system': RAGSystem(),
        'calculators': {},
        'course_names': [],
        'chatbot': None,
        'current_course': None
    }

def add_course(pdf_file, course_name, session_state):
    """Process uploaded syllabus and add course"""
    
    if not pdf_file:
        return "Please upload a PDF file", gr.update(choices=session_state['course_names']), None, session_state
    
    if not course_name or not course_name.strip():
        return "Please enter a course name", gr.update(choices=session_state['course_names']), None, session_state
    
    course_name = course_name.strip().upper()
    
    if course_name in session_state['course_names']:
        return f"Course {course_name} already exists!", gr.update(choices=session_state['course_names']), None, session_state
    
    try:
        result = process_syllabus(pdf_file.name)
        
        if not result:
            return "Failed to process PDF", gr.update(choices=session_state['course_names']), None, session_state
        
        grading_info = parser.parse_grading_structure(result['text'])
        
        if not grading_info:
            return "Failed to parse grading structure", gr.update(choices=session_state['course_names']), None, session_state
        
        grading = grading_info["grading_breakdown"]
        counts = grading_info["assignment_counts"]
        session_state['calculators'][course_name] = GradeCalculator(course_name, grading, counts)
        
        session_state['rag_system'].add_course(course_name, result['chunks'])
        session_state['course_names'].append(course_name)
        session_state['rag_system'].index_chunks()
        
        session_state['chatbot'] = RAGChat(
            session_state['rag_system'], 
            session_state['calculators'], 
            session_state['course_names']
        )
        
        return (
            f"Successfully added {course_name}!", 
            gr.update(choices=session_state['course_names'], value=course_name), 
            None, 
            session_state
        )
        
    except Exception as e:
        return f"Error adding course: {str(e)}", gr.update(choices=session_state['course_names']), None, session_state


def chat_with_bot(message, history, session_state):
    """Handle chat messages"""
    if history is None:
        history = []
    
    if not session_state['chatbot']:
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "Please add at least one course first!"}
        ], session_state
    
    if not message or not message.strip():
        return history, session_state
    
    try:
        response = session_state['chatbot'].chat(message.strip())
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ], session_state
    except Exception as e:
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": f"Error: {str(e)}"}
        ], session_state


def select_course(course_name, session_state):
    """Update the grade table when a course is selected"""
    if not course_name or course_name not in session_state['calculators']:
        return gr.update(value="No course selected"), gr.update(visible=False), gr.update(choices=[]), session_state
    
    session_state['current_course'] = course_name
    calculator = session_state['calculators'][course_name]
    summary = calculator.get_summary()
    
    category_choices = list(calculator.grading_breakdown.keys())
    
    max_scores = 0
    for category in summary["categories"].keys():
        scores_count = len(calculator.grades[category])
        max_scores = max(max_scores, scores_count)
    
    table_data = []
    for category, info in summary["categories"].items():
        scores = calculator.grades[category]
        count = info["total"]
        
        row = [category, f"{info['weight']:.1f}%", count]
        
        for i in range(max_scores):
            if i < len(scores):
                row.append(f"{scores[i]:.1f}")
            else:
                row.append("")
        
        if info["average"] is not None:
            row.append(f"{info['average']:.1f}")
        else:
            row.append("--")
        
        table_data.append(row)
    
    headers = ["Category", "Weight", "Count"]
    if max_scores > 0:
        headers += [f"Score {i+1}" for i in range(max_scores)]
    headers.append("Grade")
    
    current_grade = summary["current_grade"]
    grade_display = f"Current Grade: {current_grade:.2f}%" if current_grade > 0 else "Current Grade: No grades entered yet"
    
    return (
        gr.update(value=grade_display), 
        gr.update(value=table_data, headers=headers, visible=True),
        gr.update(choices=category_choices, value=None),
        session_state
    )


def add_grade_to_course(course_dropdown, category_input, score_input, max_score_input, session_state):
    """Add a grade to the selected course"""
    if not course_dropdown or course_dropdown not in session_state['calculators']:
        return "Please select a course first", gr.update(), gr.update(), gr.update(), session_state
    
    if not category_input:
        return "Please select a category", gr.update(), gr.update(), gr.update(), session_state
    
    try:
        calculator = session_state['calculators'][course_dropdown]
        summary = calculator.get_summary()
        category_info = summary["categories"][category_input]
        
        if category_info["check"]:
            return (
                f"Cannot add grade: {category_input} is full ({category_info['completed']}/{category_info['total']})", 
                gr.update(), gr.update(), gr.update(), session_state
            )

        score = float(score_input)
        max_score = float(max_score_input) if max_score_input else 100
        
        success = calculator.add_grade(category_input, score, max_score)
        
        if success:
            grade_display, table, categories, session_state = select_course(course_dropdown, session_state)
            return f"Grade added successfully!", grade_display, table, categories, session_state
        else:
            return (
                f"Failed to add grade. Make sure '{category_input}' is a valid category.", 
                gr.update(), gr.update(), gr.update(), session_state
            )
            
    except ValueError:
        return "Please enter valid numbers for score and max score", gr.update(), gr.update(), gr.update(), session_state


# Build the Gradio interface
with gr.Blocks(title="Course Assistant") as app:
    # Create session state
    session_state = gr.State(initialize_session())
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Classes")
            course_list = gr.Radio(
                choices=[],
                label="",
                interactive=True
            )
            add_course_btn = gr.Button("Add Course", variant="primary", size="sm")
        
        with gr.Column(scale=3):
            gr.Markdown("## Course Advisor AI")
            chatbox = gr.Chatbot(height=400, show_label=False)
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask a question about your courses...",
                    show_label=False,
                    container=False,
                    scale=4
                )
                send_btn = gr.Button("send", scale=1, variant="primary")
    
    gr.Markdown("---")
    with gr.Row():
        with gr.Column():
            grade_section_title = gr.Markdown("## Grades For:")
            current_grade_display = gr.Markdown("*Select a course to view grades*")
            
            grade_table = gr.Dataframe(
                headers=["Category", "Weight", "Count", "Scores", "Grade"],
                interactive=False,
                visible=False,
                wrap=True
            )
            
            gr.Markdown("### Add New Grade")
            with gr.Row():
                grade_category = gr.Dropdown(label="Category", choices=[], interactive=True, scale=2)
                grade_score = gr.Textbox(label="Score", placeholder="85", scale=1)
                grade_max = gr.Textbox(label="Max Score", placeholder="100", scale=1)
                add_grade_btn = gr.Button("Add Grade", scale=1, variant="primary")
            
            grade_add_status = gr.Textbox(label="", interactive=False, show_label=False, visible=False)
    
    with gr.Group(visible=False) as add_course_modal:
        gr.Markdown("## Upload Syllabus")
        course_name_input = gr.Textbox(label="Course Name", placeholder="e.g., CS316")
        pdf_upload = gr.File(label="Upload Syllabus PDF", file_types=[".pdf"])
        
        with gr.Row():
            submit_course_btn = gr.Button("Add", variant="primary")
            cancel_btn = gr.Button("Cancel")
        
        upload_status = gr.Textbox(label="", interactive=False, show_label=False)
    
    # Event handlers
    add_course_btn.click(
        lambda: gr.update(visible=True),
        outputs=add_course_modal
    )
    
    cancel_btn.click(
        lambda: gr.update(visible=False),
        outputs=add_course_modal
    )
    
    def submit_and_close(pdf, name, state):
        message, courses_update, _, state = add_course(pdf, name, state)
        return message, courses_update, gr.update(visible=False), state
    
    submit_course_btn.click(
        submit_and_close,
        inputs=[pdf_upload, course_name_input, session_state],
        outputs=[upload_status, course_list, add_course_modal, session_state]
    )
    
    def update_grade_section(course_name, state):
        grade_display, table, categories, state = select_course(course_name, state)
        if course_name:
            title = f"## Grades For: {course_name}"
        else:
            title = "## Grades For:"
        return title, grade_display, table, categories, state
    
    course_list.change(
        update_grade_section,
        inputs=[course_list, session_state],
        outputs=[grade_section_title, current_grade_display, grade_table, grade_category, session_state]
    )
    
    msg_input.submit(
        chat_with_bot,
        inputs=[msg_input, chatbox, session_state],
        outputs=[chatbox, session_state]
    ).then(
        lambda: "",
        outputs=msg_input
    )
    
    send_btn.click(
        chat_with_bot,
        inputs=[msg_input, chatbox, session_state],
        outputs=[chatbox, session_state]
    ).then(
        lambda: "",
        outputs=msg_input
    )
    
    def add_grade_handler(selected_course, category, score, max_score, state):
        result = add_grade_to_course(selected_course, category, score, max_score, state)
        return result[0], result[1], result[2], result[3], gr.update(visible=True), result[4]
    
    add_grade_btn.click(
        add_grade_handler,
        inputs=[course_list, grade_category, grade_score, grade_max, session_state],
        outputs=[grade_add_status, current_grade_display, grade_table, grade_category, grade_add_status, session_state]
    )

if __name__ == "__main__":
    app.launch(share=True)