import customtkinter as ctk
from modules.utils import authenticate
from modules import admin_panel, stock_panel, sales_panel, reports, config_panel
from modules.config_panel import load_config_data, save_config_data
from pathlib import Path
import os
from PIL import Image, ImageEnhance

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        cfg = load_config_data()
        self.institution = cfg.get("institution", "FERMAN")
        self.title(f"FERMAN - Management: {self.institution}")

        # Ícone
        icon_path = r"C:\Users\rnascimento\Documents\Python\Fermon\assets\icon.ico"
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print("Erro ao aplicar ícone:", e)

        self.maxsize(1920, 1080)
        self.minsize(1000, 600)

        self.role = None
        self.username = None
        self.sidebar = None
        self.content_frame = None

        # Marca d'água no fundo
        watermark_path = r"C:\Users\rnascimento\Documents\Python\Fermon\assets\watermark.png"

        if Path(watermark_path).exists():
            try:
                img = Image.open(watermark_path).convert("RGBA")
                # Ajusta a opacidade
                alpha = img.split()[3]
                alpha = ImageEnhance.Brightness(alpha).enhance(0.7)
                img.putalpha(alpha)
                self.bg_image = ctk.CTkImage(light_image=img, dark_image=img, size=(1000, 600))
                self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                self.bg_label.place(relx=0.5, rely=0.5, anchor="center")
                self.bg_label.lower()  # coloca atrás de tudo
            except Exception as e:
                print("Erro ao carregar marca d'água:", e)

        self.show_login()

    # ---- Login ----
    def show_login(self):
        self.clear()

        # Frame centralizado para os campos de login, sem cor de fundo
        self.login_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo/Marca d'água por trás dos campos
        logo_path = r"C:\Users\rnascimento\Documents\Python\Fermon\assets\watermark.png"
        if Path(logo_path).exists():
            try:
                logo_img = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(300, 300)
                )
                logo_label = ctk.CTkLabel(self.login_frame, image=logo_img, text="")
                logo_label.pack(pady=(0, 20))  # espaço abaixo da logo
            except Exception as e:
                print("Erro ao carregar logo:", e)

        # Campos de login
        self.user_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Usuário", width=250)
        self.user_entry.pack(pady=5)

        self.pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Senha", show="*", width=250)
        self.pass_entry.pack(pady=5)
        
        # Permite acionar login com a tecla Enter no campo senha
        self.pass_entry.bind("<Return>", lambda event: self.do_login())

        # Switch de Aparência no canto superior direito
        def toggle_appearance():
            new_mode = "Dark" if ctk.get_appearance_mode() == "Light" else "Light"
            ctk.set_appearance_mode(new_mode)

        appearance_switch = ctk.CTkSwitch(
            self,
            text="Modo Dark/Light",
            command=toggle_appearance
        )
        appearance_switch.place(relx=0.98, rely=0.02, anchor="ne")
        # Inicializa conforme modo atual
        appearance_switch.select() if ctk.get_appearance_mode() == "Dark" else appearance_switch.deselect()

        # Botão de login
        ctk.CTkButton(self.login_frame, text="Entrar", width=150, command=self.do_login).pack(pady=15)

        # Mensagem de erro (inicialmente invisível)
        self.login_error_label = ctk.CTkLabel(self.login_frame, text="", text_color="red")
        self.login_error_label.pack(pady=5)


    def do_login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()  # <-- pegar senha aqui

        user = authenticate(u, p)
        if user:
            self.username = u
            self.role = user.get("role", "user")
            self.show_dashboard()
        else:
            self.login_error_label.configure(text="Credenciais inválidas")

    # ---- Dashboard ----
    def show_dashboard(self):
        self.clear()
        cfg = load_config_data()
        self.institution = cfg.get("institution", "FERMAN")
        self.title(f"FERMAN - Management: {self.institution}")

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        ctk.CTkLabel(self.sidebar, text=f"Usuário: {self.username}\nPerfil: {self.role}", font=ctk.CTkFont(size=12)).pack(pady=14)

        buttons = []
        if self.role.lower() == "admin":
            buttons += [
                ("Admin Usuários", lambda: self.load_content("admin")),
                ("Estoque", lambda: self.load_content("stock")),
                ("Vendas (PDV)", lambda: self.load_content("sales")),
                ("Relatórios", lambda: self.load_content("reports")),
                ("Configurações", lambda: self.load_content("config"))
            ]
        elif self.role.lower() == "user":
            buttons += [
                ("Estoque", lambda: self.load_content("stock")),
                ("Vendas (PDV)", lambda: self.load_content("sales")),
                ("Relatórios", lambda: self.load_content("reports"))
            ]
        for text, cmd in buttons:
            ctk.CTkButton(self.sidebar, text=text, command=cmd).pack(pady=6)
        ctk.CTkButton(self.sidebar, text="Logout", fg_color="red", command=self.logout).pack(side="bottom", pady=12, padx=10)

        # Conteúdo principal
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        if hasattr(self, "bg_label"):
            self.bg_label.lower()

        self.load_content("welcome")

    def load_content(self, page):
        for w in self.content_frame.winfo_children():
            w.destroy()

        if page == "welcome":
            welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent", corner_radius=0)
            welcome_frame.pack(expand=True, fill="both", pady=20)

            ctk.CTkLabel(welcome_frame, text=f"Olá {self.username},", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(40, 10))
            ctk.CTkLabel(welcome_frame, text="Bem-vindo ao FERMAN - Management", font=ctk.CTkFont(size=20)).pack(pady=(0, 20))

            # Logotipo
            logo_path = r"C:\Users\rnascimento\Documents\Python\Fermon\assets\fermon_logo.png"
            if Path(logo_path).exists():
                try:
                    logo_image = ctk.CTkImage(light_image=Image.open(logo_path),
                                              dark_image=Image.open(logo_path), size=(420, 420))
                    ctk.CTkLabel(welcome_frame, image=logo_image, text="").pack(pady=10)
                except Exception as e:
                    print("Erro ao carregar logo:", e)
            else:
                ctk.CTkLabel(welcome_frame, text="(Logo não encontrado)", text_color="gray").pack(pady=10)

        elif page == "admin":
            admin_panel.build(self.content_frame, on_back=self.show_dashboard)
        elif page == "stock":
            stock_panel.build(self.content_frame, on_back=self.show_dashboard)
        elif page == "sales":
            sales_panel.build(self.content_frame, username=self.username, on_back=self.show_dashboard)
        elif page == "reports":
            reports.build(self.content_frame, on_back=self.show_dashboard)
        elif page == "config":
            config_panel.build(self.content_frame, username_role=self.role, on_back=self.show_dashboard)

    def logout(self):
        self.role = None
        self.username = None
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            if w is not getattr(self, "bg_label", None):
                w.destroy()


if __name__ == "__main__":
    App().mainloop()