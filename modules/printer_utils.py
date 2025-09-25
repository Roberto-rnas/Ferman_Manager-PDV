# modules/printer_utils.py
from modules.utils import load_config
import win32print
import win32ui

def list_printers():
    """Retorna uma lista de impressoras disponíveis no sistema."""
    return [printer[2] for printer in win32print.EnumPrinters(2)]

def _print_text(printer_name, text):
    """Envia texto para a impressora especificada."""
    if not printer_name:
        print("Nenhuma impressora configurada.")
        return

    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Comprovante", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)
        win32print.WritePrinter(hPrinter, text.encode("utf-8"))
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
    finally:
        win32print.ClosePrinter(hPrinter)

def print_receipt(carrinho, username=None, payment_type=None, valor_entregue=None):
    """Gera e envia o comprovante de venda para impressão."""
    cfg = load_config()
    printer_name = cfg.get("printer_name")

    total = sum(item['quantity']*item['price'] for item in carrinho)
    valor_entregue_text = f"Valor entregue: R$ {valor_entregue:.2f}" if valor_entregue else ""
    troco_text = f"Troco: R$ {max((valor_entregue or 0) - total, 0):.2f}" if valor_entregue else ""

    text = f"=== COMPROVANTE DE VENDA ===\n"
    text += f"Usuário: {username}\n"
    text += f"Pagamento: {payment_type}\n"
    text += "----------------------------\n"
    for item in carrinho:
        text += f"{item['item']} x {item['quantity']} = R$ {item['quantity']*item['price']:.2f}\n"
    text += "----------------------------\n"
    text += f"TOTAL: R$ {total:.2f}\n"
    if valor_entregue:
        text += valor_entregue_text + "\n" + troco_text + "\n"
    text += "============================\n\n"

    _print_text(printer_name, text)

def print_ticket(carrinho, username=None, payment_type=None, valor_entregue=None):
    """Gera e envia um ticket simples para impressão (modo resumido)."""
    cfg = load_config()
    printer_name = cfg.get("printer_name")

    total = sum(item['quantity']*item['price'] for item in carrinho)

    text = f"--- TICKET DE VENDA ---\n"
    text += f"Usuário: {username}\n"
    text += f"Pagamento: {payment_type}\n"
    text += "------------------------\n"
    for item in carrinho:
        text += f"{item['item']} x {item['quantity']}\n"
    text += "------------------------\n"
    text += f"TOTAL: R$ {total:.2f}\n"
    text += "------------------------\n\n"

    _print_text(printer_name, text)
