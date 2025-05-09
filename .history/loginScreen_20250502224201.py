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
