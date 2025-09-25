import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.geometry("400x300")
root.title("Teste Foco Automático")

def abrir_janela(item):
    win = ctk.CTkToplevel(root)
    win.title(f"Quantidade - {item}")
    win.geometry("250x150")
    win.grab_set()  # impede clicar fora enquanto a janela está aberta

    ctk.CTkLabel(win, text=f"Informe a quantidade de {item}:").pack(pady=10)

    quantidade_entry = ctk.CTkEntry(win, width=100)
    quantidade_entry.pack(pady=10)

    # 🔑 foco imediato para já digitar
    win.after(100, lambda: (quantidade_entry.focus_set(),
                            quantidade_entry.select_range(0, "end")))

    def confirmar(event=None):
        print(f"Item: {item} | Quantidade: {quantidade_entry.get()}")
        win.destroy()

    # Enter confirma
    quantidade_entry.bind("<Return>", confirmar)

    ctk.CTkButton(win, text="OK", command=confirmar).pack(pady=5)

# --- Layout principal ---
frame_itens = ctk.CTkFrame(root)
frame_itens.pack(pady=20)

for produto in ["Item A", "Item B", "Item C"]:
    btn = ctk.CTkButton(frame_itens, text=produto,
                        command=lambda p=produto: abrir_janela(p))
    btn.pack(pady=5)

root.mainloop()
