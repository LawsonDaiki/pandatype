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

    class TypeText:
        def __init__(self, stdscr, text):
            self.stdscr = stdscr
            self.text = text
            self.text_index = 0

        def check_key(self, key):
            """
            Check if the pressed key is correct
            """
            if self.text[self.text_index] == chr(key):
                return True
            return False
        
        def print_text(self, key=None):
            if key and self.check_key(key):
                self.text_index +=1
            self.stdscr.addstr(f"{self.text[:self.text_index]}", curses.color_pair(2))
            self.stdscr.addstr(f"{self.text[self.text_index:]}\n")
            return

    def key_listener(stdscr):
        stdscr.nodelay(True)  # Make getch() non-blocking

        def print_quit_message():
            stdscr.clear()
            stdscr.addstr("(Press 'ESC' to quit)...\n")
            return

        print_quit_message()

        text = "The quick brown fox jumps over the lazy dog."

        type_text = TypeText(stdscr, text)
        type_text.print_text()
        
        while True:
            key = stdscr.getch()
            if key != -1:  # If a key is pressed
                print_quit_message()
                type_text.print_text(key)
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