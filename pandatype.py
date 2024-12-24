import sys
import curses
import time
import csv
import random
from pathlib import Path

curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)   # Red text, black background
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Green text, black background
curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Magenta text, black background
curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Black text, cyan background
curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)  # Black text, red background

class TypeGame():
    def __init__(self, stdscr, words_file_path):
        self.stdscr = stdscr
        self.start_time = None
        self.run_time = None
        self.words_file_path = words_file_path
        self.game_mode = words_file_path.as_posix().split('/')[-1]
        self.input_words_list = []
        self.selected_words_list = []
        self.correct_words_count = 0
        self.acc = 0
        self.progress = ''
        self.wpm = 0
        self.is_game_over = False
        self.build_text()

    def print_text(self, string):
        self.stdscr.addstr(string, curses.A_DIM)

    def print_text_bold(self, string):
        self.stdscr.addstr(string, curses.A_DIM | curses.A_BOLD)
    
    def print_text_bold_ul(self, string):
        self.stdscr.addstr(string, curses.A_DIM | curses.A_BOLD | curses.A_UNDERLINE)
    
    def print_typed_text(self, string):
        self.stdscr.addstr(string, curses.A_BOLD)
    
    def print_incorrect_typed_text(self, string):
        self.stdscr.addstr(string, curses.color_pair(1) | curses.A_BOLD)
    
    def print_game_over(self, string):
        self.stdscr.addstr(string, curses.color_pair(5) | curses.A_BOLD)
    
    def build_text(self):
        with self.words_file_path.open(mode='r') as file:
            csv_reader = csv.reader(file, delimiter='|')
            if self.words_file_path.as_posix().endswith('quotes.csv'):
                listed_words = list(csv_reader)
                random.shuffle(listed_words)
                self.selected_words_list = listed_words[0][0].split()
            else:
                words_sample = random.sample(list(csv_reader), 40)
                self.selected_words_list = [x[0] for x in words_sample]

    def start_stopwatch(self):
        if self.input_words_list and len(self.input_words_list[0]) == 1:
            self.start_time = time.time()

    def check_game_over(self, key):
        self.is_game_over = len(self.input_words_list) > len(self.selected_words_list)

    def handle_game_over(self):
        if self.is_game_over:
            self.print_game_over(" GAME OVER \n")
            if not self.run_time:
                self.run_time = time.time() - self.start_time
    
    def reset(self):
        self.start_time = None
        self.input_words_list = []
        self.run_time = None
        self.is_game_over = False
        self.build_text()
    
    def elapsed_time(self):
        if self.run_time:
            return self.run_time
        return time.time() - self.start_time if self.start_time else 0.0
    
    def idx_exists(self, list, idx):
        try:
            list[idx]
            return True
        except IndexError:
            return False
    
    def print_footer_message(self):
        self.print_text("\n")

        if self.is_game_over:
            self.print_game_over(f" progress {self.progress} \n")
            self.print_game_over(f" time: {self.elapsed_time():.2f} seconds \n")
            self.print_game_over(f" wpm: {self.wpm:.0f} \n")
            self.print_game_over(f" acc: {self.acc:.0f} % \n\n")
        else:
            self.print_text(f" progress {self.progress}\n")
            self.print_text(f" time: {self.elapsed_time():.2f} seconds\n")
            self.print_text(f" wpm: {self.wpm:.0f}\n")
            self.print_text(f" acc: {self.acc:.0f} %\n\n")

        self.print_text("(Press 'Esc' to quit)...\n")
        self.print_text("(Press 'Tab' to reset)...\n\n")

    def print_game_phrase(self):
        for right_word_idx, right_word in enumerate(self.selected_words_list):
            # 1. print inputted words
            if self.idx_exists(self.input_words_list, right_word_idx) and self.input_words_list[right_word_idx] != "":
                input_word = self.input_words_list[right_word_idx]
                # 1.1 print inputted characters
                for input_char_idx, input_char in enumerate(input_word):
                    # 1.1.1 check correct and incorrect characters and print them
                    if self.idx_exists(right_word, input_char_idx):
                        right_char = right_word[input_char_idx]
                        if input_char == right_char: # for matching letters
                            self.print_typed_text(right_char)
                        else: # for not matching inputs
                            self.print_incorrect_typed_text(right_char)
                    # 1.1.2 if the inputted word has more characters than right word, print the extra characters in magenta
                    else:
                        self.print_incorrect_typed_text(input_char)
                
                # 1.2 print the remainder characters
                if len(input_word) < len(right_word):
                    # 1.2.1 place underline cursor in the first character in the remainder characters
                    if right_word_idx == len(self.input_words_list) - 1:
                        self.print_text_bold_ul(right_word[len(input_word)])
                        self.print_text_bold(right_word[len(input_word) + 1:])
                    #1.2.2 print the remainder characters without the underline cursor
                    else:
                        self.print_text_bold(right_word[len(input_word):])

                # 1.3 print space at the end of each word
                if right_word_idx == len(self.input_words_list) - 1 and len(input_word) >= len(right_word): # case when we need to place an underline cursor in a space
                    self.print_text_bold_ul(" ")
                else:
                    self.print_text_bold(" ")
            # 2. case when the user pressed space key, we need to place the cursor in the first character of the next word
            elif self.idx_exists(self.input_words_list, right_word_idx) and self.input_words_list[right_word_idx] == "":
                self.print_text_bold_ul(right_word[0])
                self.print_text_bold(f"{right_word[1:]} ")
            # 3. print the remainder words
            else:
                remainder_words = " ".join(self.selected_words_list[right_word_idx:])
                self.print_text_bold(remainder_words)
                break
        self.stdscr.addstr("\n")

    def print_game_text(self):
        self.print_text(f" game mode: {self.game_mode}\n\n") # subtitle
        self.print_game_phrase()
        self.print_footer_message()
    
    def handle_input(self, key):
        if key == 9: # on key 'Tab' reset game
            self.reset()
        elif key == 32 and self.input_words_list[-1] != '': # on key "Space" jump to the next word. If the user try to press space key in sequence, the game will catch only the first press.
            self.input_words_list.append('')
        elif key == 127 and self.input_words_list[-1] != '': # on key "Delete" erase last inputted character. Don't allow user to delete the previous word
            self.input_words_list[-1] = self.input_words_list[-1][:-1]
        elif self.input_words_list: # on a normal key press, append character to last item
            self.input_words_list[-1] += chr(key)
        else: # this is case when is the first input of the game
            self.input_words_list.append(chr(key))
    
    def get_metrics(self):
        # get correct words
        self.correct_words_count = 0
        for input_word_idx, input_word in enumerate(self.input_words_list):
            if self.idx_exists(self.selected_words_list, input_word_idx) and input_word == self.selected_words_list[input_word_idx]:
                self.correct_words_count += 1
        
        # get accuracy
        inputted_words_count = len(self.input_words_list) if len(self.input_words_list) < len(self.selected_words_list) else len(self.selected_words_list)
        self.acc = 0 if inputted_words_count == 0 else self.correct_words_count/inputted_words_count*100
        
        # get progress
        self.progress = f"{inputted_words_count}/{len(self.selected_words_list)}"

        # get wpm
        self.wpm = 0 if self.elapsed_time() == 0 else self.correct_words_count/self.elapsed_time()*60

    def on_key_press(self, key):
        self.handle_input(key)
        self.check_game_over(key)
        self.start_stopwatch()
        self.get_metrics()
        
        # self.stdscr.addstr(f"\nKey pressed: {key} ('{chr(key)}')\n")

        self.handle_game_over()

