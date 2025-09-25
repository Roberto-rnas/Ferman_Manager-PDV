# modules/stock_panel.py
import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
from pathlib import Path
from modules.utils import load_items, save_items, DB_STOCK

def build(parent, on_back=None):
    # Limpa o conteúdo anterior
    for w in parent.winfo_children():
        w.destroy()

    frame = ctk.CTkFrame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(frame, text="Estoque de Itens", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)

    # Scrollable frame para listar os itens
    list_frame = ctk.CTkScrollableFrame(frame, height=300)
    list_frame.pack(fill="x", pady=8)

    # Carrega itens do estoque
    stock_df = load_items(DB_STOCK)

    selected_item_index = [None]  # índice do item selecionado na listagem
    card_frames = []  # lista para controlar os frames

    def refresh_list():
        # Limpa listagem
        for w in list_frame.winfo_children():
            w.destroy()
        card_frames.clear()
        # Recarrega DataFrame
        nonlocal stock_df
        stock_df = load_items(DB_STOCK)
        if stock_df.empty:
            ctk.CTkLabel(list_frame, text="Nenhum item cadastrado.").pack()
            return
        for idx, row in stock_df.iterrows():
            # Cartão visual do item
            item_frame = ctk.CTkFrame(list_frame, corner_radius=10, border_width=2, fg_color="#FFA500")  # laranja
            item_frame.pack(fill="x", padx=5, pady=5)
            card_frames.append(item_frame)

            text = f"{row['description']} | Saldo: {row['balance']} | Custo: {row['cost']} | Preço: {row['price']}"
            lbl = ctk.CTkLabel(item_frame, text=text, anchor="w")
            lbl.pack(fill="x", padx=5, pady=5)

            def select_item(event, idx=idx):
                selected_item_index[0] = idx
                # destaca o item selecionado
                for i, f in enumerate(card_frames):
                    if i == idx:
                        f.configure(fg_color="#FF8C00")  # laranja mais escuro
                    else:
                        f.configure(fg_color="#FFA500")  # laranja normal

            item_frame.bind("<Button-1>", select_item)
            lbl.bind("<Button-1>", select_item)

    def open_modal(edit=False):
        modal = ctk.CTkToplevel()
        modal.title("Cadastrar Item" if not edit else "Editar Item")
        modal.geometry("400x350")
        modal.grab_set()  # modal

        ctk.CTkLabel(modal, text="Descrição").pack(pady=5)
        desc_entry = ctk.CTkEntry(modal)
        desc_entry.pack(pady=5, padx=20, anchor="center")

        ctk.CTkLabel(modal, text="Saldo").pack(pady=5)
        balance_entry = ctk.CTkEntry(modal)
        balance_entry.pack(pady=5, padx=20)

        ctk.CTkLabel(modal, text="Custo").pack(pady=5)
        cost_entry = ctk.CTkEntry(modal)
        cost_entry.pack(pady=5, padx=20)

        ctk.CTkLabel(modal, text="Preço de Venda").pack(pady=5)
        price_entry = ctk.CTkEntry(modal)
        price_entry.pack(pady=5, padx=20)

        if edit and selected_item_index[0] is not None:
            row = stock_df.loc[selected_item_index[0]]
            desc_entry.insert(0, row["description"])
            balance_entry.insert(0, str(row["balance"]))
            cost_entry.insert(0, str(row["cost"]))
            price_entry.insert(0, str(row["price"]))

        def salvar():
            desc = desc_entry.get().strip()
            bal = balance_entry.get().strip()
            cost = cost_entry.get().strip()
            price = price_entry.get().strip()
            if not desc or not bal or not cost or not price:
                messagebox.showwarning("Aviso", "Preencha todos os campos")
                return
            try:
                bal = float(bal)
                cost = float(cost)
                price = float(price)
            except ValueError:
                messagebox.showwarning("Aviso", "Saldo, custo e preço devem ser números")
                return

            nonlocal stock_df
            if edit and selected_item_index[0] is not None:
                # Atualiza item existente
                stock_df.loc[selected_item_index[0]] = [desc, bal, cost, price]
            else:
                # Novo item
                stock_df.loc[len(stock_df)] = [desc, bal, cost, price]

            save_items(stock_df)
            refresh_list()
            modal.destroy()

        btn_frame = ctk.CTkFrame(modal)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Salvar", command=salvar).pack(side="left", padx=8)
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray30", command=modal.destroy).pack(side="left", padx=8)

    def incluir_item():
        open_modal(edit=False)

    def alterar_item():
        if selected_item_index[0] is None:
            messagebox.showinfo("Info", "Selecione um item para alterar")
            return
        open_modal(edit=True)

    def excluir_item():
        if selected_item_index[0] is None:
            messagebox.showinfo("Info", "Selecione um item para excluir")
            return
        confirm = messagebox.askyesno("Confirmar", "Deseja realmente excluir o item selecionado?")
        if confirm:
            stock_df.drop(index=selected_item_index[0], inplace=True)
            stock_df.reset_index(drop=True, inplace=True)
            save_items(stock_df)
            selected_item_index[0] = None
            refresh_list()

    # --- Botões ---
    btn_frame = ctk.CTkFrame(frame)
    btn_frame.pack(pady=10)
    ctk.CTkButton(btn_frame, text="Incluir", command=incluir_item).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Alterar", command=alterar_item).pack(side="left", padx=8)
    ctk.CTkButton(btn_frame, text="Excluir", command=excluir_item).pack(side="left", padx=8)
    if on_back:
        ctk.CTkButton(btn_frame, text="Voltar", fg_color="gray25", command=on_back).pack(side="left", padx=8)

    refresh_list()
