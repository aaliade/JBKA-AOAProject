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
        number = 0
        file_path = filedialog.askopenfilename(title="Select Correct Answers File")
        if not file_path:
            print("No correct answers file selected. Defaulting to an empty dictionary.")
            return
        try:
            with open(file_path, "r") as file:
                # Read all lines from the correct answers file
                lines = file.readlines()
                number = len(lines)
                print("Correct", number)
                # Extract questions and answers from the file
                for line in lines:
                    if ":" in line:
                        question, answer = map(str.strip, line.split(":", 1))
                        print(f"Loaded: {question.lower()} => {answer.lower()}")
                        self.correct_answers[question.lower()] = answer.lower()
        except FileNotFoundError:
            print("Correct answers file not found. Defaulting to an empty dictionary.")
        return number


    def get_correct_answers(self, timestamps, senders, messages, sender_name):
        correct_answers_count = 0
        answered_questions = set()
        current_question = None
        current_answer = None  # Variable to store the current correct answer

        for timestamp, sender, message in zip(timestamps, senders, messages):
            print(f"{timestamp} {sender} {message}")

            # Check if the message is from the tutor and contains a question
            if sender.lower() == self.tutor_name.lower() and "?" in message:
                print(f"Tutor Question: {sender} {self.tutor_name} {message} \n")
                # Save the current question and its correct answer, reset the answered questions set
                current_question = message.strip().lower()  # Added strip() to remove whitespaces
                current_answer = self.correct_answers.get(current_question, None)
                answered_questions = set()

                print(f"Current Question and answer     {current_question} {current_answer}")

            # Check if the message is from the specified sender
            elif sender.lower() == sender_name.lower():
                # Check if the current question exists (i.e., a tutor question has been encountered)
                if current_question is not None:
                    # Check if the sender has not answered the current question yet
                    if current_question not in answered_questions:
                        if current_answer is not None and self.is_correct_answer(message, current_answer):
                            correct_answers_count += 1
                            answered_questions.add(current_question)
                            print(f"Correct Answer: {message}")

        print(f"{correct_answers_count} End\n")
        return correct_answers_count

    def is_correct_answer(self, message, correct_answer):
        # Check if the message is correct based on keyword matching with the stored correct answer
        return self.word_keyword_match(message.lower(), correct_answer.lower())
    
    def word_keyword_match(self, text, keyword):
        # Check if any part of the keyword is present in the text
        return keyword in text.lower()

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
            # Use Boyer-Moore matching to find occurrences of any part of the correct answer in the message
            if self.boyer_moore_match(message.lower(), correct_answer.lower()):
                if question not in self.answered_questions:  # Check if already answered
                    participation_score += 1
                    self.answered_questions.add(question)  # Add to answered questions

        return participation_score
   
    def boyer_moore_match(self, text, pattern):
        # Preprocessing: Build the bad character skip table
        bad_char_skip = {pattern[i]: max(1, len(pattern) - 1 - i) for i in range(len(pattern) - 1)}

        # Search with Boyer-Moore algorithm
        i = len(pattern) - 1
        while i < len(text):
            j = len(pattern) - 1
            while text[i] == pattern[j]:
                if j == 0:
                    return True  # Match found
                i -= 1
                j -= 1
            i += max(bad_char_skip.get(text[i], len(pattern)), 1)

        return False  # No match found
    
    def export_results_to_file(self):
        try:
             # Specify the file path for the results file
            file_path = "results.txt"

            # Open the file in write mode
            with open(file_path, "w") as file:
                file.write(f"Results for {self.tutor_name} class:\n\n")
                file.write("Student Participation Grades:\n")

                # Dictionary to store messages for each sender (student)
                sender_messages = {}
                 # Iterate over matches to organize messages by sender
                for match in self.matches: 
                    timestamp, sender, message = match
                    if sender.lower() != self.tutor_name.lower():
                        if sender not in sender_messages:
                            sender_messages[sender] = []
                        sender_messages[sender].append(message)

                 # Iterates over sender_messages to write each student's participation grade
                for sender, messages in sender_messages.items():
                    participation_grade = self.analyze_participation(messages)
                    correct_answers_count = sum(self.count_correct_answers_keywords(message) for message in messages)

                     # Writes the information to the file
                    file.write(f"{sender}: Grade = {correct_answers_count}   Questions Answered = {len(messages)}   Correct Answers = {correct_answers_count}\n")

            # Prints a success message
            print(f"Results exported to {file_path}")
        except Exception as e:
             # Print an error message if an exception occurs during the export
            print(f"Error exporting results: {e}")