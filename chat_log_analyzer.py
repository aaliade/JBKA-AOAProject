import re
import tkinter as tk
from tkinter import filedialog

class ChatLogAnalyzer:
    def __init__(self, tutor_name):
        self.tutor_name = tutor_name
        self.text = ""
        self.matches = []
        self.correct_answers = {}

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

        # Criteria 1: Number of Messages Sent
        message_count = len(messages)
        if message_count >= 50:
            participation_score += 5
        elif message_count >= 30:
            participation_score += 4
        elif message_count >= 15:
            participation_score += 3
        elif message_count >= 5:
            participation_score += 2
        else:
            participation_score += 1

        # Criteria 2: Average Word Count in Messages
        total_word_count = sum(len(message.split()) for message in messages)
        average_word_count = total_word_count / message_count

        if average_word_count >= 20:
            participation_score += 3
        elif average_word_count >= 10:
            participation_score += 2
        elif average_word_count >= 5:
            participation_score += 1

        # Criteria 3: Engagement with Others
        response_count = sum(1 for message in messages if "response" in message.lower())
        participation_score += response_count

        # Criteria 4: Productive Messages
        productive_count = sum(1 for message in messages if self.is_productive(message))
        participation_score += productive_count

        # Criteria 5: Correct Answers to Questions
        correct_answer_count = sum(1 for message in messages if self.is_correct_answer(message))
        participation_score += correct_answer_count

        return participation_score

    def is_productive(self, message):
        # Define criteria for a productive message
        productive_keywords = ["question", "discussion", "answer", "explanation", "insight"]
        message = message.lower()

        return any(keyword in message for keyword in productive_keywords)
    
    def is_correct_answer(self, message):
        # Check if a message contains a correct answer to a question
        message = message.lower()

        for question, correct_answer in self.correct_answers.items():
            if question in message:
                print(f"Debug: Question '{question}' found in message '{message}'")
                if correct_answer in message:
                    print(f"Debug: Correct answer '{correct_answer}' found in message '{message}'")
                    return True
                else:
                    print(f"Debug: Incorrect answer found in message '{message}'")
        return False


    def count_correct_answers(self, messages):
        correct_answers_count = sum(1 for message in messages if self.is_correct_answer(message))
        return correct_answers_count