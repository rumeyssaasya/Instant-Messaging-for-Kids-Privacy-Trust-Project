import tkinter as tk
from tkinter import messagebox
import json
from loginScreen import open_login_screen

def open_register_screen(root):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text="Kullanıcı Adı").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Şifre").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    tk.Label(root, text="Kullanıcı Türü").pack()
    user_type = tk.StringVar(value="child")
    tk.Radiobutton(root, text="Çocuk", variable=user_type, value="child").pack()
    tk.Radiobutton(root, text="Ebeveyn", variable=user_type, value="parent").pack()

    def register():
        username = username_entry.get()
        password = password_entry.get()
        utype = user_type.get()

        if not username or not password:
            messagebox.showerror("Hata", "Tüm alanları doldurun.")
            return

        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

        for user in users:
            if user["username"] == username:
                messagebox.showerror("Hata", "Bu kullanıcı zaten var.")
                return

        users.append({"username": username, "password": password, "type": utype})
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)

        messagebox.showinfo("Başarılı", "Kayıt tamamlandı!")
        open_login_screen(root)

    tk.Button(root, text="Kayıt Ol", command=register).pack(pady=5)
    tk.Button(root, text="Geri", command=lambda: open_login_screen(root)).pack()

