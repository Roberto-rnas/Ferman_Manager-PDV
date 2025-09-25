import customtkinter as ctk
from modules.stock_panel import open_stock_panel
from modules.sales_panel import open_sales_panel
from modules.admin_panel import open_admin_panel
from modules.reports import open_reports_panel

def open_main_dashboard(role):
    """Tela inicial do aplicativo após login"""

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("FERMON - Dashboard")
    root.state("zoomed")

    # ======== Título ========
    title = ctk.CTkLabel(root, text=f"Bem-vindo! Role: {role}", font=("Arial", 24, "bold"))
    title.pack(pady=20)

    # ======== Frame com botões ========
    frame = ctk.CTkFrame(root, corner_radius=15)
    frame.pack(pady=40, padx=40)

    # Função auxiliar para abrir painéis
    def open_panel(panel_func):
        root.withdraw()  # esconde dashboard
        panel_func()
        root.deiconify()  # volta ao dashboard

    # ======== Botões do Dashboard ========
    stock_btn = ctk.CTkButton(frame, text="Estoque", width=200,
                              command=lambda: open_panel(open_stock_panel))
    stock_btn.grid(row=0, column=0, padx=20, pady=10)

    sales_btn = ctk.CTkButton(frame, text="Vendas / PDV", width=200,
                              command=lambda: open_panel(open_sales_panel))
    sales_btn.grid(row=0, column=1, padx=20, pady=10)

    reports_btn = ctk.CTkButton(frame, text="Relatórios", width=200,
                                command=lambda: open_panel(open_reports_panel))
    reports_btn.grid(row=1, column=0, padx=20, pady=10)

    if role == "admin":
        admin_btn = ctk.CTkButton(frame, text="Administração", width=200,
                                  command=lambda: open_panel(open_admin_panel))
        admin_btn.grid(row=1, column=1, padx=20, pady=10)

    # ======== Botão de Sair ========
    exit_btn = ctk.CTkButton(root, text="Sair", fg_color="red", command=root.destroy)
    exit_btn.pack(pady=20)

    root.mainloop()
