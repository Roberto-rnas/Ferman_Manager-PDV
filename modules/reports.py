# modules/reports.py
import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
from modules.utils import DB_SALES   # Caminho padrão do banco de vendas

# Caso queira fixar manualmente para testes, descomente:
# DB_SALES = Path(r"C:\Users\rnascimento\Documents\Python\Fermon\db\sales.xlsx")

def build(parent, on_back=None):
    for w in parent.winfo_children():
        w.destroy()

    scroll = ctk.CTkScrollableFrame(parent)
    scroll.pack(fill="both", expand=True, padx=10, pady=10)

    ctk.CTkLabel(scroll, text="Relatórios de Vendas", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=8)

    # ---------------------- Filtros ---------------------- #
    filt = ctk.CTkFrame(scroll)
    filt.pack(fill="x", padx=6, pady=6)
    ctk.CTkLabel(filt, text="Data Inicial:").grid(row=0, column=0, padx=6)
    start = DateEntry(filt, date_pattern="dd/mm/yyyy")
    start.grid(row=0, column=1, padx=6)
    ctk.CTkLabel(filt, text="Data Final:").grid(row=0, column=2, padx=6)
    end = DateEntry(filt, date_pattern="dd/mm/yyyy")
    end.grid(row=0, column=3, padx=6)

    result = ctk.CTkFrame(scroll)
    result.pack(fill="both", expand=True, padx=6, pady=6)

    txt = ctk.CTkTextbox(result, height=200)
    txt.pack(fill="x", padx=6, pady=6)

    # ---------------------- Gráfico ---------------------- #
    chart_frame = ctk.CTkFrame(result)
    chart_frame.pack(fill="both", expand=True, padx=6, pady=6)

    fig, ax = plt.subplots(figsize=(7, 3))

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Guardar canvas/figura para liberar depois
    scroll._report_canvas = canvas
    scroll._report_fig = fig

    def gerar():
        """
        Gera o relatório na tela e gráfico.
        Guarda dois DataFrames:
            result._last_df  -> df filtrado (para exibição/estatística)
            result._full_df  -> df completo (para exportação)
        """
        txt.configure(state="normal")
        txt.delete("1.0", "end")
        ax.clear()

        if not DB_SALES.exists():
            txt.insert("end", "Nenhuma venda registrada.\n")
            canvas.draw()
            return

        # Lê sempre TODO o banco (para exportação completa)
        df_full = pd.read_excel(DB_SALES)

        if df_full.empty:
            txt.insert("end", "Nenhuma venda registrada.\n")
            canvas.draw()
            return

        # --- Padronizar colunas para compatibilidade ---
        col_mapping = {
            "item": "produto",
            "Item": "produto",
            "description": "produto",
            "produto": "produto",
            "quantity": "quantidade",
            "Quantity": "quantidade",
            "Qtd": "quantidade",
            "qtd": "quantidade",
            "price": "preco",
            "Price": "preco",
            "valor_entregue": "valor_entregue",
            "total": "total",
            "tipo_pagamento": "tipo_pagamento",
            "usuario": "usuario",
            "data": "data"
        }
        df_full.rename(columns=lambda x: col_mapping.get(x, x), inplace=True)

        # Filtro de período apenas para análise
        df_full["data"] = pd.to_datetime(df_full["data"], dayfirst=True, errors="coerce")
        mask = (
            df_full["data"].dt.normalize() >= pd.to_datetime(start.get_date()).normalize()
        ) & (
            df_full["data"].dt.normalize() <= pd.to_datetime(end.get_date()).normalize()
        )
        df_filtered = df_full.loc[mask].copy()

        if df_filtered.empty:
            txt.insert("end", "Nenhum registro no período.\n")
            canvas.draw()
            return

        df_filtered["receita"] = df_filtered["quantidade"] * df_filtered["preco"]
        grouped = (
            df_filtered.groupby("produto")
            .agg(qtd=("quantidade", "sum"), receita=("receita", "sum"))
            .reset_index()
            .sort_values("receita", ascending=False)
        )

        for _, r in grouped.iterrows():
            txt.insert("end", f"{r['produto']} | Qtd: {int(r['qtd'])} | Receita: R$ {r['receita']:.2f}\n")

        total = grouped["receita"].sum()
        txt.insert("end", f"\nTotal Geral: R$ {total:.2f}\n")

        # Gráfico
        # Cor do frame (fundo do scroll)
        frame_bg = scroll.cget("fg_color")  # pega a cor real do CTkScrollableFrame

        # Tornar fundo do gráfico transparente
        fig.patch.set_alpha(0)      # fundo da figura
        ax.set_facecolor("none")    # fundo do eixo transparente

        # Gráfico
        # Identifica o modo Dark ou Light
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            bg_color   = "#FF8C00" # Laranja forte
            bar_color  = "#1E90FF"  # Azul Dodger
            text_color = "white"
            
        else:
            bg_color   = "#1E90FF"  # Azul claro
            bar_color  = "#FF8C00"  # Laranja forte
            text_color = "black"
            

        # Gráfico
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.bar(grouped["produto"].astype(str), grouped["receita"], color=bar_color)
        ax.set_title("Receita por Produto", color=text_color)

        fig.tight_layout()
        canvas.draw()

        # Guardar para exportação
        result._last_df = df_filtered       # filtrado (se precisar no futuro)
        result._full_df = df_full           # COMPLETO (exportar todos os campos)


    def export_xlsx():
        """
        Exporta TODO o banco de dados, não apenas o filtrado.
        """
        dfexp = getattr(result, "_full_df", None)
        if dfexp is None:
            messagebox.showinfo("Exportar", "Gere relatório antes de exportar.")
            return
        file = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            title="Salvar relatório completo"
        )
        if file:
            # Exporta todas as colunas sem índice
            dfexp.to_excel(file, index=False)
            messagebox.showinfo("Exportar", "Relatório completo exportado com sucesso.")

    # ---------------------- Botões ---------------------- #
    btns = ctk.CTkFrame(scroll)
    btns.pack(pady=6)
    ctk.CTkButton(btns, text="Gerar Relatório", command=gerar).pack(side="left", padx=6)
    ctk.CTkButton(btns, text="Exportar Excel (Completo)", command=export_xlsx).pack(side="left", padx=6)
    if on_back:
        ctk.CTkButton(btns, text="Voltar", command=on_back).pack(side="left", padx=6)

            # Função de limpeza para quando clicar em voltar
    def cleanup():
        try:
            # fecha a figura do matplotlib para liberar recursos
            if hasattr(scroll, "_report_fig"):
                plt.close(scroll._report_fig)
        except Exception:
            pass

    if on_back:
        orig_on_back = on_back
        def wrapped_back():
            cleanup()
            orig_on_back()
        # substitui o botão Voltar
        for btn in btns.winfo_children():
            if btn.cget("text") == "Voltar":
                btn.configure(command=wrapped_back)