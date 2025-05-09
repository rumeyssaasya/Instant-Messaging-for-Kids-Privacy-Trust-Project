from tkinter import Tk
from loginScreen import open_login_screen

if __name__ == "__main__":
    root = Tk()
    root.title("SafeChat Kids - Giriş")
    root.geometry("300x200")
    open_login_screen(root)
    root.mainloop()
