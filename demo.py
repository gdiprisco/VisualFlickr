from modules.user_interface import start_interface


def start_test():
    import os
    os.environ["TERM"] = "xterm"
    from simple_term_menu import TerminalMenu
    print(TerminalMenu(["AMERICA", "EUROPA"]).show())


if __name__ == "__main__":
    start_interface()

# ver. 0.8beta

