import re
import tkinter as tk
from tkinter import filedialog
import os

class ChatLogAnalyzer:
    def __init__(self, tutor_name):
        self.tutor_name = tutor_name
        self.text = ""
        self.matches = []
        self.correct_answers = {}
        self.answered_questions = set()

    def load_chat_logs(self, file_path):
        try:
            with open(file_path, "r") as file:
                self.text = file.read()

            # Define a regular expression pattern to match each line
            pattern = r'(\d+:\d+:\d+)\s+From\s+(.*?)\s+To\s+Everyone:\n(.*)'

            # Use re.findall to find all matching patterns in the text
            self.matches = re.findall(pattern, self.text, re.MULTILINE)
        except FileNotFoundError:
            print("File not found. Please provide a valid file path.")
            exit(1)

    def extract_tutor_questions(self):
        return [question for question, answer in self.correct_answers.items()]
    
    def load_correct_answers(self):
        file_path = filedialog.askopenfilename(title="Select Correct Answers File")
        if not file_path:
            print("No correct answers file selected. Defaulting to an empty dictionary.")
            return
        try:
            with open(file_path, "r") as file:
                # Read all lines from the correct answers file
                lines = file.readlines()

                # Extract questions and answers from the file
                for line in lines:
                    if ":" in line:
                        question, answer = map(str.strip, line.split(":", 1))
                        self.correct_answers[question.lower()] = answer.lower()
        except FileNotFoundError:
            print("Correct answers file not found. Defaulting to an empty dictionary.")

    def analyze_participation(self, messages):
        participation_score = 0

        for message in messages:
            # Criteria 1: Correct Answers to Questions
            correct_answer_count = self.count_correct_answers_keywords(message)
            participation_score += correct_answer_count
        
        # Clear the set of answered questions after processing each student
        self.answered_questions.clear()
        
        return participation_score

    def count_correct_answers_keywords(self, message):
        participation_score = 0

        # Iterate over each question and its correct answer
        for question, correct_answer in self.correct_answers.items():
            # Use keyword matching to find occurrences of any part of the correct answer in the message
            if self.keyword_match(message.lower(), correct_answer.lower()):
                if question not in self.answered_questions:  # Check if already answered
                    participation_score += 1
                    self.answered_questions.add(question)  # Add to answered questions

        return participation_score

    def keyword_match(self, text, keyword):
        # Check if any part of the keyword is present in the text
        return keyword in text.lower()
    
    def export_results_to_file(self):
        try:
            folder_path = os.path.dirname(os.path.abspath(__file__))
            file_name = "results.txt"  # Specify the name of the results file
            file_path = os.path.join(folder_path, file_name) # Creates the path to the results file

            # Open the results file for writing
            with open(file_path, "w") as file:
                 # Write header with tutor's name
                file.write(f"Results for {self.tutor_name}:\n\n")

                # Write Correct Answers section
                file.write("Correct Answers:\n")
                for question, answer in self.correct_answers.items():
                    file.write(f"{question}: {answer}\n")

                # Write Participation Results section
                file.write("\nParticipation Results:\n")
                for message in self.matches:
                    file.write(f"{message[0]} From {message[1]}: {message[2]}\n")

             # Print a success message with the file path
            print(f"Results exported to {file_path}")
        except Exception as e:
            print(f"Error exporting results: {e}") #Handles exceptions
    