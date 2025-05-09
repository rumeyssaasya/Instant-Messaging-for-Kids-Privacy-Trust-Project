import tkinter as tk
from tkinter import messagebox
import json
from loginScreen import open_login_screen

def open_register_screen(root):
    # Kayıt ekranını oluşturuyoruz
    for widget in root.winfo_children():
        widget.destroy()  # Ana ekrandan mevcut widget'ları kaldırıyoruz
    root.geometry("250x300")
    tk.Label(root, text="Kullanıcı Adı").pack(pady=10)
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Şifre").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=10)
    
    tk.Label(root, text="Yaş").pack()
    age_entry = tk.Entry(root)
    age_entry.pack()


    tk.Label(root, text="Kullanıcı Türü").pack()
    age = age_entry.get()

    age = int(age)
    utype = "child" if age < 18 else "parent" 

    def register():
        username = username_entry.get()
        password = password_entry.get()
        utype = user_type.get()
        
        if not age.isdigit():
            messagebox.showerror("Hata", "Yaş sayısal bir değer olmalı.")
            return

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
        open_login_screen(root)  # Kayıt başarılı olursa giriş ekranına geçiş

    # Kayıt Ol butonu
    tk.Button(root, text="Kayıt Ol", command=register).pack(pady=5)

    # Geri butonu
    def go_back():
        open_login_screen(root)  # Geri butonuyla login ekranına dönme

    tk.Button(root, text="Giriş Yap", command=go_back).pack(pady=5)
