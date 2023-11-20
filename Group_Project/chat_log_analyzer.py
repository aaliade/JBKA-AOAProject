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

    def get_correct_answers(self, timestamps, senders, messages, sender_name):
        correct_answers_count = 0
        answered_questions = set()
        current_question = None

        for timestamp, sender, message in zip(timestamps, senders, messages):
            print(f"Beginning {timestamp} {sender} {message} End==")

            # Check if the message is from the tutor and contains a question
            if sender.lower() == self.tutor_name.lower() and "?" in message:
                print(f"== {sender} {self.tutor_name} {message} \n")
                current_question = message.lower()

            # Check if the message is from the specified sender
            elif sender.lower() == sender_name.lower():
                #  Check if the message is from a student and it's not a repeated answer
                if current_question is not None and current_question not in answered_questions:
                    if self.is_correct_answer(message):
                        correct_answers_count += 1
                        answered_questions.add(current_question)
                        print(f"Correct Answer: {message}")

        print(f"Beginning {correct_answers_count} End\n")
        return correct_answers_count

    def is_correct_answer(self, message):
        # Iterate over each question and its correct answer
        for question, correct_answer in self.correct_answers.items():
            # Use keyword matching to find occurrences of any part of the correct answer in the message
            if self.keyword_match(message.lower(), correct_answer.lower()):
                return True

        return False

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
