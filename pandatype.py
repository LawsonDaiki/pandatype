import curses

def print_quit_message(stdscr):
    stdscr.clear()
    stdscr.addstr("Press any key (Press 'ESC' to quit)...\n")
    return

def main():
    """
    Main function to execute the core logic of the script.
    """

    def key_listener(stdscr):
        stdscr.nodelay(True)  # Make getch non-blocking
        print_quit_message(stdscr)
        
        while True:
            key = stdscr.getch()
            if key != -1:  # If a key is pressed
                print_quit_message(stdscr)
                stdscr.addstr(f"Key pressed: {key} ('{chr(key)}')\n")
                stdscr.refresh()
                if key == 27:  # Exit on 'q'
                    break

    # Run the curses application
    curses.wrapper(key_listener)

if __name__ == "__main__":
    # Entry point of the script
    print("Script is being run directly.")
    main()
else:
    print("Script is being imported as a module.")