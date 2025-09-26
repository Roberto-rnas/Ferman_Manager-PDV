# modules/sales_panel.py
import customtkinter as ctk
from tkinter import messagebox
from modules.utils import load_items, save_items, DB_STOCK, DB_SALES
from modules.config_panel import load_config
from modules.printer_utils import print_receipt, print_ticket
import pandas as pd
from pathlib import Path
from datetime import datetime

def build(parent, username=None, on_back=None):
    for w in parent.winfo_children():
        w.destroy()

    frame = ctk.CTkFrame(parent)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(frame, text="PDV - Vendas", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)

    carrinho = []

    container = ctk.CTkFrame(frame)
    container.pack(fill="both", expand=True)

    # Lista de itens
    items_frame = ctk.CTkScrollableFrame(container, width=500)
    items_frame.pack(side="left", fill="both", expand=True, padx=6, pady=6)

    # Carrinho
    carrinho_frame = ctk.CTkFrame(container, width=400)
    carrinho_frame.pack(side="left", fill="both", expand=True, padx=6, pady=6)

    carrinho_scroll = ctk.CTkScrollableFrame(carrinho_frame, width=380, height=400)
    carrinho_scroll.pack(fill="both", expand=True, padx=6, pady=6)

    btn_frame = ctk.CTkFrame(carrinho_frame)
    btn_frame.pack(pady=5)
    if on_back:
        ctk.CTkButton(btn_frame, text="Voltar", fg_color="gray25", command=on_back).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Finalizar Venda", command=lambda: finalizar_venda()).pack(side="left", padx=5)
    ctk.CTkButton(btn_frame, text="Limpar Carrinho", command=lambda: carrinho.clear() or atualizar_carrinho()).pack(side="left", padx=5)

    cfg = load_config()

    # --- Funções ---
    def atualizar_lista():
        for w in items_frame.winfo_children():
            w.destroy()
        stock_df = load_items(DB_STOCK)
        if stock_df.empty:
            ctk.CTkLabel(items_frame, text="Nenhum item em estoque").pack()
            return
        for _, row in stock_df.iterrows():
            txt = f"{row['description']}\nSaldo: {row['balance']} | Custo: R${row['cost']} | Preço: R${row['price']}"
            card = ctk.CTkFrame(items_frame, corner_radius=10, fg_color="#1E90FF", height=80)
            card.pack(padx=5, pady=5, fill="x")
            lbl = ctk.CTkLabel(card, text=txt, text_color="white", font=ctk.CTkFont(size=12))
            lbl.pack(padx=5, pady=5)

            def on_click(event=None, r=row):
                adicionar_ao_carrinho(r)
            card.bind("<Button-1>", on_click)
            lbl.bind("<Button-1>", on_click)

    def atualizar_carrinho():
        for w in carrinho_scroll.winfo_children():
            w.destroy()

        total = sum(item['quantity'] * item['price'] for item in carrinho)

        for idx, item in enumerate(carrinho):
            card = ctk.CTkFrame(carrinho_scroll, fg_color="#FF8C00", corner_radius=10)
            card.pack(fill="x", padx=5, pady=5)

            texto = (
                f"{item['item']}\n"
                f"Qtd: {item['quantity']} | "
                f"Preço: R${item['price']:.2f} | "
                f"Subtotal: R${item['quantity'] * item['price']:.2f}"
            )
            lbl = ctk.CTkLabel(card, text=texto, text_color="black", anchor="w", justify="left")
            lbl.pack(fill="x", padx=8, pady=6)

            card.bind("<Button-1>", lambda e, i=idx: alterar_quantidade(i))
            lbl.bind("<Button-1>", lambda e, i=idx: alterar_quantidade(i))

        total_card = ctk.CTkFrame(carrinho_scroll, fg_color="#FF8C00", corner_radius=10)
        total_card.pack(fill="x", padx=5, pady=10)
        ctk.CTkLabel(
            total_card,
            text=f"TOTAL: R$ {total:.2f}",
            text_color="black",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(padx=8, pady=6)

    def adicionar_ao_carrinho(item):
        win = ctk.CTkToplevel()
        win.title(f"Quantidade - {item['description']}")
        win.geometry("300x150")
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (300 // 2)
        y = (win.winfo_screenheight() // 2) - (150 // 2)
        win.geometry(f"300x150+{x}+{y}")

        ctk.CTkLabel(win, text=f"{item['description']}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        ctk.CTkLabel(win, text=f"Saldo disponível: {item['balance']}").pack(pady=5)
        qtd_entry = ctk.CTkEntry(win)
        qtd_entry.pack(pady=5)

        # 🔑 Foco imediato e seleção de texto
        win.after(100, lambda: (qtd_entry.focus_set(), qtd_entry.select_range(0, "end")))

        def confirmar(event=None):
            try:
                qtd = int(qtd_entry.get())
                if qtd <= 0 or qtd > item['balance']:
                    messagebox.showerror("Erro", "Quantidade inválida")
                    return
                carrinho.append({'item': item['description'], 'quantity': qtd, 'price': item['price']})
                win.destroy()
                atualizar_carrinho()
            except:
                messagebox.showerror("Erro", "Quantidade inválida")

        qtd_entry.bind("<Return>", confirmar)
        ctk.CTkButton(win, text="OK", command=confirmar).pack(pady=5)

    def alterar_quantidade(idx):
        item = carrinho[idx]
        win = ctk.CTkToplevel()
        win.title(f"Editar - {item['item']}")
        win.geometry("300x180")
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (300 // 2)
        y = (win.winfo_screenheight() // 2) - (180 // 2)
        win.geometry(f"300x180+{x}+{y}")

        ctk.CTkLabel(win, text=f"{item['item']}", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)

        qtd_entry = ctk.CTkEntry(win)
        qtd_entry.insert(0, str(item['quantity']))
        qtd_entry.pack(pady=5)

        win.after(100, lambda: (qtd_entry.focus_set(), qtd_entry.select_range(0, "end")))

        def salvar(event=None):
            try:
                nova_qtd = qtd_entry.get().strip()
                if nova_qtd == "":  # Se vazio, deleta
                    carrinho.pop(idx)
                else:
                    nova_qtd = int(nova_qtd)
                    if nova_qtd <= 0:
                        carrinho.pop(idx)
                    else:
                        carrinho[idx]['quantity'] = nova_qtd
                win.destroy()
                atualizar_carrinho()
            except:
                messagebox.showerror("Erro", "Quantidade inválida")

        def deletar():
            carrinho.pop(idx)
            win.destroy()
            atualizar_carrinho()

        qtd_entry.bind("<Return>", salvar)
        ctk.CTkButton(win, text="Salvar", command=salvar).pack(pady=5)
        ctk.CTkButton(win, text="Excluir Item", fg_color="red", command=deletar).pack(pady=5)

        def confirmar(event=None):
            try:
                nova_qtd = int(qtd_entry.get())
                if nova_qtd <= 0:
                    carrinho.pop(idx)
                else:
                    carrinho[idx]['quantity'] = nova_qtd
                win.destroy()
                atualizar_carrinho()
            except:
                messagebox.showerror("Erro", "Quantidade inválida")

        qtd_entry.bind("<Return>", confirmar)
        ctk.CTkButton(win, text="OK", command=confirmar).pack(pady=5)

    def finalizar_venda():
        if not carrinho:
            messagebox.showinfo("Info", "Carrinho vazio")
            return

        win = ctk.CTkToplevel()
        win.title("Pagamento")
        win.geometry("300x200")
        win.grab_set()
        win.update_idletasks()
        x = (win.winfo_screenwidth() // 2) - (300 // 2)
        y = (win.winfo_screenheight() // 2) - (200 // 2)
        win.geometry(f"300x200+{x}+{y}")

        ctk.CTkLabel(win, text="Escolha a forma de pagamento", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=10)
        ctk.CTkButton(win, text="Pix", command=lambda: [registrar_venda("Pix"), win.destroy()]).pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(win, text="Dinheiro", command=lambda: [win.destroy(), pagar_dinheiro()]).pack(pady=10, fill="x", padx=20)

    def pagar_dinheiro():
        total = sum(item['quantity']*item['price'] for item in carrinho)
        win2 = ctk.CTkToplevel()
        win2.title("Pagamento em Dinheiro")
        win2.geometry("300x200")
        win2.grab_set()
        win2.update_idletasks()
        x = (win2.winfo_screenwidth() // 2) - (300 // 2)
        y = (win2.winfo_screenheight() // 2) - (200 // 2)
        win2.geometry(f"300x200+{x}+{y}")

        ctk.CTkLabel(win2, text=f"Total a pagar: R$ {total:.2f}", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=5)
        valor_entry = ctk.CTkEntry(win2)
        valor_entry.pack(pady=5)

        # 🔑 Foco imediato
        win2.after(100, lambda: (valor_entry.focus_set(), valor_entry.select_range(0, "end")))

        troco_label = ctk.CTkLabel(win2, text="Troco: R$ 0.00", font=ctk.CTkFont(size=12))
        troco_label.pack(pady=5)

        def calcular_troco(event=None):
            try:
                valor = float(valor_entry.get())
                troco = max(valor - total, 0)
                troco_label.configure(text=f"Troco: R$ {troco:.2f}")
            except:
                troco_label.configure(text="Troco: R$ 0.00")

        valor_entry.bind("<KeyRelease>", calcular_troco)

        def finalizar(event=None):
            try:
                registrar_venda("Dinheiro", valor_entregue=float(valor_entry.get()))
                win2.destroy()
            except:
                messagebox.showerror("Erro", "Valor inválido")

        valor_entry.bind("<Return>", finalizar)
        ctk.CTkButton(win2, text="Confirmar", command=finalizar).pack(pady=5)

    def registrar_venda(payment_type, valor_entregue=None):
        df_stock = load_items(DB_STOCK)
        for item in carrinho:
            idx = df_stock.index[df_stock['description'] == item['item']][0]
            df_stock.at[idx, 'balance'] -= item['quantity']
        save_items(df_stock)

        sales_file = Path(DB_SALES)

        # 🔹 PADRONIZAÇÃO: sempre salva com nomes fixos
        registros = []
        for item in carrinho:
            registros.append({
                "data": datetime.now(),
                "usuario": username,
                "tipo_pagamento": payment_type,
                "produto": item["item"],      # ✅ padronizado
                "quantidade": item["quantity"], # ✅ padronizado
                "preco": item["price"],         # ✅ padronizado
                "valor_entregue": valor_entregue,
                "total": item["quantity"] * item["price"]
            })

        df_sales = pd.DataFrame(registros)

        # Se já existe, concatena mantendo colunas corretas
        if sales_file.exists():
            df_exist = pd.read_excel(sales_file)
            df_sales = pd.concat([df_exist, df_sales], ignore_index=True)

        # Grava sempre com as colunas fixas
        df_sales = df_sales[
            ["data","usuario","tipo_pagamento","produto","quantidade",
            "preco","valor_entregue","total"]
        ]
        df_sales.to_excel(sales_file, index=False)

        # Impressão automática
        if cfg.get("enable_receipt", True):
            print_receipt(carrinho, username=username,
                        payment_type=payment_type, valor_entregue=valor_entregue)
        if cfg.get("enable_ticket", True):
            print_ticket(carrinho, username=username,
                        payment_type=payment_type, valor_entregue=valor_entregue)

        carrinho.clear()
        atualizar_lista()
        atualizar_carrinho()
        messagebox.showinfo("Sucesso", "Venda finalizada!")


    atualizar_lista()
    atualizar_carrinho()