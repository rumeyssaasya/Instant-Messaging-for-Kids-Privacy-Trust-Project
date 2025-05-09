import tkinter as tk
from loginScreen import open_login_screen
from registerScreen import open_register_screen

def open_main_screen():
    # Ana ekranı oluşturuyoruz
    main_root = tk.Tk()
    main_root.title("SafeChat Kids - Ana Ekran")
    main_root.geometry("100x200")
    # Giriş Yap butonu
    tk.Button(main_root, text="Giriş Yap", command=lambda: open_login_screen(main_root)).pack(pady=20)

    # Kayıt Ol butonu
    tk.Button(main_root, text="Kayıt Ol", command=lambda: open_register_screen(main_root)).pack(pady=20)

    main_root.mainloop()
    
if __name__ == "__main__":
    open_main_screen()
