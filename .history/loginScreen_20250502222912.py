import tkinter as tk
from tkinter import messagebox
import json
from registerScreen import open_register_screen
from dashboard import open_dashboard

def open_login_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Kullanıcı Adı").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Şifre").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def login():
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

        username = username_entry.get()
        password = password_entry.get()

        for user in users:
            if user["username"] == username and user["password"] == password:
                messagebox.showinfo("Başarılı", "Giriş başarılı!")
                open_dashboard(root, user)  # Dashboard ekranına geç
                return

        messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı.")

    tk.Button(root, text="Giriş Yap", command=login).pack(pady=5)
    tk.Button(root, text="Kayıt Ol", command=lambda: open_register_screen(root)).pack()
