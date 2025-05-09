import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime
import hashlib
import re

class KidMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("SafeKid Messenger")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f8ff')
        
        # Database setup
        self.conn = sqlite3.connect('kid_messenger.db')
        self.c = self.conn.cursor()
        self.create_tables()
        
        # User session
        self.current_user = None
        self.is_parent = False
        
        # Initialize chat_text attribute
        self.chat_text = None
        
        # UI Setup
        self.setup_login_ui()

        # Update database
        self.update_database_schema()
        
    # ... [keep all other methods exactly the same until setup_main_ui] ...

    def setup_main_ui(self):
        self.clear_window()
        
        # Header
        header_frame = tk.Frame(self.root, bg='#4682b4')
        header_frame.pack(fill='x')
        
        tk.Label(header_frame, text=f"Welcome, {self.current_user[1]}!", 
                 font=('Arial', 16), bg='#4682b4', fg='white').pack(side='left', padx=10)
        
        if not self.is_parent:
            tk.Button(header_frame, text="Add Friend", command=self.add_friend, bg='#add8e6').pack(side='right', padx=5)
        
        tk.Button(header_frame, text="Logout", command=self.setup_login_ui, bg='#ff9999').pack(side='right', padx=5)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill='both', expand=True)
        
        # Contacts list
        contacts_frame = tk.Frame(main_frame, width=200, bg='#e6f2ff')
        contacts_frame.pack(side='left', fill='y')
        
        tk.Label(contacts_frame, text="Contacts", font=('Arial', 12), bg='#e6f2ff').pack(pady=5)
        
        self.contacts_listbox = tk.Listbox(contacts_frame, width=25)
        self.contacts_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.load_messages)
        
        self.load_contacts()
        
        # Chat area
        chat_frame = tk.Frame(main_frame, bg='#ffffff')
        chat_frame.pack(side='right', fill='both', expand=True)
        
        self.chat_text = tk.Text(chat_frame, state='disabled', wrap='word')
        self.chat_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configure tags AFTER creating the widget
        self.chat_text.tag_config("rejected", foreground="red", background="#ffeeee")
        
        # ... [rest of the setup_main_ui method and all other methods remain unchanged] ...

if __name__ == "__main__":
    root = tk.Tk()
    app = KidMessenger(root)
    root.mainloop()