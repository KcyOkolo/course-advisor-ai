from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import sys
import os

class RAGSystem:
    def __init__(self):
        print("Loading embedding model")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chunks = [] #holds chunks from all syllabi
        self.chunk_metadata = [] #holds corresponding course name of chunks in self.chunks[]
        self.index = None
        print("Model loaded!")

    def add_course(self, course_name, chunks):
        """Place all chunks from all syllabi in self.chunks[] and build
            Parallel list of corresponding course names"""
        print(f"Adding in chunks from {course_name} and making parallel meta data entries")
        for chunk in chunks:
            self.chunks.append(chunk)
            self.chunk_metadata.append(course_name.upper())
    
    def index_chunks(self):
        """Creates embeddings and FAISS index for all chunks across all syllabi"""
        print(f"Creating embeddings for {len(self.chunks)} chunks")
        
        embeddings = self.model.encode(self.chunks, show_progress_bar=True)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        print(f"Indexed {len(self.chunks)} chunks!")
    
    def retrieve(self, question, num_courses, course_filter=None, k=2):
        """Given user prompt, retrieves top k relevant chunks """
        if self.index is None:
            return []
        
        if course_filter:
            num_filters = len(course_filter)
            k = num_filters * k
        

        question_embedding = self.model.encode([question])
        
        distances, indices = self.index.search(question_embedding.astype('float32'), num_courses*k*3)
        
        results = []
        retrieved_course_counts = {}
        for i, dist in zip(indices[0], distances[0]):


            retrieved_chunk_course = self.chunk_metadata[i]

            if course_filter and retrieved_chunk_course not in course_filter:
                continue 
            

            current_count = retrieved_course_counts.get(retrieved_chunk_course, 0)

            if current_count >= 3:
                continue

            retrieved_course_counts[retrieved_chunk_course] = current_count + 1
            
            retrieved_chunk = self.chunks[i]

            results.append({
                'chunk': retrieved_chunk,
                'course': retrieved_chunk_course,
                'distance': float(dist)
            })


            if len(results)>= k:
                break
        
        return results

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from extraction.pdf_to_text_chunks import process_syllabus
    
    syllabus_dir = "data/duke_syllabi"
    pdfs = [f for f in os.listdir(syllabus_dir) if f.endswith('.pdf')]

    if not pdfs:
        print("No PDFs in data/duke_syllabi/")
        sys.exit(1)

    # Getting chunks from numerous syllabi from pdf_to_text_chunks.py and putting meta data in one array
    rag = RAGSystem()
    num_courses = 0
    course_names = []


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
        rag.add_course(course_name, result['chunks'])
        num_courses+=1

    
    print(f"\nTesting RAG filtering & retrieval for index with multiple pdfs:")
    rag.index_chunks()


    test_1 = "What is the late policy for my CS240 class?"
    course_filter1 = ["CS240"]
    print(f"\n  Question: {test_1}")
    results = rag.retrieve(test_1, num_courses, course_filter1)
    for i, result in enumerate(results, 1):
        print(f"\n Retrieved Chunk {i}; {result['course']} (Distance: {result['distance']:.2f}):")
        print(result['chunk'][:300] + "...")


    test_2 = "Which of my classes have finals?"
    course_filter2 = ["CS240", "CS372", "PSY277", "CS316"]
    print(f"\n  Question: {test_2}")
    results = rag.retrieve(test_2, num_courses, course_filter2)
    for i, result in enumerate(results, 1):
        print(f"\n Retrieved Chunk {i}; {result['course']} (Distance: {result['distance']:.2f}):")
        print(result['chunk'][:300] + "...")



    test_3 = "Which of my course policy is stricter? CS240 or PSY277?"
    course_filter3 = ["CS240","PSY277"]
    print(f"\n  Question: {test_3}")
    results = rag.retrieve(test_3, num_courses, course_filter3)
    for i, result in enumerate(results, 1):
        print(f"\n Retrieved Chunk {i}; {result['course']} (Distance: {result['distance']:.2f}):")
        print(result['chunk'][:300] + "...")


    test_4 = "Which class seems the easiest to get an A?"
    course_filter4 = ["CS240", "CS372", "PSY277", "CS316"]
    print(f"\n  Question: {test_4}")
    results = rag.retrieve(test_4, num_courses, course_filter4)
    for i, result in enumerate(results, 1):
        print(f"\n Retrieved Chunk {i}; {result['course']} (Distance: {result['distance']:.2f}):")
        print(result['chunk'][:300] + "...")

    test_5 = "Summarize the sylabus for CS240, what are they key things I need to know?"
    course_filter5 = ["CS240"]
    print(f"\n  Question: {test_5}")
    results = rag.retrieve(test_5, num_courses, course_filter5)
    for i, result in enumerate(results, 1):
        print(f"\n Retrieved Chunk {i}; {result['course']} (Distance: {result['distance']:.2f}):")
        print(result['chunk'][:300] + "...")
