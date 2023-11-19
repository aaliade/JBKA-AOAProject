import re
import tkinter as tk
from tkinter import filedialog

class KeywordMatcher:
    def __init__(self, keyword):
        self.keyword = keyword
        self.prefix_table = self.build_prefix_table()

    def build_prefix_table(self):
        prefix_table = [0] * len(self.keyword)
        j = 0

        for i in range(1, len(self.keyword)):
            while j > 0 and self.keyword[i] != self.keyword[j]:
                j = prefix_table[j - 1]

            if self.keyword[i] == self.keyword[j]:
                j += 1

            prefix_table[i] = j

        return prefix_table

    def search(self, text):
        j = 0
        for i in range(len(text)):
            while j > 0 and text[i] != self.keyword[j]:
                j = self.prefix_table[j - 1]

            if text[i] == self.keyword[j]:
                j += 1

            if j == len(self.keyword):
                return True

        return False

    def search(self, text):
        j = 0
        for i in range(len(text)):
            while j > 0 and text[i] != self.keyword[j]:
                j = self.prefix_table[j - 1]

            if text[i] == self.keyword[j]:
                j += 1

            if j == len(self.keyword):
                return True

        return False


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

    def is_correct_answer_kmp(self, message):
        message = message.lower()

        for question, correct_answer in self.correct_answers.items():
            matcher = KeywordMatcher(correct_answer.lower())
            if matcher.search(message):
                print(f"Checking: Question: {question}, Correct Answer: {correct_answer}, Message: {message}")
                return True

        return False


    def is_productive(self, message):
        # Define criteria for a productive message
        productive_keywords = ["question", "discussion", "answer", "explanation", "insight"]
        message = message.lower()

        return any(keyword in message for keyword in productive_keywords)

    def analyze_participation(self, messages):
        participation_score = 0
        correct_answers_count = 0  # Initialize the correct_answers_count

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

        # Criteria 5: Correct Answers to Questions (using KMP)
        for message in messages:
            correct_answer = self.is_correct_answer_kmp(message)
            if correct_answer:  # Change this line
                correct_answers_count += 1
                print(f"Correct Message: {message}, Correct Answer: {correct_answer}")

        participation_score += correct_answers_count
        print("[Correct Message Number]", correct_answers_count)

        return participation_score
    
    def count_correct_answers(self, messages):
        correct_answers_count = sum(1 for message in messages if self.is_correct_answer_kmp(message))
        return correct_answers_count