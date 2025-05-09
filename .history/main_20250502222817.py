from tkinter import Tk
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from login_screen import open_login_screen

if __name__ == "__main__":
    root = Tk()
    root.title("SafeChat Kids - Giriş")
    root.geometry("300x200")
    open_login_screen(root)
    root.mainloop()
