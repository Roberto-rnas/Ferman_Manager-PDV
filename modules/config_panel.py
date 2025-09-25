# modules/config_panel.py
import customtkinter as ctk
from tkinter import messagebox
from modules.utils import load_config as load_config_data, save_config as save_config_data
from modules.printer_utils import list_printers

def build(parent, on_back=None):
    for w in parent.winfo_children():
        w.destroy()

    scroll = ctk.CTkScrollableFrame(parent)
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(scroll, text="Configurações do Sistema", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)

    cfg = load_config_data()

    frame = ctk.CTkFrame(scroll)
    frame.pack(fill="x", padx=10, pady=10)

    # Instituição
    ctk.CTkLabel(frame, text="Instituição:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
    institution_entry = ctk.CTkEntry(frame)
    institution_entry.grid(row=0, column=1, padx=6, pady=6)
    institution_entry.insert(0, cfg.get("institution", ""))

    # Tipo de banco de dados
    ctk.CTkLabel(frame, text="Banco de Dados:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
    db_var = ctk.StringVar(value=cfg.get("db_type", "Excel"))
    db_option = ctk.CTkOptionMenu(frame, values=["Excel", "MySQL"], variable=db_var)
    db_option.grid(row=1, column=1, padx=6, pady=6)

    # Frame MySQL (inicialmente escondido)
    mysql_frame = ctk.CTkFrame(frame)
    mysql_frame.grid(row=2, column=0, columnspan=2, pady=6, sticky="we")
    mysql_frame.grid_remove()

    ctk.CTkLabel(mysql_frame, text="Host:").grid(row=0, column=0, padx=6, pady=3, sticky="w")
    host_entry = ctk.CTkEntry(mysql_frame)
    host_entry.grid(row=0, column=1, padx=6, pady=3)
    host_entry.insert(0, cfg.get("mysql_host", ""))

    ctk.CTkLabel(mysql_frame, text="Porta:").grid(row=1, column=0, padx=6, pady=3, sticky="w")
    port_entry = ctk.CTkEntry(mysql_frame)
    port_entry.grid(row=1, column=1, padx=6, pady=3)
    port_entry.insert(0, cfg.get("mysql_port", "3306"))

    ctk.CTkLabel(mysql_frame, text="Usuário:").grid(row=2, column=0, padx=6, pady=3, sticky="w")
    user_entry = ctk.CTkEntry(mysql_frame)
    user_entry.grid(row=2, column=1, padx=6, pady=3)
    user_entry.insert(0, cfg.get("mysql_user", ""))

    ctk.CTkLabel(mysql_frame, text="Senha:").grid(row=3, column=0, padx=6, pady=3, sticky="w")
    password_entry = ctk.CTkEntry(mysql_frame, show="*")
    password_entry.grid(row=3, column=1, padx=6, pady=3)
    password_entry.insert(0, cfg.get("mysql_password", ""))

    ctk.CTkLabel(mysql_frame, text="Database:").grid(row=4, column=0, padx=6, pady=3, sticky="w")
    database_entry = ctk.CTkEntry(mysql_frame)
    database_entry.grid(row=4, column=1, padx=6, pady=3)
    database_entry.insert(0, cfg.get("mysql_database", ""))

    # Mostrar/ocultar frame MySQL
    def toggle_mysql_frame(choice):
        if choice == "MySQL":
            mysql_frame.grid()
        else:
            mysql_frame.grid_remove()

    db_var.trace_add("write", lambda *args: toggle_mysql_frame(db_var.get()))
    toggle_mysql_frame(db_var.get())

    # Impressora
    ctk.CTkLabel(frame, text="Impressora Padrão:").grid(row=10, column=0, sticky="w", padx=6, pady=6)
    printers = list_printers()
    printer_var = ctk.StringVar(value=cfg.get("printer_name", printers[0] if printers else ""))
    printer_menu = ctk.CTkOptionMenu(frame, values=printers, variable=printer_var)
    printer_menu.grid(row=10, column=1, padx=6, pady=6)

    # Habilitar impressão de comprovantes
    receipt_var = ctk.BooleanVar(value=cfg.get("enable_receipt", True))
    ctk.CTkCheckBox(frame, text="Habilitar impressão de comprovantes", variable=receipt_var).grid(row=11, column=0, columnspan=2, padx=6, pady=6, sticky="w")

    # Habilitar impressão de tickets
    ticket_var = ctk.BooleanVar(value=cfg.get("enable_ticket", True))
    ctk.CTkCheckBox(frame, text="Habilitar impressão de tickets", variable=ticket_var).grid(row=12, column=0, columnspan=2, padx=6, pady=6, sticky="w")

    # Botões Salvar e Voltar
    btn_frame = ctk.CTkFrame(scroll)
    btn_frame.pack(pady=10)
    def save_config():
        new_cfg = {
            "institution": institution_entry.get().strip(),
            "db_type": db_var.get(),
            "printer_name": printer_var.get(),
            "enable_receipt": receipt_var.get(),
            "enable_ticket": ticket_var.get()
        }
        if db_var.get() == "MySQL":
            new_cfg.update({
                "mysql_host": host_entry.get().strip(),
                "mysql_port": port_entry.get().strip(),
                "mysql_user": user_entry.get().strip(),
                "mysql_password": password_entry.get(),
                "mysql_database": database_entry.get().strip()
            })
        save_config_data(new_cfg)
        messagebox.showinfo("Configurações", "Configurações salvas com sucesso!")

    ctk.CTkButton(btn_frame, text="Salvar", command=save_config).pack(side="left", padx=8)
    if on_back:
        ctk.CTkButton(btn_frame, text="Voltar", fg_color="gray25", command=on_back).pack(side="left", padx=8)

# Função utilitária
def load_config():
    return load_config_data()
