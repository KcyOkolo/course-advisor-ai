# AI generated: Claude Code"

import gradio as gr
import os
import sys
from dotenv import load_dotenv



from extraction.pdf_to_text_chunks import process_syllabus
from rag.rag_system import RAGSystem
from utils.syllabus_parser import SyllabusParser
from utils.grade_calculator import GradeCalculator
from integrated_chat import RAGChat

load_dotenv()

# Global vars
rag_system = RAGSystem()
parser = SyllabusParser()
calculators = {}
course_names = []
chatbot = None
current_course = None

def add_course(pdf_file, course_name):
    """Process uploaded syllabus and add course"""
    global rag_system, calculators, course_names, chatbot
    
    if not pdf_file:
        return "Please upload a PDF file", gr.update(choices=course_names), None
    
    if not course_name or not course_name.strip():
        return "Please enter a course name", gr.update(choices=course_names), None
    
    course_name = course_name.strip().upper()
    
    if course_name in course_names:
        return f"Course {course_name} already exists!", gr.update(choices=course_names), None
    
    try:
        # Process the PDF
        result = process_syllabus(pdf_file.name)
        
        if not result:
            return "Failed to process PDF", gr.update(choices=course_names), None
        
        # Parse grading structure
        grading_info = parser.parse_grading_structure(result['text'])
        
        if not grading_info:
            return "Failed to parse grading structure", gr.update(choices=course_names), None
        
        # Create grade calculator for this course
        grading = grading_info["grading_breakdown"]
        counts = grading_info["assignment_counts"]
        calculators[course_name] = GradeCalculator(course_name, grading, counts)
        
        # Add to RAG system
        rag_system.add_course(course_name, result['chunks'])
        course_names.append(course_name)
        
        # Re-index with new course
        rag_system.index_chunks()
        
        # Recreate chatbot with updated courses
        chatbot = RAGChat(rag_system, calculators, course_names)
        
        return f"Successfully added {course_name}!", gr.update(choices=course_names, value=course_name), None
        
    except Exception as e:
        return f"Error adding course: {str(e)}", gr.update(choices=course_names), None


def chat_with_bot(message, history):
    """Handle chat messages - using new Gradio message format"""
    global chatbot
    
    # Ensure history is always a list
    if history is None:
        history = []
    
    if not chatbot:
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "Please add at least one course first!"}
        ]
    
    if not message or not message.strip():
        return history
    
    try:
        response = chatbot.chat(message.strip())
        # Return as list of message dicts
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
    except Exception as e:
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": f"Error: {str(e)}"}
        ]


def select_course(course_name):
    """Update the grade table when a course is selected"""
    global current_course, calculators
    
    if not course_name or course_name not in calculators:
        return gr.update(value="No course selected"), gr.update(visible=False), gr.update(choices=[])
    
    current_course = course_name
    calculator = calculators[course_name]
    summary = calculator.get_summary()
    
    # Get category names for dropdown
    category_choices = list(calculator.grading_breakdown.keys())
    
    # Find max number of scores across all categories
    max_scores = 0
    for category in summary["categories"].keys():
        scores_count = len(calculator.grades[category])
        max_scores = max(max_scores, scores_count)
    
    # Build the grade table data
    table_data = []
    for category, info in summary["categories"].items():
        # Get individual scores for this category
        scores = calculator.grades[category]
        count = info["total"]
        
        # Create row: [category, weight, count, scores..., average]
        row = [
            category,
            f"{info['weight']:.1f}%",
            count,
        ]
        
        # Add individual score columns (pad with empty strings if fewer scores)
        for i in range(max_scores):
            if i < len(scores):
                row.append(f"{scores[i]:.1f}")
            else:
                row.append("")
        
        # Add average
        if info["average"] is not None:
            row.append(f"{info['average']:.1f}")
        else:
            row.append("--")
        
        table_data.append(row)
    
    # Build headers dynamically based on max scores
    headers = ["Category", "Weight", "Count"]
    if max_scores > 0:
        headers += [f"Score {i+1}" for i in range(max_scores)]
    headers.append("Grade")
    
    current_grade = summary["current_grade"]
    grade_display = f"Current Grade: {current_grade:.2f}%" if current_grade > 0 else "Current Grade: No grades entered yet"
    
    return (
        gr.update(value=grade_display), 
        gr.update(value=table_data, headers=headers, visible=True),
        gr.update(choices=category_choices, value=None)
    )