def convert_key_to_int(key):
    try:
        return int(chr(key))  # Try converting to integer
    except ValueError:
        return

def main():
    """
    Function to execute the core typing game logic.
    """
    def pandatype_game(stdscr):
        stdscr.nodelay(True)  # Make getch() non-blocking

        # decorator for key listener function
        def key_listener_decorator(func):
            def listener_wrapper(text_to_print):
                while True:
                    time.sleep(.01) # Sleep script at each iteration run to reduce CPU usage
                    stdscr.clear()
                    stdscr.addstr(" PANDATYPE \n", curses.color_pair(4) | curses.A_BOLD)
                    if callable(text_to_print):
                        text_to_print()
                    elif isinstance(text_to_print, str):
                        stdscr.addstr(text_to_print) # print text_to_print outside the condition "if key != -1"
                    key = stdscr.getch()
                    func_return = False
                    if key != -1: # If a key is pressed
                        # Exit on 'ESC' press
                        if key == 27:
                            sys.exit()
                        func_return = func(key)
                    stdscr.refresh()
                    if func_return: break
                return func_return
            return listener_wrapper

        # 1. Initial screen where user have to select the language
        language_directory = Path.cwd() / 'words'
        # 1.1 Build text for language selection and build language_options dict
        select_language_text = 'Select language:\n'
        language_options = {}
        for idx, language_path in enumerate(language_directory.iterdir()):
            language = str(language_path).split('/')[-1]
            select_language_text += f'{idx}. {language}\n'
            language_options[idx] = language
        
        # 1.2 Key listening function for languege selection screen
        @key_listener_decorator
        def language_selection(key):
            selected_language_key = convert_key_to_int(key)
            if selected_language_key in language_options.keys():
                return language_options[selected_language_key]
        selected_language = language_selection(select_language_text)
        selected_language_path = language_directory / selected_language

        # 2. Second screen where use have to select game mode
        # 2.1 Build text to print for game mode selection and build game_mode_options dict
        select_game_mode_text = 'Select game mode: \n'
        game_mode_options = {}
        for idx, game_mode_path in enumerate(selected_language_path.iterdir()):
            game_mode = str(game_mode_path).split('/')[-1]
            select_game_mode_text += f'{idx}. {game_mode}\n'
            game_mode_options[idx] = game_mode

        # 2.2 Key listening function for game mode selection scree
        @key_listener_decorator
        def game_mode_selection(key):
            selected_game_mode_key = convert_key_to_int(key)
            if selected_game_mode_key in game_mode_options.keys():
                return game_mode_options[selected_game_mode_key]
        selected_game_mode = game_mode_selection(select_game_mode_text)
        selected_game_mode_path = selected_language_path / selected_game_mode
        
        # 3. Build TypeGame instance and start game
        type_text = TypeGame(stdscr, selected_game_mode_path)

        # 3.1 Key listening function for game input
        @key_listener_decorator
        def game_input_listener(key):
            type_text.on_key_press(key)
        game_input_listener(type_text.print_game_text)

    curses.wrapper(pandatype_game) # Run the curses application

if __name__ == "__main__":
    main()
