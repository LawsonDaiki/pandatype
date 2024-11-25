import curses
import time

def main():
    """
    Main function to execute the core logic of the script.
    """
    curses.initscr()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)   # Red text, black background
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # Green text, black background
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE)  # Blue text, white background

    text = "The quick brown fox jumps over the lazy dog."

    class TypeText:
        def __init__(self, stdscr, text):
            self.stdscr = stdscr
            self.start_time = None
            self.run_time = None
            self.text = text
            self.user_text = ''

        def current_idx(self):
            return len(self.user_text)
        
        def start_stopwatch(self):
            if self.current_idx() == 0:
                self.start_time = time.time()

        def elapsed_time(self):
            if self.has_ended():
                if not self.run_time:
                    self.run_time = time.time() - self.start_time
                return self.run_time
            return time.time() - self.start_time
        
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
            for text_idx, letter_text in enumerate(self.text):
                if text_idx == self.current_idx(): # print the white characters
                    self.stdscr.addstr(f"{self.text[text_idx:]}")
                    break
                elif letter_text == self.user_text[text_idx]: # print the green characters
                    self.stdscr.addstr(f"{letter_text}", curses.color_pair(2))
                else: # print the red characters
                    self.stdscr.addstr(f"{letter_text}", curses.color_pair(1))
            self.stdscr.addstr("\n")
        
        def has_ended(self):
            return self.current_idx() >= len(self.text)
        
        def reset(self):
            self.user_text = ''
            self.start_time = time.time() # It is like this (and not None) because print_footer_message() will need self.start_time to call self.elapsed_time() to print 0.00 seconds
            self.run_time = None
        
        def on_key_press(self, key):
            if key == 127: # on key 'Delete' erase the last input
                self.user_text = self.user_text[:-1]
            elif key == 9: # on key 'Tab' reset game
                self.reset()
            else:
                self.start_stopwatch()
                self.user_text += chr(key)
            
            self.print_header_message()
            self.print_text()
            self.print_footer_message()

            self.stdscr.addstr(f"\nKey pressed: {key} ('{chr(key)}')\n")

            if self.has_ended():
                self.stdscr.addstr("\nGAME OVER\n", curses.color_pair(1))

    def key_listener(stdscr):
        stdscr.nodelay(True)  # Make getch() non-blocking


        type_text = TypeText(stdscr, text)
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
    main()