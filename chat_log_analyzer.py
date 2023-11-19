import re
import tkinter as tk
from tkinter import filedialog

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
