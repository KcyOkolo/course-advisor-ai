class GradeCalculator:
    def __init__(self, name, grading_breakdown, assignment_counts):
        """
        grading_breakdown is dict like {"homeworks": 0.25, "midterm": 0.30, ...}
        assignment_counts is dict like {"homeworks": 10, "midterm": 1, ...}
        """
        self.name = name
        self.grading_breakdown = grading_breakdown
        self.assignment_counts = assignment_counts
        self.grades = {} # % grade(s) under each category
        for category in grading_breakdown.keys():  # ["homeworks", "midterm",....]
            self.grades[category] = []

    
    def add_grade(self, category, score, max_score=100):
        """Add a grade for a category"""
        if category not in self.grades:
            print(f"{category} is not a category for this course")
            return False
        
        percentage = (score / max_score) * 100
        self.grades[category].append(percentage)
        return True

    def add_category(self, category, weight=0.0, counts=1):
        """Add a new category"""
        if category in self.grading_breakdown:
            print(f"{category} is already included for this course")
            return False

        self.grading_breakdown[category] = weight
        self.assignment_counts[category] = counts

        return True
    
    def get_category_grade(self, category):
        """Get %grade for a category"""
        if not self.grades[category]: #if no grades have been reported under that
            return None

        return sum(self.grades[category]) / len(self.grades[category])
    
    def get_current_total_grade(self):
        """Calculate %overall grade for course (scaled to completed work)"""
        total = 0
        weight_used = 0
        
        for category, weight in self.grading_breakdown.items():
            avg = self.get_category_grade(category)
            if avg is not None:
                total += avg * weight
                weight_used += weight
        
        if weight_used == 0:
            return 0
        
        # scaled to what's been completed
        return total / weight_used
    
    def get_summary(self):
        """Get grade summary for current course"""
        summary = {
            "course": self.name,
            "current_grade": self.get_current_total_grade(),
            "categories": {}
        }
        
        for category in self.grading_breakdown.keys():
            avg = self.get_category_grade(category)
            completed = len(self.grades[category])
            total = self.assignment_counts.get(category, 1)
            
            summary["categories"][category] = {
                "average": avg,
                "weight": self.grading_breakdown[category] * 100,
                "completed": completed,
                "total": total,
                "check": (total == completed),
                "remaining": total - completed
            }
        
        return summary

    def update_category_name(self, category, new_category_name):
        """edit the current category name"""
        if category not in self.grading_breakdown:
            print(f"{category} is not a category for this course")
            return False

        if new_category_name in self.grading_breakdown:
            print(f"{category} already exists")
            return False
        
        self.grading_breakdown[new_category_name] = self.grading_breakdown.pop(category)
        self.assignment_counts[new_category_name] = self.assignment_counts.pop(category)
        self.grades[new_category_name] = self.grades.pop(category)
        return True


    def update_category_count(self, category, count):
        """edit the current assignment count for a category"""
        if category not in self.assignment_counts:
            print(f"{category} is not a category for this course")
            return False
        
        self.assignment_counts[category] = count
        return True

        
    def update_category_grade(self, category, old_score, new_score):
        """edit one of the current %scores in a category"""
        if category not in self.grades:
            print(f"{category} is not a category for this course")
            return False

        if old_score not in self.grades[category]:
            print(f"{old_score} is not a score in {category}")
            return False
        
        i = self.grades[category].index(old_score)
        self.grades[category][i] = new_score
        return True

    def remove_category(self, category):
        """delete an existing category"""
        if category not in self.grading_breakdown:
            print(f"{category} is not a category for this course")
            return False

        self.grading_breakdown.pop(category)
        self.assignment_counts.pop(category)
        self.grades.pop(category)
        return True

    def remove_grade(self, category, score):
        """remove one of the existing %scores from a category"""
        if category not in self.grades:
            print(f"{category} is not a category for this course")
            return False
        if score not in self.grades[category]:
            print(f"{score} is not a number in this category")
            return False

        self.grades[category].remove(score)
        return True


if __name__ == "__main__":
    grading = {
        "homeworks": 0.25,
        "gradiance_exercises": 0.1,
        "project": 0.25,
        "in_class_exams": 0.4
    }
    
    counts = {
        "homeworks": 4,
        "gradiance_exercises": 11,
        "project": 1,
        "in_class_exams": 2
    }
    
    calc = GradeCalculator("CS316", grading, counts)
    
    
    print("Adding grades...")
    calc.add_grade("homeworks", 85, 100)
    calc.add_grade("homeworks", 90, 100)
    calc.add_grade("gradiance_exercises", 95, 100)
    calc.add_grade("gradiance_exercises", 88, 100)
    calc.add_grade("gradiance_exercises", 92, 100)
    
    # Get summary
    print("Grade Summary:")
    summary = calc.get_summary()
    print(f"\n{summary}")
    