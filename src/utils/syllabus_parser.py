import anthropic
import os
import json
from dotenv import load_dotenv

load_dotenv()

class SyllabusParser:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def parse_grading_structure(self, syllabus_text):
        """Extracts grading breakdown from syllabus text"""
        
        prompt = f"""Analyze this course syllabus and extract the grading structure.

Syllabus text:
{syllabus_text}

Extract:
1. Grading breakdown (what percentage each category is worth)
2. Number of assignments in each category (if mentioned, otherwise default to 1)

Return ONLY valid JSON in this exact format:
{{
  "grading_breakdown": {{
    "category_name": percentage_as_decimal
  }},
  "assignment_counts": {{
    "category_name": number_of_assignments
  }}
}}

Example:
{{
  "grading_breakdown": {{
    "homeworks": 0.25,
    "midterm 1": 0.30,
    "midterm 2": 0.35,
    "participation": 0.10
  }},
  "assignment_counts": {{
    "homeworks": 4,
    "midterm": 1,
    "final_project": 1,
    "participation": 1
  }}
}}

Important:
- Percentages must be decimals (0.25 not 25)
- If assignment count not specified, use 1
- Category names should be lowercase with underscores

Return ONLY the JSON, no other text."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        json_text = response.content[0].text.strip()
        
        # AI generated: Claude (66-84)
        if json_text.startswith("```"):
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:]
        
        try:
            grading_info = json.loads(json_text)
            
            # Ensure all categories have assignment counts
            for category in grading_info.get("grading_breakdown", {}).keys():
                if category not in grading_info.get("assignment_counts", {}):
                    grading_info["assignment_counts"][category] = 1
            
            return grading_info
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Response was: {json_text}")
            return None


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
    
    from src.extraction.pdf_to_text_chunks import process_syllabus
    

    syllabus_dir = "data/duke_syllabi"
    pdfs = [f for f in os.listdir(syllabus_dir) if f.endswith('.pdf')]
    parser = SyllabusParser()

    # testing parser fn for all 4 pdfs
    for pdf in pdfs:
      test_pdf = os.path.join(syllabus_dir, pdf)
      result = process_syllabus(test_pdf)
      print("\nExtracting grading structure...")
      grading_info = parser.parse_grading_structure(result['text'])

      if grading_info:
          print("\nGrading Breakdown:")
          print(json.dumps(grading_info, indent=2))
      else:
          print("\n FAILED to parse grading structure")