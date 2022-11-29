import curses
from curses import wrapper
from interface.console import Pad, clear_line, edit, exit_console, init_console, redraw, report, wait_for_key
from parser.input_parser import parse_hypothesis
from parsimonious import exceptions

def get_text(main_window, win3):
    string = ""
    index = 0 # index in current string to start editing
    while True:
        clear_line(win3, 0)
        string = edit(win3, string, index) # get characters from edit window
        # main_window.refresh()
        try:
            ast = parse_hypothesis.parse(string) # parse input
            break
        except exceptions.IncompleteParseError as inst:
            index = inst.args[1]
            report(win3, "Extra characters on line, starting at column "+str(index + 1)+". Press ENTER to continue")
            wait_for_key("\n")
        except exceptions.ParseError as inst:
            index = inst.pos
            report(win3, "Error in statement starting at column "+str(index + 1)+". Press ENTER to continue")
            wait_for_key("\n")
    return string, ast

def main(stdscr):
    win1, win2, win3 = init_console()
    pad1 = Pad() # data that is in the windows (test + AST)
    pad2 = Pad()
    main_window = win1 # which window has focus
    main_pad = pad1

    while True:
        c = stdscr.getkey()
        if c == '\t': # TAB = switch window focus (and associated pad)
            main_window = win2 if main_window == win1 else win1
            main_pad = pad2 if main_pad == pad1 else pad1
            main_window.refresh() # tell curses to update display (moves the cursor)
        elif c == 'q': # q = quit
            break
        elif c == 'e': # e = edit
            main_pad[main_pad.line] = get_text(main_window, win3) # get text from user and parse
            main_pad.adjust() # line might now be shorter, so adjust window it is being inserted in
            redraw(main_window, main_pad) # redraw the window
            main_window.refresh() # tell curses it can now update display
        elif c == 'KEY_DOWN':
            if main_pad.line < main_pad.len(): # if we are not on the last line of data
                height, width = main_window.getmaxyx()
                if main_pad.cursor_line < height - 3: # if the cursor is not at the bottom of window
                    main_pad.cursor_line += 1
                main_pad.line += 1 # move down one in the data
                main_pad.adjust() # new cursor line might be shorter, so adjust window
                redraw(main_window, main_pad) # redraw the window
                main_window.refresh() # tell curses it can now update display
        elif c == 'KEY_UP':
            if main_pad.line > 0: # if we are not on the first line of data
                if main_pad.cursor_line > 0: # if the cursor is not on first line of window
                    main_pad.cursor_line -= 1
                main_pad.line -= 1 # move up one line in the data
                main_pad.adjust() # new cursor line might be shorter, so adjust window
                redraw(main_window, main_pad) # redraw the window
                main_window.refresh() # tell curses it can now update display
        else:
            continue

    exit_console()

wrapper(main) # curses wrapper handles exceptions
