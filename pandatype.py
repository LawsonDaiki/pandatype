import curses
import time
import csv
import random

curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)   # Red text, black background
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Green text, black background
curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Magenta text, black background

class TypeGame:
    def __init__(self, stdscr, words_list):
        self.stdscr = stdscr
        self.start_time = None
        self.run_time = None
        self.words_list = words_list
        self.input_words_list = []
        self.selected_words_list = []
        self.is_game_over = False
        self.build_text()
    
    def build_text(self):
        words_count = 20
        self.selected_words_list = random.sample(self.words_list, words_count)

    def start_stopwatch(self):
        if self.input_words_list and len(self.input_words_list[0]) == 1:
            self.start_time = time.time()

    def handle_game_over(self, key):
        if key == 32 and len(self.input_words_list) > len(self.selected_words_list):
            self.is_game_over = True
            if not self.run_time:
                self.run_time = time.time() - self.start_time
        if self.is_game_over:
            self.stdscr.addstr("\nGAME OVER\n", curses.color_pair(1))
    
    def reset(self):
        self.start_time = time.time() # It is like this (and not None) because print_footer_message() will need to call self.elapsed_time() to print 0.00 seconds
        self.input_words_list = []
        self.run_time = None
        self.is_game_over = False
        self.build_text()
    
    def elapsed_time(self):
        if self.run_time:
            return self.run_time
        return time.time() - self.start_time
    
    def idx_exists(self, list, idx):
        try:
            list[idx]
            return True
        except IndexError:
            return False
    
    def print_header_message(self):
        self.stdscr.clear()
        self.stdscr.addstr("(Press 'ESC' to quit)...\n")
        self.stdscr.addstr("(Press 'Tab' to reset)...\n\n")
    
    def print_footer_message(self):
        self.stdscr.addstr("\n")
        self.stdscr.addstr(f"time: {self.elapsed_time():.2f} seconds\n")
        self.stdscr.addstr("wpm: <>\n")
        self.stdscr.addstr("acc: <>\n")
        self.stdscr.addstr("test type: <>\n")

    def print_text(self):
        for right_word_idx, right_word in enumerate(self.selected_words_list):
            # 1. print inputed words
            if self.idx_exists(self.input_words_list, right_word_idx) and self.input_words_list[right_word_idx] != '':
                # 1.1 print inputed characters
                for input_char_idx, input_char in enumerate(self.input_words_list[right_word_idx]):
                    # 1.1.1 check correct and incorrect characters and print them
                    if self.idx_exists(right_word, input_char_idx):
                        right_char = right_word[input_char_idx]
                        if input_char == right_char: # for matching letters, print green characters
                            self.stdscr.addstr(f"{right_char}", curses.color_pair(2))
                        else: # for not matching inputs, print red characters
                            self.stdscr.addstr(f"{right_char}", curses.color_pair(1))
                    # 1.1.2 if the inputed word has more characters than right word, print the extra characters in magenta
                    else:
                        self.stdscr.addstr(f"{input_char}", curses.color_pair(3))
                
                # 1.2 print the remainder characters
                for right_char_idx, right_char in enumerate(right_word):
                    if not self.idx_exists(self.input_words_list[right_word_idx], right_char_idx):
                        self.stdscr.addstr(f"{right_char}")

                # 1.3 print space at the end of each word
                self.stdscr.addstr(f" ")
            
            # 2. print the remainder words
            else:
                remainder_words = " ".join(self.selected_words_list[right_word_idx:])
                self.stdscr.addstr(f"{remainder_words}")
                break
    
    def handle_input(self, key):
        if key == 9: # on key 'Tab' reset game
            self.reset()
            return
        elif key == 32: # on key "Space" jump to the next word
            if self.input_words_list[-1] == '': # if the user try to press space key in sequence, the game will catch only the first press.
                return
            self.input_words_list.append('')
            return
        elif key == 127: # on key "Delete" erase last inputed character
            if self.input_words_list[-1] != '':
                self.input_words_list[-1] = self.input_words_list[-1][:-1]
            return
        elif self.input_words_list:
            self.input_words_list[-1] += chr(key)
            return
        else: # for case when is the first input of the game
            self.input_words_list.append(chr(key))
    
    def on_key_press(self, key):
        self.handle_input(key)
        self.start_stopwatch()
        
        self.print_header_message()
        self.print_text()
        self.print_footer_message()

        #self.stdscr.addstr(f"\nKey pressed: {key} ('{chr(key)}')\n")

        self.handle_game_over(key)

def select_csv_file():
    words_list = []
    with open("words/english/english_100.csv", mode="r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row[0]) == 1:
                continue
            words_list.append(row[0])
    return words_list

def main(words_list):
    """
    Function to execute the core typing game logic.
    """
    def key_listener(stdscr):
        stdscr.nodelay(True)  # Make getch() non-blocking

        type_text = TypeGame(stdscr, words_list)
        type_text.print_header_message()
        type_text.print_text()
        
        while True:
            key = stdscr.getch()
            if key != -1:  # If a key is pressed
                if key == 27:  # Exit on 'ESC'
                    break
                
                type_text.on_key_press(key)

                stdscr.refresh()

    curses.wrapper(key_listener) # Run the curses application

if __name__ == "__main__":
    words_list = select_csv_file()
    main(words_list)