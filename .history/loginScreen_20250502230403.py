import tkinter as tk
from tkinter import messagebox
import json
from dashboard import open_dashboard

def open_login_screen(main_root):
    # Giriş ekranını oluşturuyoruz
    login_root = tk.Toplevel(main_root)  # Yeni pencere açıyoruz
    login_root.title("Giriş Yap")
    login_root.geometry("150x200")
    # Giriş ekranındaki başlık
    tk.Label(login_root, text="Kullanıcı Adı").pack(pady=5)
    username_entry = tk.Entry(login_root)
    username_entry.pack(pady=5)

    tk.Label(login_root, text="Şifre").pack(pady=5)
    password_entry = tk.Entry(login_root, show="*")
    password_entry.pack(pady=5)

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
                open_dashboard(login_root, user)  # Dashboard ekranına geç
                login_root.destroy()  # Giriş ekranını kapat
                return

        messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı.")

    tk.Button(login_root, text="Giriş Yap", command=login).pack(pady=5)

    # Geri butonunun işlevini tanımlıyoruz
    def go_back():
        login_root.destroy()  # Giriş ekranını kapat
        main_root.deiconify()  # Ana ekranı göster

    tk.Button(login_root, text="Geri", command=go_back).pack(pady=5)

    # Ana ekranı gizle
    main_root.withdraw()

    login_root.mainloop()