def add_grade_to_course(course_dropdown, category_input, score_input, max_score_input):
    """Add a grade to the selected course"""
    global calculators, current_course
    
    if not course_dropdown or course_dropdown not in calculators:
        return "Please select a course first", gr.update(), gr.update(), gr.update()
    
    if not category_input:
        return "Please select a category", gr.update(), gr.update(), gr.update()
    
    try:
        calculator = calculators[course_dropdown]
        
        # prevent adding if category is full
        summary = calculator.get_summary()
        category_info = summary["categories"][category_input]
        if category_info["check"]:  # check is True when completed == total
            return f"Cannot add grade: {category_input} is full ({category_info['completed']}/{category_info['total']})", gr.update(), gr.update(), gr.update()

        score = float(score_input)
        max_score = float(max_score_input) if max_score_input else 100
        
        success = calculator.add_grade(category_input, score, max_score)
        
        if success:
            grade_display, table, categories = select_course(course_dropdown)
            return f"Grade added successfully!", grade_display, table, categories
        else:
            return f"Failed to add grade. Make sure '{category_input}' is a valid category.", gr.update(), gr.update(), gr.update()
            
    except ValueError:
        return "Please enter valid numbers for score and max score", gr.update(), gr.update(), gr.update()
# Build the Gradio interface
with gr.Blocks(title="Course Assistant") as app:

    modal_visible = gr.State(False)
    
    with gr.Row():
        # Left sidebar has list of courses
        with gr.Column(scale=1):
            gr.Markdown("## Classes")
            course_list = gr.Radio(
                choices=course_names,
                label="",
                interactive=True
            )
            add_course_btn = gr.Button("Add Course", variant="primary", size="sm")
        
        # Right main area has chat interface
        with gr.Column(scale=3):
            gr.Markdown("## Course Advisor AI")
            chatbox = gr.Chatbot(
                height=400, 
                show_label=False
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask a question about your courses...",
                    show_label=False,
                    container=False,
                    scale=4
                )
                send_btn = gr.Button("send", scale=1, variant="primary")
    
    # Grade calculator section (at bottom)
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
            
            # Add grade interface
            gr.Markdown("### Add New Grade")
            with gr.Row():
                grade_category = gr.Dropdown(label="Category", choices=[], interactive=True, scale=2)
                grade_score = gr.Textbox(label="Score", placeholder="85", scale=1)
                grade_max = gr.Textbox(label="Max Score", placeholder="100", scale=1)
                add_grade_btn = gr.Button("Add Grade", scale=1, variant="primary")
            
            grade_add_status = gr.Textbox(label="", interactive=False, show_label=False, visible=False)
    
    # Add course modal 
    with gr.Group(visible=False) as add_course_modal:
        gr.Markdown("## Upload Syllabus")
        course_name_input = gr.Textbox(label="Course Name", placeholder="e.g., CS316")
        pdf_upload = gr.File(label="Upload Syllabus PDF", file_types=[".pdf"])
        
        with gr.Row():
            submit_course_btn = gr.Button("Add", variant="primary")
            cancel_btn = gr.Button("Cancel")
        
        upload_status = gr.Textbox(label="", interactive=False, show_label=False)
    
    # Event handlers
    
    # Toggle add course modal
    def toggle_modal(visible):
        return gr.update(visible=not visible)
    
    add_course_btn.click(
        lambda: gr.update(visible=True),
        outputs=add_course_modal
    )
    
    cancel_btn.click(
        lambda: gr.update(visible=False),
        outputs=add_course_modal
    )
    
    # Add course submission
    def submit_and_close(pdf, name):
        message, courses_update, _ = add_course(pdf, name)
        return message, courses_update, gr.update(visible=False)
    
    submit_course_btn.click(
        submit_and_close,
        inputs=[pdf_upload, course_name_input],
        outputs=[upload_status, course_list, add_course_modal]
    )
    
    # Course selection updates grade table
    def update_grade_section(course_name):
        grade_display, table, categories = select_course(course_name)
        if course_name:
            title = f"## Grades For: {course_name}"
        else:
            title = "## Grades For:"
        return title, grade_display, table, categories
    
    course_list.change(
        update_grade_section,
        inputs=course_list,
        outputs=[grade_section_title, current_grade_display, grade_table, grade_category]
    )
    
    # Chat functionality
    msg_input.submit(
        chat_with_bot,
        inputs=[msg_input, chatbox],
        outputs=chatbox
    ).then(
        lambda: "",
        outputs=msg_input
    )
    
    send_btn.click(
        chat_with_bot,
        inputs=[msg_input, chatbox],
        outputs=chatbox
    ).then(
        lambda: "",
        outputs=msg_input
    )
    
    # Add grade functionality - use selected course from course_list
    def add_grade_handler(selected_course, category, score, max_score):
        result = add_grade_to_course(selected_course, category, score, max_score)
        return result[0], result[1], result[2], result[3], gr.update(visible=True)
    
    add_grade_btn.click(
        add_grade_handler,
        inputs=[course_list, grade_category, grade_score, grade_max],
        outputs=[grade_add_status, current_grade_display, grade_table, grade_category, grade_add_status]
    )

if __name__ == "__main__":
    app.launch(share=True)