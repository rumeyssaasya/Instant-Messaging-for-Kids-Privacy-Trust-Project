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

    def register():
        username = username_entry.get()
        password = password_entry.get()
        age_text = age_entry.get()  # Yaş önce string olarak alınır

        if not username or not password or not age_text:
            messagebox.showerror("Hata", "Tüm alanları doldurun.")
            return

        if not age_text.isdigit():  # Sayı mı diye kontrol
            messagebox.showerror("Hata", "Yaş sayısal bir değer olmalı.")
            return

        age = int(age_text)  # Şimdi güvenle sayı yapabiliriz

        # Yaşa göre çocuk mu ebeveyn mi karar ver
        utype = "child" if age < 18 else "parent"

        # Kullanıcı kaydını yap
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

        for user in users:
            if user["username"] == username:
                messagebox.showerror("Hata", "Bu kullanıcı zaten var.")
                return

        users.append({"username": username, "password": password, "type": utype, "age": age})
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)

        messagebox.showinfo("Başarılı", "Kayıt tamamlandı!")
        open_login_screen(root)



    # Kayıt Ol butonu
    tk.Button(root, text="Kayıt Ol", command=register).pack(pady=5)

    # Geri butonu
    def go_back():
        open_login_screen(root)  # Geri butonuyla login ekranına dönme

    tk.Button(root, text="Giriş Yap", command=go_back).pack(pady=5)
