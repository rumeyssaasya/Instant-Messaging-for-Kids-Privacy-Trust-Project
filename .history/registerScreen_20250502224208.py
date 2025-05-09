import tkinter as tk

def open_register_screen(main_root):
    # Kayıt ekranını oluşturuyoruz
    register_root = tk.Toplevel(main_root)  # Yeni pencere açıyoruz
    register_root.title("Kayıt Ol")

    # Kayıt ekranındaki başlık
    tk.Label(register_root, text="Kayıt Olma Ekranı").pack(pady=20)

    # Geri butonu
    def go_back():
        register_root.destroy()  # Kayıt ekranını kapat
        main_root.deiconify()  # Ana ekranı göster

    tk.Button(register_root, text="Geri", command=go_back).pack(pady=10)
    
    # Ana ekranı gizle
    main_root.withdraw()
    register_root.mainloop()
