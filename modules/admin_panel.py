# modules/admin_panel.py
import customtkinter as ctk
from tkinter import messagebox
from modules.utils import load_users, save_users, hash_pw

def build(parent, on_back=None):
    # Limpa conteúdo anterior
    for w in parent.winfo_children():
        w.destroy()

    frame = ctk.CTkFrame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(frame, text="Administração de Usuários", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)

    list_frame = ctk.CTkScrollableFrame(frame, height=400)
    list_frame.pack(fill="x", pady=8)

    selected_index = [None]  # índice do usuário selecionado

    def refresh_list():
        for w in list_frame.winfo_children():
            w.destroy()
        users_df = load_users()
        if users_df.empty:
            ctk.CTkLabel(list_frame, text="Nenhum usuário cadastrado.").pack()
            return
        for idx, row in users_df.iterrows():
            # Card do usuário
            card = ctk.CTkFrame(list_frame, fg_color="#FFA500", corner_radius=10, border_width=2)
            card.pack(fill="x", padx=5, pady=5)

            txt = f"Usuário: {row['username']}\nTipo: {row['role']}"
            lbl = ctk.CTkLabel(card, text=txt, anchor="w")
            lbl.pack(fill="x", padx=5, pady=5)

            def select_user(event, idx=idx, card=card):
                selected_index[0] = idx
                # destaca somente o card selecionado
                for f in list_frame.winfo_children():
                    f.configure(fg_color="#FFA500")
                card.configure(fg_color="#FF8C00")  # cor mais escura quando selecionado

            card.bind("<Button-1>", select_user)
            lbl.bind("<Button-1>", select_user)

    def add_user():
        open_modal(edit=False)

    def edit_user():
        if selected_index[0] is None:
            messagebox.showinfo("Info", "Selecione um usuário para alterar")
            return
        open_modal(edit=True)

    def delete_user():
        if selected_index[0] is None:
            messagebox.showinfo("Info", "Selecione um usuário para excluir")
            return
        confirm = messagebox.askyesno("Confirmar", "Deseja realmente excluir o usuário selecionado?")
        if confirm:
            df = load_users()
            df.drop(index=selected_index[0], inplace=True)
            df.reset_index(drop=True, inplace=True)
            save_users(df)
            selected_index[0] = None
            refresh_list()

    def open_modal(edit=False):
        modal = ctk.CTkToplevel()
        modal.title("Cadastrar Usuário" if not edit else "Editar Usuário")
        modal.geometry("400x300")
        modal.grab_set()

        ctk.CTkLabel(modal, text="Usuário").pack(pady=5)
        user_entry = ctk.CTkEntry(modal)
        user_entry.pack(pady=5, padx=20)

        ctk.CTkLabel(modal, text="Senha").pack(pady=5)
        pass_entry = ctk.CTkEntry(modal)
        pass_entry.pack(pady=5, padx=20)

        ctk.CTkLabel(modal, text="Tipo").pack(pady=5)
        role_entry = ctk.CTkOptionMenu(modal, values=["user", "admin"])
        role_entry.pack(pady=5, padx=20)

        df = load_users()
        if edit and selected_index[0] is not None:
            row = df.loc[selected_index[0]]
            user_entry.insert(0, row["username"])
            role_entry.set(row["role"])

        def save_user():
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            role = role_entry.get()
            if not username or (not edit and not password) or not role:
                messagebox.showwarning("Aviso", "Preencha todos os campos")
                return
            df = load_users()
            if edit:
                df.loc[selected_index[0], "username"] = username
                if password:
                    df.loc[selected_index[0], "password_hash"] = hash_pw(password)
                df.loc[selected_index[0], "role"] = role
            else:
                df.loc[len(df)] = {"username": username, "password_hash": hash_pw(password), "role": role}
            save_users(df)
            refresh_list()
            modal.destroy()

        btn_frame = ctk.CTkFrame(modal)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Salvar", command=save_user).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray30", command=modal.destroy).pack(side="left", padx=8)

    # Botões principais
    btn_frame = ctk.CTkFrame(frame)
    btn_frame.pack(pady=10)
    ctk.CTkButton(btn_frame, text="Incluir", command=add_user).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Alterar", command=edit_user).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Excluir", command=delete_user).pack(side="left", padx=8)
    if on_back:
        ctk.CTkButton(btn_frame, text="Voltar", fg_color="gray25", command=on_back).pack(side="left", padx=8)

    refresh_list()
