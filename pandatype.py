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

def idx_exists_in_list(list, idx):
    try:
        list[idx]
        return True
    except IndexError:
        return False

def convert_key_to_int(key):
    try:
        return int(chr(key))  # Try converting to integer
    except ValueError:
        return

class TypeGame():
    def __init__(self, stdscr, words_file_path):
        self.stdscr = stdscr
        self.start_time = None
        self.run_time = None
        self.words_file_path = words_file_path
        self.game_mode = words_file_path.as_posix().split('/')[-1]
        self.phrase = []
        self.word_count_in_phrase = 0
        self.correct_words_count = 0
        self.acc = 0
        self.progress = ''
        self.wpm = 0
        self.is_game_over = False
        self.build_phrase()
        self.cursor_word_idx = 0
        self.cursor_char_idx = 0
        self.input_char_status = []

    def print_text(self, string):
        self.stdscr.addstr(string, curses.A_DIM)

    def print_text_bold(self, string):
        self.stdscr.addstr(string, curses.A_DIM | curses.A_BOLD)
    
    def print_text_bold_ul(self, string):
        self.stdscr.addstr(string, curses.A_DIM | curses.A_BOLD | curses.A_UNDERLINE)
    
    def print_correctly_typed_char(self, string):
        self.stdscr.addstr(string, curses.A_BOLD)
    
    def print_incorrectly_typed_char(self, string):
        self.stdscr.addstr(string, curses.color_pair(1) | curses.A_BOLD)
    
    def print_game_over(self, string):
        self.stdscr.addstr(string, curses.color_pair(5) | curses.A_BOLD)
    
    def build_phrase(self):
        with self.words_file_path.open(mode='r') as file:
            csv_reader = csv.reader(file, delimiter='|')
            if self.words_file_path.as_posix().endswith('quotes.csv'):
                listed_words = list(csv_reader)
                random.shuffle(listed_words)
                self.phrase = listed_words[0][0].split()
            else:
                words_sample = random.sample(list(csv_reader), 40)
                self.phrase = [x[0] for x in words_sample]
            self.word_count_in_phrase = len(self.phrase)

    def reset_game(self):
        self.start_time = None
        self.input_char_status = []
        self.cursor_word_idx = 0
        self.cursor_char_idx = 0
        self.run_time = None
        self.is_game_over = False
        self.build_phrase()
        self.is_current_word_correct = False
        self.correct_words_count = 0
        self.update_metrics()

    
    def elapsed_time(self):
        if self.run_time:
            return self.run_time
        return time.time() - self.start_time if self.start_time else 0.0
    
    def print_footer_message(self):
        # print game metrics
        if self.is_game_over:
            self.print_game_over(f"\n progress {self.progress} \n time: {self.elapsed_time():.2f} seconds \n wpm: {self.wpm:.0f} \n acc: {self.acc:.0f} % \n\n GAME OVER \n")
        else:
            self.print_text(f"\n progress {self.progress}\n time: {self.elapsed_time():.2f} seconds\n wpm: {self.wpm:.0f}\n acc: {self.acc:.0f} %\n\n")

        # print quit and reset game messages
        self.print_text("(Press 'Tab' to reset)...\n")

    def print_game_phrase(self):
        for input_char_status, input_char in self.input_char_status:
            if input_char_status == 'correct':
                self.print_correctly_typed_char(input_char)
            elif input_char_status == 'incorrect':
                self.print_incorrectly_typed_char(input_char)
            elif input_char_status == 'not_typed':
                self.print_text_bold(input_char)
            elif input_char_status == 'incorrect_extra_char':
                self.print_incorrectly_typed_char(input_char)
            elif input_char_status == 'space':
                self.print_text_bold(' ')

        # print remainder characters from the current word
        cursor_in_space_char = True
        if idx_exists_in_list(self.phrase, self.cursor_word_idx):
            for relative_idx, remainder_char in enumerate(self.phrase[self.cursor_word_idx][self.cursor_char_idx:]):
                if relative_idx == 0:
                    self.print_text_bold_ul(remainder_char)
                    cursor_in_space_char = False
                else:
                    self.print_text_bold(remainder_char)

        # print space before remainder words
        if cursor_in_space_char:
            self.print_text_bold_ul(' ')
        else:
            self.print_text_bold(' ')

        # print remainder words all at once
        self.print_text_bold(' '.join(self.phrase[self.cursor_word_idx+1:]))
        return

    def store_char_status(self, char):
        if idx_exists_in_list(self.phrase, self.cursor_word_idx):
            if idx_exists_in_list(self.phrase[self.cursor_word_idx], self.cursor_char_idx):
                if char == self.phrase[self.cursor_word_idx][self.cursor_char_idx]:
                    self.input_char_status.append(('correct', char))
                else:
                    self.input_char_status.append(('incorrect', self.phrase[self.cursor_word_idx][self.cursor_char_idx]))
            else:
                self.input_char_status.append(('incorrect_extra_char', char))

    def check_remaining_chars_in_word(self):
        if self.cursor_char_idx + 1 <= len(self.phrase[self.cursor_word_idx]):
            for not_typed_char in self.phrase[self.cursor_word_idx][self.cursor_char_idx:]:
                self.input_char_status.append(('not_typed', not_typed_char))

    def check_if_input_word_is_correct(self):
        for char_status, char in reversed(self.input_char_status):
            if char_status == 'space':
                self.correct_words_count += 1
                return
            if char_status != 'correct':
                return
        self.correct_words_count += 1
        return

    def update_metrics(self):
        # get accuracy
        self.acc = 0 if self.cursor_word_idx == 0 else self.correct_words_count/self.cursor_word_idx*100
        
        # get progress
        self.progress = f"{self.cursor_word_idx}/{self.word_count_in_phrase}"
        
        # get wpm
        self.wpm = 0 if self.elapsed_time() == 0 else self.correct_words_count/self.elapsed_time()*60

    def print_game_text(self):
        self.print_text(f" game mode: {self.game_mode}\n\n") # subtitle
        self.print_game_phrase()
        self.print_footer_message()
    
    def on_key_press(self, key):
        # self.stdscr.addstr(f"\nKey pressed: {key} ('{chr(key)}')\n")
        if key == 9: # on key 'Tab' reset game
            self.reset_game()
        elif not self.is_game_over:
            if key == 32: # on key "Space" jump to the next word.
                if self.cursor_char_idx != 0: # If the user try to press space key in sequence, the game will catch only the first press
                    if self.cursor_word_idx+1 == len(self.phrase): # handle game over
                        self.is_game_over = True
                        self.run_time = time.time() - self.start_time
                    self.check_remaining_chars_in_word()
                    self.check_if_input_word_is_correct()
                    self.input_char_status.append(('space', ' '))
                    self.cursor_word_idx += 1
                    self.cursor_char_idx = 0
                    self.update_metrics()
            elif key == 127: # on key "Delete" erase last inputted character. Don't allow user to delete the previous word
                if self.cursor_char_idx != 0:
                    self.input_char_status.pop()
                    self.cursor_char_idx -= 1
            else: # on a normal key press, store character by appending it to last item
                if self.cursor_word_idx == 0 and self.cursor_char_idx == 0: # this is case when is the user's first input of the game the start_time must be saved
                    self.start_time = time.time()
                self.store_char_status(chr(key))
                self.cursor_char_idx += 1

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
                    stdscr.addstr("(Press 'Esc' to quit)...\n\n", curses.A_DIM)
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

        @key_listener_decorator
        def game_input_listener(key):
            type_text.on_key_press(key)
        game_input_listener(type_text.print_game_text)

    curses.wrapper(pandatype_game) # Run the curses application

if __name__ == "__main__":
    main()
