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
        self.conn = sqlite3.connect('kid_messenger.db', check_same_thread=False)
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
                    is_visible INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(sender_id) REFERENCES users(id),
                    FOREIGN KEY(receiver_id) REFERENCES users(id)
                )'''
        }
        
        for table, schema in tables.items():
            self.c.execute(schema)
        
        self.conn.commit()
    
    # [Previous methods remain the same until send_message]

    def send_message(self, event=None):
        """Send a new message with proper approval handling"""
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
        
        # Set initial visibility based on sender
        is_visible = 1 if self.is_parent else 0  # Only visible immediately if sent by parent
        
        try:
            self.c.execute("""INSERT INTO messages 
                           (sender_id, receiver_id, message, timestamp, approved, is_visible)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                           (self.current_user[0], receiver_id, message, timestamp, is_visible, is_visible))
            self.conn.commit()
            
            self.message_entry.delete(0, tk.END)
            
            if not self.is_parent:
                messagebox.showinfo("Sent", "Message sent for parental approval")
                # Notify parent if online
                self.notify_parent()
            
            self.load_conversation()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

    def process_message(self, message_id, approved, window):
        """Process message approval or rejection with proper visibility control"""
        try:
            # Update both approval and visibility status together
            self.c.execute("UPDATE messages SET approved=?, is_visible=? WHERE id=?", 
                         (approved, approved, message_id))
            self.conn.commit()
            
            # Close the review window
            window.destroy()
            
            messagebox.showinfo("Success", "Message processed successfully")
            
            # Refresh conversation if viewing affected chat
            self.load_conversation()
            
            # Reopen review window if more pending messages exist
            if self.has_pending_messages():
                self.show_pending_messages()
                
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to process message: {str(e)}")
            self.conn.rollback()

    def load_conversation(self, event=None):
        """Load only approved and visible messages for the conversation"""
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
                
                query = """SELECT u.username, m.message, m.timestamp 
                        FROM messages m
                        JOIN users u ON m.sender_id = u.id
                        WHERE (m.sender_id=? OR m.receiver_id=?)
                        AND m.is_visible=1
                        ORDER BY m.timestamp"""
                params = (child_id, child_id)
            else:
                # Regular conversation
                self.c.execute("SELECT id FROM users WHERE username=?", (selected_contact,))
                contact_id = self.c.fetchone()[0]
                
                query = """SELECT u.username, m.message, m.timestamp 
                        FROM messages m
                        JOIN users u ON m.sender_id = u.id
                        WHERE ((m.sender_id=? AND m.receiver_id=?)
                        OR (m.sender_id=? AND m.receiver_id=?))
                        AND m.is_visible=1
                        ORDER BY m.timestamp"""
                params = (self.current_user[0], contact_id, contact_id, self.current_user[0])
            
            self.c.execute(query, params)
            messages = self.c.fetchall()
            
            for message in messages:
                username, msg, timestamp = message
                display_msg = f"{username} ({timestamp}): {msg}\n"
                self.chat_text.insert(tk.END, display_msg)
                    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            self.chat_text.config(state='disabled')
            self.chat_text.yview(tk.END)

    def notify_parent(self):
        """Notify parent that a new message needs approval"""
        if not self.is_parent:
            self.c.execute("SELECT id FROM users WHERE parent_id=?", (self.current_user[0],))
            parent = self.c.fetchone()
            if parent:
                # In a real app, this would trigger a notification
                pass

    # [Rest of the methods remain the same]

if __name__ == "__main__":
    root = tk.Tk()
    app = SafeKidMessenger(root)
    root.mainloop()