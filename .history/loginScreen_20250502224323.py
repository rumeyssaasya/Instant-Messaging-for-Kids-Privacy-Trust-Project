import tkinter as tk
from tkinter import messagebox
import json
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
    import tkinter as tk

def open_login_screen(main_root):
    # Giriş ekranını oluşturuyoruz
    login_root = tk.Toplevel(main_root)  # Yeni pencere açıyoruz
    login_root.title("Giriş Yap")

    # Giriş ekranındaki başlık
    tk.Label(login_root, text="Giriş Yap Ekranı").pack(pady=20)

    # Geri butonu
    def go_back():
        login_root.destroy()  # Giriş ekranını kapat
        main_root.deiconify()  # Ana ekranı göster

    tk.Button(login_root, text="Geri", command=go_back).pack(pady=10)
    
    # Ana ekranı gizle
    main_root.withdraw()
    login_root.mainloop()
