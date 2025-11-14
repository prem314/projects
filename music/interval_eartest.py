"""
Note: This code did not work with python 3.11 although it did work for 3.9
"""

import pyaudio
import numpy as np
import random
import sys
import time

class AudioGame:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.fs = 44100
        self.volume = 0.5
        self.score = 0
        self.correct_f = []
        self.wrong_f = []
        self.no_of_questions = 0

    def play_tone(self, freq, duration):
        samples = (np.sin(2 * np.pi * np.arange(self.fs * duration) * freq / self.fs)).astype(np.float32)
        stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=self.fs, output=True)
        stream.write(self.volume * samples)
        stream.stop_stream()
        stream.close()

    def next_question(self):
        self.res_first = False
        self.res_second = False
        self.ans1 = None
        self.ans2 = None      
        
        
        if self.no_of_questions < 10:
            self.no_of_questions += 1
            print("")
            print(f"Round {self.no_of_questions}")
            print("")
            self.f = random.uniform(100, 4000)
            self.semi_tone_diff = random.randint(-self.n, self.n)
            k = 2 ** (abs(self.semi_tone_diff) / 12)
            self.new_f = self.f * k if self.semi_tone_diff > 0 else self.f / k if self.semi_tone_diff < 0 else self.f
            self.correct_answer = "w" if self.semi_tone_diff > 0 else "s" if self.semi_tone_diff < 0 else '0'
            self.play_the_question()
        else:
            print(f"Your final score is {self.score} out of 10.")
            print("You made mistakes for the following frequencies:", self.wrong_f)
            sys.exit()

    def play_the_question(self):
        self.play_tone(self.f, 1)
        time.sleep(0.5)
        self.play_tone(self.new_f, 1)
        
        if self.res_first == False:
            self.user_input = input("Press 'a' to replay, 'w' for higher frequency, 's' for lower frequency, '0' for same frequency: ").lower()
            print(f"your response was {self.user_input}")
        
        if self.ans1 == False or self.ans2 == False:
            self.user_input = input("Press 'd' to continue").lower()
            print(f"your response was {self.user_input}")
        self.response_processing()

    def response_processing(self):
        
        if self.res_first == False:
                
            if self.user_input in ['w', 's', '0']:
                
                if self.user_input == self.correct_answer:
                    print("your response to 1st qeustion was correct!")
                    self.ans1 = True
                else:
                    self.ans1 = False
                    self.ans2 = False
                    self.res_second=True
                    
                    print("your response to 1st question was incorrect!")
                self.res_first = True #if the response is w,s or 0, then user has responsed to the first question.
        
                
        if self.res_first == True and self.res_second == False:
            if self.n == 1 or self.user_input == '0': #answering the second question is redundant if these conditions are met.
                self.res_second = True
                self.ans2 = self.ans1
                print("you don't need to respond to the second question")
            elif self.ans1 == True:
                
                user_input2 = input("Now guess the interval: ")
                if user_input2 == str(abs(self.semi_tone_diff)):  # Added missing self.
                    
                    self.ans2 = True
                    self.res_second = True
                elif user_input2 in self.string_on_n:
                    self.ans2 = False
                    self.res_second = True
            elif self.ans1 == False:
                self.res_second = True
                    
            
        print("all the responses",self.res_first, self.res_second, self.ans1, self.ans2)
            
        
        if self.res_first == True and self.res_second == True:
            print("you have responded to all questions")
            if self.user_input == 'd':
                self.next_question()
        
        if self.ans1 == True and self.ans2 == True:
            print("Totally correct responses!")
            self.score +=1
            self.next_question()
        
        elif self.ans1 == False or self.ans2 == False:
            print("some answers were incorrect")
            self.incorrect_answer()
                
        else:
            print("did you give valid response?")
            self.play_the_question()

    def incorrect_answer(self):
        
        if int(self.f) not in self.wrong_f:
            print(self.wrong_f)
            print(self.f)
            print(f"Incorrect answer. The correct answer was '{self.correct_answer}' with a semi-tone difference of {abs(self.semi_tone_diff)}.")  # Added missing self.
            self.wrong_f.append(int(self.f))  # Added missing self.
        self.play_the_question()
        

    def main(self):
        self.n = int(input("Enter an integer n for semi-tone range: "))
        while self.n < 1:
            self.n = int(input("ERROR. Enter a POSITIVE integer for semi-tone range: "))
        self.string_on_n = [str(i) for i in range(1, abs(self.n) + 1)]
        self.next_question()  # Added missing self.n

if __name__ == "__main__":
    game = AudioGame()
    game.main()
