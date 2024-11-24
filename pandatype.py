import curses

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
            self.text = text
            self.user_text = ''
        
        def print_text(self):
            for text_idx, letter_text in enumerate(self.text):
                if text_idx == len(self.user_text):
                    self.stdscr.addstr(f"{self.text[text_idx:]}")
                    break
                elif letter_text == self.user_text[text_idx]:
                    self.stdscr.addstr(f"{letter_text}", curses.color_pair(2))
                else:
                    self.stdscr.addstr(f"{letter_text}", curses.color_pair(1))
            self.stdscr.addstr("\n")
            return
        
        def on_key_press(self, key):
            if key == 127:
                self.user_text = self.user_text[:-1]
            else:
                self.user_text += chr(key)
            self.print_text()

    def key_listener(stdscr):
        stdscr.nodelay(True)  # Make getch() non-blocking

        def print_quit_message():
            stdscr.clear()
            stdscr.addstr("(Press 'ESC' to quit)...\n")
            return

        print_quit_message()

        type_text = TypeText(stdscr, text)
        type_text.print_text()
        
        while True:
            key = stdscr.getch()
            if key != -1:  # If a key is pressed
                print_quit_message()
                type_text.on_key_press(key)
                stdscr.addstr(f"Key pressed: {key} ('{chr(key)}')\n")
                stdscr.refresh()
                if key == 27:  # Exit on 'ESC'
                    break

    curses.wrapper(key_listener) # Run the curses application

if __name__ == "__main__":
    # Entry point of the script
    print("Script is being run directly.")
    main()
else:
    print("Script is being imported as a module.")