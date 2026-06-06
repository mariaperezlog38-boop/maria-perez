sudo apt update && sudo apt upgrade -y
sudo apt install -y git zip unzip openjdk-17-jdk build-essential ccache \
  zlib1g-dev libncurses5-dev libgdbm-dev libffi-dev liblzma-dev \
  libssl-dev libsqlite3-devimport os
import sys
import threading
import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import simpledialog

try:
    from PIL import Image, ImageOps, ImageDraw
except ImportError:
    Image = None

import customtkinter as ctk
import updater

__version__ = "1.0.0"
UPDATE_INFO_URL = "https://example.com/calculadorabcv_update.json"

from calculadora_bcv_logic import (
    convert_amount,
    format_result,
    get_rate_from_pybcv,
    parse_amount,
    evaluate_expression,
)

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


class CalculadoraBCV(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Conversor Dólar ⇄ Bolívar (BCV)")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color=("#e4ecf5", "#24263b"))

        self.current_rate = None

        # When bundled with PyInstaller, data files are extracted to sys._MEIPASS
        if getattr(sys, "frozen", False):
            base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
        else:
            base_path = os.path.dirname(__file__)

        background_path = os.path.join(base_path, "fondo.png")
        if os.path.exists(background_path):
            if Image is not None:
                original_image = Image.open(background_path).convert("RGBA")
                try:
                    resample = Image.Resampling.LANCZOS
                except AttributeError:
                    resample = Image.LANCZOS

                self.bg_image = ctk.CTkImage(light_image=original_image, size=(420, 420))
                banner_image = ImageOps.fit(original_image, (376, 110), method=resample)
                self.banner_image = ctk.CTkImage(light_image=banner_image, size=(376, 110))
            else:
                self.bg_image = tk.PhotoImage(file=background_path)
                self.banner_image = None

            # use CTkLabel only when we created a CTkImage (Pillow available)
            if Image is not None:
                self.background_label = ctk.CTkLabel(self, image=self.bg_image, text="")
            else:
                self.background_label = tk.Label(self, image=self.bg_image)

            self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            # send background behind everything
            try:
                self.background_label.lower()
            except Exception:
                pass
        else:
            self.banner_image = None

        self.card = ctk.CTkFrame(
            self,
            corner_radius=25,
            border_width=2,
            border_color=("#ffffff", "#5b5b5b"),
            fg_color="transparent",
        )
        self.card.pack(expand=True, fill="both", padx=22, pady=22)

        # semi-transparent rounded overlay to improve contrast over the PNG background
        if Image is not None:
            try:
                overlay_w, overlay_h = (376, 320)
                overlay = Image.new("RGBA", (overlay_w, overlay_h), (255, 255, 255, 200))
                mask = Image.new("L", (overlay_w, overlay_h), 0)
                draw = ImageDraw.Draw(mask)
                radius = 24
                draw.rounded_rectangle((0, 0, overlay_w, overlay_h), radius=radius, fill=255)
                overlay.putalpha(mask)
                overlay_ctk = ctk.CTkImage(light_image=overlay, size=(overlay_w, overlay_h))
                overlay_label = ctk.CTkLabel(self.card, image=overlay_ctk, text="")
                overlay_label.place(
                    relx=0.5,
                    rely=0.15,
                    anchor="n",
                    width=overlay_w,
                    height=overlay_h,
                )
                overlay_label.lower()
            except Exception:
                pass
        else:
            # fallback: use a subtle card background color when Pillow not available
            self.card.configure(fg_color=("#eff6fb", "#2a3844"))

        if getattr(self, 'banner_image', None) is not None:
            banner_label = ctk.CTkLabel(self.card, image=self.banner_image, text="")
            banner_label.pack(fill="x", pady=(20, 12))

        self.label_titulo = ctk.CTkLabel(
            self.card,
            text="💱  Conversor Dólar ⇄ Bolívar",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color=("#164e63", "#ffe376"),
        )
        self.label_titulo.pack(pady=(0, 14))

        self.label_tasa = ctk.CTkLabel(
            self.card,
            text="Obteniendo tasa...",
            font=("Segoe UI", 16),
            text_color=("#24497a", "#ffe49b"),
        )
        self.label_tasa.pack()
        self.refrescar_tasa()

        ctk.CTkLabel(
            self.card,
            text="Ingrese monto y elija conversión:",
            font=("Segoe UI", 14),
            text_color=("#213049", "#ffd266"),
        ).pack(pady=(10, 5))

        entry_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        entry_frame.pack(pady=2)

        self.entry_cantidad = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Monto",
            width=120,
            height=38,
            corner_radius=12,
            font=("Segoe UI", 18, "bold"),
        )
        self.entry_cantidad.grid(row=0, column=0, padx=(0, 13), pady=6)

        self.modo = ctk.StringVar(value="USD a Bs")
        self.combo_modo = ctk.CTkSegmentedButton(
            entry_frame,
            values=["USD a Bs", "Bs a USD"],
            variable=self.modo,
            font=("Segoe UI", 15, "bold"),
            height=38,
            corner_radius=12,
        )
        self.combo_modo.grid(row=0, column=1, pady=6)

        self.btn_convertir = ctk.CTkButton(
            self.card,
            text="Convertir",
            font=("Segoe UI Bold", 15),
            height=40,
            corner_radius=16,
            fg_color=("#0ea063", "#53d10c"),
            hover_color=("#0bbf74", "#7aff38"),
            text_color=("#fff", "#263110"),
            command=self.convertir,
        )
        self.btn_convertir.pack(pady=(10, 3), ipadx=3)

        self.btn_limpiar = ctk.CTkButton(
            self.card,
            text="Limpiar",
            font=("Segoe UI", 14),
            height=35,
            corner_radius=16,
            fg_color=("#b2b2b2", "#4a4a4a"),
            hover_color=("#9ca3af", "#6b7280"),
            command=self.limpiar,
        )
        self.btn_limpiar.pack(pady=(0, 3), ipadx=3)

        self.btn_calc_basic = ctk.CTkButton(
            self.card,
            text="Calculadora básica",
            font=("Segoe UI", 12),
            height=36,
            corner_radius=12,
            fg_color=("#f6b26b", "#d97706"),
            hover_color=("#f59e0b", "#ffb74d"),
            command=self.open_calculadora_basica,
        )
        self.btn_calc_basic.pack(pady=(4, 6), ipadx=3)

        self.label_result = ctk.CTkLabel(
            self.card,
            text="",
            font=("Segoe UI Black", 22),
            text_color=("#155791", "#ffd166"),
        )
        self.label_result.pack(pady=(15, 5))

        self.btn_refrescar = ctk.CTkButton(
            self.card,
            text="⟳ Refrescar Tasa BCV",
            font=("Segoe UI Bold", 13),
            height=36,
            corner_radius=14,
            fg_color=("#b2cfff", "#786419"),
            hover_color=("#92b7fa", "#e1c464"),
            text_color=("#2d3862", "#fff8de"),
            command=self.refrescar_tasa,
        )
        self.btn_refrescar.pack(pady=(4, 10), ipadx=3)

        self.switch_tema = ctk.CTkSwitch(
            self.card,
            text="Tema oscuro",
            command=self.toggle_tema,
        )
        self.switch_tema.pack(anchor="e", pady=(3, 4), padx=5)

        self.btn_actualizar = ctk.CTkButton(
            self.card,
            text="Buscar actualización",
            font=("Segoe UI", 12),
            height=36,
            corner_radius=12,
            fg_color=("#6aa7ff", "#2b6cff"),
            hover_color=("#4e8efb", "#1f58f0"),
            command=self.check_update,
        )
        self.btn_actualizar.pack(pady=(6, 8), ipadx=3)

        self.bind("<Return>", lambda event: self.convertir())
        self.bind("<Escape>", lambda event: self.limpiar())
        self.entry_cantidad.focus_set()

        if ctk.get_appearance_mode().lower() == "dark":
            self.switch_tema.select()

        self.after(1200, self.startup_check_updates)

    def check_update(self):
        def worker():
            updated, msg = updater.check_for_updates(__version__, UPDATE_INFO_URL)
            try:
                messagebox.showinfo("Actualización", msg)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def startup_check_updates(self):
        def worker():
            _updated, msg = updater.check_for_updates(__version__, UPDATE_INFO_URL)
            if _updated:
                try:
                    messagebox.showinfo("Actualización disponible", msg)
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    def obtener_tasa(self) -> float | None:
        if self.current_rate is not None:
            return self.current_rate

        try:
            tasa = get_rate_from_pybcv()
        except Exception as error:
            messagebox.showwarning("Advertencia", f"Error al obtener la tasa BCV: {error}")
            tasa = None

        if tasa is not None:
            self.current_rate = tasa
            return tasa

        tasa_manual = simpledialog.askfloat(
            "Tasa BCV no disponible",
            "No se pudo obtener la tasa automáticamente.\n"
            "Ingresa la tasa BCV manualmente (Bs/USD):",
            minvalue=0.0,
        )

        if tasa_manual is None:
            return None
        if tasa_manual <= 0:
            messagebox.showerror("Error", "La tasa debe ser mayor que cero.")
            return None

        self.current_rate = tasa_manual
        return tasa_manual

    def convertir(self):
        try:
            cantidad = parse_amount(self.entry_cantidad.get())
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        tasa = self.obtener_tasa()
        if tasa is None:
            return

        try:
            resultado = convert_amount(cantidad, tasa, self.modo.get())
            self.label_result.configure(text=format_result(resultado, self.modo.get()))
        except ValueError as error:
            messagebox.showerror("Error", str(error))

    def limpiar(self):
        self.entry_cantidad.delete(0, "end")
        self.label_result.configure(text="")

    def open_calculadora_basica(self):
        top = ctk.CTkToplevel(self)
        top.title("Calculadora básica")
        top.geometry("320x420")
        top.resizable(False, False)

        entry = ctk.CTkEntry(top, placeholder_text="0", font=("Segoe UI", 22), justify="right")
        entry.pack(padx=10, pady=(10, 8), fill="x")

        result_label = ctk.CTkLabel(top, text="", font=("Segoe UI", 18))
        result_label.pack(pady=(0, 6))

        btn_frame = ctk.CTkFrame(top, fg_color="transparent")
        btn_frame.pack(padx=10, pady=6, fill="both", expand=True)

        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]

        def compute():
            try:
                res = evaluate_expression(entry.get())
                result_label.configure(text=str(res))
            except Exception as e:
                try:
                    messagebox.showerror("Error", str(e))
                except Exception:
                    pass

        def on_button_click(val):
            if val == "=":
                compute()
                return
            entry.insert("end", val)

        def on_clear():
            entry.delete(0, "end")
            result_label.configure(text="")

        def on_backspace():
            txt = entry.get()
            entry.delete(0, "end")
            entry.insert(0, txt[:-1])

        # top control buttons
        control_frame = ctk.CTkFrame(top, fg_color="transparent")
        control_frame.pack(padx=10, pady=(0, 6), fill="x")

        ctk.CTkButton(control_frame, text="C", width=60, command=on_clear).pack(side="left", padx=4)
        ctk.CTkButton(control_frame, text="⌫", width=60, command=on_backspace).pack(side="left", padx=4)

        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                b = ctk.CTkButton(
                    btn_frame,
                    text=label,
                    width=60,
                    height=44,
                    command=lambda v=label: on_button_click(v),
                )
                b.grid(row=r, column=c, padx=6, pady=6)

        # Bring to front, make transient and ensure focus for typing
        def focus_entry():
            try:
                top.focus_force()
                entry.focus_set()
            except Exception:
                pass

        try:
            top.transient(self)
            top.lift()
            top.attributes("-topmost", True)
            top.after(100, lambda: top.attributes("-topmost", False))
            top.grab_set()
            top.after(50, focus_entry)
            top.after(150, focus_entry)
        except Exception:
            pass

        # Execute compute on Enter
        top.bind("<Return>", lambda event: compute())
        entry.bind("<Return>", lambda event: compute())

        # Keyboard shortcuts: Esc to close, Delete to clear, Ctrl+C to copy result
        def copy_result(event=None):
            text = result_label.cget("text") or entry.get()
            if not text:
                try:
                    messagebox.showinfo("Copiar", "No hay resultado para copiar.")
                except Exception:
                    pass
                return
            try:
                top.clipboard_clear()
                top.clipboard_append(str(text))
                try:
                    messagebox.showinfo("Copiado", "Resultado copiado al portapapeles.")
                except Exception:
                    pass
            except Exception:
                pass

        top.bind("<Escape>", lambda event: top.destroy())
        top.bind("<Delete>", lambda event: on_clear())
        top.bind("<Control-c>", copy_result)
        top.bind("<Control-C>", copy_result)
        entry.bind("<Return>", lambda event: compute())
        entry.bind("<Control-c>", copy_result)
        entry.bind("<Control-C>", copy_result)
        entry.bind("<Delete>", lambda event: on_clear())

    def refrescar_tasa(self):
        try:
            tasa = get_rate_from_pybcv()
        except Exception as error:
            messagebox.showwarning("Advertencia", f"Error al obtener la tasa BCV: {error}")
            tasa = None

        if tasa is not None:
            self.current_rate = tasa
            self.label_tasa.configure(text=f"Tasa BCV del día: {tasa:,.2f} Bs/USD")
            return

        self.label_tasa.configure(
            text="Tasa BCV no disponible. Ingresa manualmente al convertir."
        )

    def toggle_tema(self):
        mode = "dark" if self.switch_tema.get() else "light"
        ctk.set_appearance_mode(mode)


def main() -> None:
    app = CalculadoraBCV()
    app.mainloop()


if __name__ == "__main__":
    main()
