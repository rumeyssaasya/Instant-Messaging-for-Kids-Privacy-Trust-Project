import tkinter as tk

def open_dashboard(root, user):
    for widget in root.winfo_children():
        widget.destroy()

    tk.Label(root, text=f"Hoş geldin, {user['username']}!").pack()
    if user["type"] == "parent":
        tk.Label(root, text="(Ebeveyn hesabı)").pack()
    else:
        tk.Label(root, text="(Çocuk hesabı)").pack()

    tk.Label(root, text="Mesajlaşma paneli buraya gelecek.").pack(pady=20)
