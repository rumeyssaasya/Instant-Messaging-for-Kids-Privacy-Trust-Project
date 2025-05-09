import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from datetime import datetime
import hashlib
import re

class SafeKidMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("SafeKid Messenger")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f8ff')
        
        # Database setup
        self.conn = sqlite3.connect('kid_messenger.db')
        self.c = self.conn.cursor()
        self.setup_database()
        
        # User session
        self.current_user = None
        self.is_parent = False
        
        # UI components
        self.chat_text = None
        self.contacts_listbox = None
        self.message_entry = None
        
        # Initialize UI
        self.show_login_screen()
    
    def setup_database(self):
        """Initialize database tables with proper schema"""
        tables = {
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_parent INTEGER NOT NULL DEFAULT 0,
                    parent_id INTEGER,
                    FOREIGN KEY(parent_id) REFERENCES users(id)
                )''',
            'contacts': '''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    contact_id INTEGER NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(contact_id) REFERENCES users(id),
                    UNIQUE(user_id, contact_id)
                )''',
            'messages': '''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    approved INTEGER NOT NULL DEFAULT 0,
                    visible_to_child INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY(sender_id) REFERENCES users(id),
                    FOREIGN KEY(receiver_id) REFERENCES users(id)
                )'''
        }
        
        for table, schema in tables.items():
            self.c.execute(schema)
        
        # Add any missing columns
        self.c.execute("PRAGMA table_info(messages)")
        columns = [col[1] for col in self.c.fetchall()]
        if 'visible_to_child' not in columns:
            self.c.execute("ALTER TABLE messages ADD COLUMN visible_to_child INTEGER DEFAULT 1")
        
        self.conn.commit()
    
    # ========== AUTHENTICATION METHODS ==========
    
    def show_login_screen(self):
        """Display the login/registration screen"""
        self.clear_window()
        
        tk.Label(self.root, text="SafeKid Messenger", font=('Arial', 24), bg='#f0f8ff').pack(pady=20)
        
        # Username field
        tk.Label(self.root, text="Username:", bg='#f0f8ff').pack()
        self.username_entry = tk.Entry(self.root, width=30)
        self.username_entry.pack()
        
        # Password field
        tk.Label(self.root, text="Password:", bg='#f0f8ff').pack()
        self.password_entry = tk.Entry(self.root, width=30, show="*")
        self.password_entry.pack()
        
        # Buttons
        tk.Button(self.root, text="Login", command=self.login, bg='#add8e6').pack(pady=10)
        tk.Button(self.root, text="Register", command=self.register, bg='#98fb98').pack(pady=5)
    
    def login(self):
        """Handle user login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        hashed_password = self.hash_password(password)
        
        self.c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = self.c.fetchone()
        
        if user:
            self.current_user = user
            self.is_parent = bool(user[3])
            self.show_main_interface()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    
    def register(self):
        """Handle new user registration"""
        username = simpledialog.askstring("Register", "Enter username:")
        if not username:
            return
        
        if not re.match("^[a-zA-Z0-9_]+$", username):
            messagebox.showerror("Error", "Username can only contain letters, numbers and underscores")
            return
        
        password = simpledialog.askstring("Register", "Enter password:", show='*')
        if not password:
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        is_parent = messagebox.askyesno("Register", "Is this a parent account?")
        
        parent_id = None
        if not is_parent:
            parent_username = simpledialog.askstring("Register", "Enter parent's username:")
            if parent_username:
                self.c.execute("SELECT id FROM users WHERE username=? AND is_parent=1", (parent_username,))
                parent = self.c.fetchone()
                if parent:
                    parent_id = parent[0]
                else:
                    messagebox.showerror("Error", "Parent username not found")
                    return
        
        try:
            hashed_password = self.hash_password(password)
            self.c.execute(
                "INSERT INTO users (username, password, is_parent, parent_id) VALUES (?, ?, ?, ?)",
                (username, hashed_password, int(is_parent), parent_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
    
    def hash_password(self, password):
        """Hash password for secure storage"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ========== MAIN INTERFACE METHODS ==========
    
    def show_main_interface(self):
        """Display the main messaging interface"""
        self.clear_window()
        
        # Header with user info and controls
        header_frame = tk.Frame(self.root, bg='#4682b4')
        header_frame.pack(fill='x')
        
        tk.Label(header_frame, text=f"Welcome, {self.current_user[1]}!", 
                font=('Arial', 16), bg='#4682b4', fg='white').pack(side='left', padx=10)
        
        if not self.is_parent:
            tk.Button(header_frame, text="Add Friend", command=self.add_friend, bg='#add8e6').pack(side='right', padx=5)
        
        tk.Button(header_frame, text="Logout", command=self.show_login_screen, bg='#ff9999').pack(side='right', padx=5)
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#f0f8ff')
        main_frame.pack(fill='both', expand=True)
        
        # Contacts list (left sidebar)
        contacts_frame = tk.Frame(main_frame, width=200, bg='#e6f2ff')
        contacts_frame.pack(side='left', fill='y')
        
        tk.Label(contacts_frame, text="Contacts", font=('Arial', 12), bg='#e6f2ff').pack(pady=5)
        
        self.contacts_listbox = tk.Listbox(contacts_frame, width=25)
        self.contacts_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.load_conversation)
        
        self.load_contacts()
        
        # Chat area (right side)
        chat_frame = tk.Frame(main_frame, bg='#ffffff')
        chat_frame.pack(side='right', fill='both', expand=True)
        
        self.chat_text = tk.Text(chat_frame, state='disabled', wrap='word')
        self.chat_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.chat_text.tag_config("rejected", foreground="red", background="#ffeeee")
        
        # Message input area
        message_frame = tk.Frame(chat_frame, bg='#ffffff')
        message_frame.pack(fill='x', padx=5, pady=5)
        
        self.message_entry = tk.Entry(message_frame, width=50)
        self.message_entry.pack(side='left', fill='x', expand=True)
        self.message_entry.bind('<Return>', self.send_message)
        
        send_button = tk.Button(message_frame, text="Send", command=self.send_message, bg='#add8e6')
        send_button.pack(side='right', padx=5)
        
        # Parent controls if applicable
        if self.is_parent:
            self.setup_parent_controls()
    
    def setup_parent_controls(self):
        """Add parent-specific controls to the interface"""
        control_frame = tk.Frame(self.root, bg='#f0f8ff')
        control_frame.pack(fill='x')
        
        tk.Button(control_frame, text="Approve Contacts", command=self.show_pending_contacts, 
                bg='#98fb98').pack(side='left', padx=5)
        tk.Button(control_frame, text="Review Messages", command=self.show_pending_messages, 
                bg='#98fb98').pack(side='left', padx=5)
        tk.Button(control_frame, text="Add Child Account", command=self.add_child_account, 
                bg='#98fb98').pack(side='left', padx=5)
    
    def clear_window(self):
        """Clear all widgets from the main window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ========== CONTACT MANAGEMENT ==========
    
    def load_contacts(self):
        """Load the user's contact list"""
        self.contacts_listbox.delete(0, tk.END)
        
        if self.is_parent:
            # Parents see their children
            self.c.execute("""SELECT id, username FROM users 
                            WHERE parent_id=?""", (self.current_user[0],))
            for child in self.c.fetchall():
                self.contacts_listbox.insert(tk.END, f"👶 {child[1]}")
        else:
            # Children see approved contacts
            self.c.execute("""SELECT u.id, u.username FROM contacts c
                            JOIN users u ON c.contact_id = u.id
                            WHERE c.user_id=? AND c.approved=1""", (self.current_user[0],))
            for contact in self.c.fetchall():
                self.contacts_listbox.insert(tk.END, contact[1])
    
    def add_friend(self):
        """Initiate adding a new friend/contact"""
        friend_username = simpledialog.askstring("Add Friend", "Enter friend's username:")
        if not friend_username:
            return
            
        self.c.execute("SELECT id FROM users WHERE username=?", (friend_username,))
        friend = self.c.fetchone()
        
        if not friend:
            messagebox.showerror("Error", "User not found")
            return
            
        friend_id = friend[0]
        
        # Check if already a contact
        self.c.execute("""SELECT 1 FROM contacts 
                        WHERE user_id=? AND contact_id=?""", (self.current_user[0], friend_id))
        if self.c.fetchone():
            messagebox.showerror("Error", "Already a contact")
            return
            
        # Add to contacts (pending approval)
        try:
            self.c.execute("""INSERT INTO contacts (user_id, contact_id, approved)
                          VALUES (?, ?, ?)""", (self.current_user[0], friend_id, 0))
            self.conn.commit()
            messagebox.showinfo("Success", "Friend request sent for parental approval")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Contact request already exists")
        
        self.load_contacts()
    
    def show_pending_contacts(self):
        """Display pending contact requests for parent approval"""
        self.c.execute("""SELECT c.id, u1.username, u2.username 
                       FROM contacts c
                       JOIN users u1 ON c.user_id = u1.id
                       JOIN users u2 ON c.contact_id = u2.id
                       WHERE u1.parent_id=? AND c.approved=0""", (self.current_user[0],))
        pending_contacts = self.c.fetchall()
        
        if not pending_contacts:
            messagebox.showinfo("Info", "No pending contact requests")
            return
            
        # Create approval window
        approve_window = tk.Toplevel(self.root)
        approve_window.title("Approve Contacts")
        
        tk.Label(approve_window, text="Pending Contact Requests", font=('Arial', 12)).pack(pady=5)
        
        for contact in pending_contacts:
            contact_id, child_username, friend_username = contact
            frame = tk.Frame(approve_window)
            frame.pack(fill='x', padx=5, pady=2)
            
            tk.Label(frame, text=f"{child_username} wants to chat with {friend_username}").pack(side='left')
            
            btn_frame = tk.Frame(frame)
            btn_frame.pack(side='right')
            
            tk.Button(btn_frame, text="Approve", 
                     command=lambda cid=contact_id: self.process_contact_request(cid, 1, approve_window),
                     bg='#98fb98').pack(side='left', padx=2)
            tk.Button(btn_frame, text="Reject", 
                     command=lambda cid=contact_id: self.process_contact_request(cid, 0, approve_window),
                     bg='#ff9999').pack(side='left', padx=2)
    
    def process_contact_request(self, contact_id, approved, window):
        """Process a contact approval or rejection"""
        self.c.execute("UPDATE contacts SET approved=? WHERE id=?", (approved, contact_id))
        self.conn.commit()
        
        # Close the current window
        window.destroy()
        
        messagebox.showinfo("Success", "Contact request processed")
        
        # Reopen if there are more pending requests
        self.c.execute("""SELECT COUNT(*) FROM contacts c
                       JOIN users u ON c.user_id = u.id
                       WHERE u.parent_id=? AND c.approved=0""", (self.current_user[0],))
        if self.c.fetchone()[0] > 0:
            self.show_pending_contacts()
    
    # ========== MESSAGE MANAGEMENT ==========
    
    def load_conversation(self, event=None):
        """Load messages for the selected contact"""
        self.chat_text.config(state='normal')
        self.chat_text.delete('1.0', tk.END)
        
        selection = self.contacts_listbox.curselection()
        if not selection:
            return
            
        selected_contact = self.contacts_listbox.get(selection[0])
        
        try:
            if selected_contact.startswith("👶"):
                # Parent viewing child's messages
                child_username = selected_contact[2:].strip()
                self.c.execute("SELECT id FROM users WHERE username=?", (child_username,))
                child_id = self.c.fetchone()[0]
                
                query = """SELECT u.username, m.message, m.timestamp, m.approved 
                        FROM messages m
                        JOIN users u ON m.sender_id = u.id
                        WHERE (m.sender_id=? OR m.receiver_id=?)
                        AND (m.visible_to_child=1 OR ?=1)
                        ORDER BY m.timestamp"""
                params = (child_id, child_id, int(self.is_parent))
            else:
                # Regular conversation
                self.c.execute("SELECT id FROM users WHERE username=?", (selected_contact,))
                contact_id = self.c.fetchone()[0]
                
                query = """SELECT u.username, m.message, m.timestamp, m.approved 
                        FROM messages m
                        JOIN users u ON m.sender_id = u.id
                        WHERE ((m.sender_id=? AND m.receiver_id=?)
                        OR (m.sender_id=? AND m.receiver_id=?))
                        AND (m.visible_to_child=1 OR ?=1)
                        ORDER BY m.timestamp"""
                params = (self.current_user[0], contact_id, contact_id, self.current_user[0], int(self.is_parent))
            
            self.c.execute(query, params)
            messages = self.c.fetchall()
            
            for message in messages:
                username, msg, timestamp, approved = message
                display_msg = f"{username} ({timestamp}): {msg}\n"
                
                if not approved:
                    display_msg = "[REJECTED] " + display_msg
                    self.chat_text.insert(tk.END, display_msg, "rejected")
                else:
                    self.chat_text.insert(tk.END, display_msg)
                    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            self.chat_text.config(state='disabled')
            self.chat_text.yview(tk.END)
    
    def send_message(self, event=None):
        """Send a new message"""
        if not self.is_parent and not self.check_contact_approved():
            messagebox.showerror("Error", "Contact not approved by parent")
            return
            
        message = self.message_entry.get()
        if not message:
            return
            
        selection = self.contacts_listbox.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a contact")
            return
            
        selected_contact = self.contacts_listbox.get(selection[0])
        
        # Get receiver ID
        if selected_contact.startswith("👶"):
            child_username = selected_contact[2:].strip()
            self.c.execute("SELECT id FROM users WHERE username=?", (child_username,))
            receiver_id = self.c.fetchone()[0]
        else:
            self.c.execute("SELECT id FROM users WHERE username=?", (selected_contact,))
            receiver_id = self.c.fetchone()[0]
        
        # Apply content filtering
        message = self.filter_message(message)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Auto-approve if sent by parent, otherwise require approval
        approved = 1 if self.is_parent else 0
        
        try:
            self.c.execute("""INSERT INTO messages 
                           (sender_id, receiver_id, message, timestamp, approved)
                           VALUES (?, ?, ?, ?, ?)""",
                           (self.current_user[0], receiver_id, message, timestamp, approved))
            self.conn.commit()
            
            self.message_entry.delete(0, tk.END)
            
            if not self.is_parent:
                messagebox.showinfo("Sent", "Message sent for parental approval")
            
            self.load_conversation()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")
    
    def filter_message(self, message):
        """Apply content filtering to messages"""
        bad_words = ["bad", "hate", "stupid"]  # Should be more comprehensive in production
        for word in bad_words:
            if word in message.lower():
                message = message.replace(word, "***")
                messagebox.showinfo("Filtered", "Some words were filtered out for safety")
                break
        return message
    
    def check_contact_approved(self):
        """Check if current contact is approved"""
        selection = self.contacts_listbox.curselection()
        if not selection:
            return False
            
        contact_name = self.contacts_listbox.get(selection[0])
        self.c.execute("""SELECT c.approved FROM contacts c
                        JOIN users u ON c.contact_id = u.id
                        WHERE u.username=? AND c.user_id=?""",
                        (contact_name, self.current_user[0]))
        result = self.c.fetchone()
        return result and result[0] == 1
    
    def show_pending_messages(self):
        """Display messages pending approval"""
        self.c.execute("""SELECT m.id, u1.username, u2.username, m.message, m.timestamp
                       FROM messages m
                       JOIN users u1 ON m.sender_id = u1.id
                       JOIN users u2 ON m.receiver_id = u2.id
                       WHERE (u1.parent_id=? OR u2.parent_id=?) AND m.approved=0""",
                       (self.current_user[0], self.current_user[0]))
        pending_messages = self.c.fetchall()
        
        if not pending_messages:
            messagebox.showinfo("Info", "No pending messages to review")
            return
            
        # Create review window
        review_window = tk.Toplevel(self.root)
        review_window.title("Review Messages")
        
        tk.Label(review_window, text="Pending Messages for Approval", font=('Arial', 12)).pack(pady=5)
        
        for msg in pending_messages:
            msg_id, sender, receiver, message, timestamp = msg
            frame = tk.Frame(review_window, borderwidth=1, relief='solid')
            frame.pack(fill='x', padx=5, pady=2)
            
            tk.Label(frame, text=f"ID: {msg_id} | From: {sender} | To: {receiver} | {timestamp}").pack(anchor='w')
            tk.Label(frame, text=message, wraplength=400, justify='left').pack(anchor='w')
            
            btn_frame = tk.Frame(frame)
            btn_frame.pack(fill='x')
            
            tk.Button(btn_frame, text="Approve", 
                     command=lambda mid=msg_id, w=review_window: self.process_message(mid, 1, w),
                     bg='#98fb98').pack(side='right', padx=2)
            tk.Button(btn_frame, text="Reject", 
                     command=lambda mid=msg_id, w=review_window: self.process_message(mid, 0, w),
                     bg='#ff9999').pack(side='right', padx=2)
    
    def process_message(self, message_id, approved, window):
        """Process message approval or rejection"""
        try:
            self.c.execute("UPDATE messages SET approved=? WHERE id=?", (approved, message_id))
            
            if not approved:
                self.c.execute("UPDATE messages SET visible_to_child=0 WHERE id=?", (message_id,))
            
            self.conn.commit()
            
            # Close the current window
            window.destroy()
            
            messagebox.showinfo("Success", "Message processed successfully")
            
            # Reopen if there are more pending messages
            self.c.execute("""SELECT COUNT(*) FROM messages m
                           JOIN users u1 ON m.sender_id = u1.id
                           JOIN users u2 ON m.receiver_id = u2.id
                           WHERE (u1.parent_id=? OR u2.parent_id=?) AND m.approved=0""",
                           (self.current_user[0], self.current_user[0]))
            if self.c.fetchone()[0] > 0:
                self.show_pending_messages()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to process message: {str(e)}")
    
    # ========== PARENT METHODS ==========
    
    def add_child_account(self):
        """Create a new child account"""
        child_username = simpledialog.askstring("Add Child", "Enter child's username:")
        if not child_username:
            return
            
        if not re.match("^[a-zA-Z0-9_]+$", child_username):
            messagebox.showerror("Error", "Username can only contain letters, numbers and underscores")
            return
            
        child_password = simpledialog.askstring("Add Child", "Enter child's password:", show='*')
        if not child_password:
            return
            
        if len(child_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
            
        try:
            hashed_password = self.hash_password(child_password)
            self.c.execute("""INSERT INTO users (username, password, is_parent, parent_id)
                          VALUES (?, ?, 0, ?)""",
                          (child_username, hashed_password, self.current_user[0]))
            self.conn.commit()
            messagebox.showinfo("Success", "Child account added successfully!")
            self.load_contacts()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")

if __name__ == "__main__":
    root = tk.Tk()
    app = SafeKidMessenger(root)
    root.mainloop()