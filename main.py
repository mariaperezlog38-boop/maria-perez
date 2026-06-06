from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from calculadora_bcv_logic import (
    convert_amount,
    evaluate_expression,
    format_result,
    get_rate_from_pybcv,
    parse_amount,
)


class CalculatorScreen(BoxLayout):
    status_text = StringProperty("Cargando tasa...")

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=12, padding=16, **kwargs)
        Window.clearcolor = (0.95, 0.95, 0.96, 1)

        title = Label(
            text="Conversor Dólar ⇄ Bolívar",
            font_size="26sp",
            size_hint=(1, None),
            height=64,
            color=(0.12, 0.32, 0.56, 1),
        )
        self.add_widget(title)

        self.rate_label = Label(
            text=self.status_text,
            font_size="16sp",
            size_hint=(1, None),
            height=36,
            color=(0.16, 0.16, 0.16, 1),
        )
        self.add_widget(self.rate_label)

        self.input_amount = TextInput(
            hint_text="Monto",
            multiline=False,
            input_filter="float",
            font_size="20sp",
            size_hint=(1, None),
            height=56,
            background_normal="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[12, 12, 12, 12],
        )
        self.input_amount.bind(on_text_validate=self.on_convert)
        self.add_widget(self.input_amount)

        self.input_rate = TextInput(
            hint_text="Tasa BCV (Bs/USD)",
            multiline=False,
            input_filter="float",
            font_size="20sp",
            size_hint=(1, None),
            height=56,
            background_normal="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            padding=[12, 12, 12, 12],
        )
        self.input_rate.bind(on_text_validate=self.on_convert)
        self.add_widget(self.input_rate)

        self.mode_spinner = Spinner(
            text="USD a Bs",
            values=("USD a Bs", "Bs a USD"),
            size_hint=(1, None),
            height=52,
            background_color=(1, 1, 1, 1),
            color=(0, 0, 0, 1),
        )
        self.add_widget(self.mode_spinner)

        buttons_layout = GridLayout(cols=2, size_hint=(1, None), height=56, spacing=10)
        self.btn_convert = Button(
            text="Convertir",
            background_color=(0.16, 0.59, 0.92, 1),
            color=(1, 1, 1, 1),
            on_press=self.on_convert,
        )
        self.btn_clear = Button(
            text="Limpiar",
            background_color=(0.75, 0.75, 0.75, 1),
            color=(0, 0, 0, 1),
            on_press=self.on_clear,
        )
        buttons_layout.add_widget(self.btn_convert)
        buttons_layout.add_widget(self.btn_clear)
        self.add_widget(buttons_layout)

        self.result_label = Label(
            text="",
            font_size="22sp",
            size_hint=(1, None),
            height=72,
            color=(0.1, 0.25, 0.55, 1),
        )
        self.add_widget(self.result_label)

        extra_buttons = GridLayout(cols=2, size_hint=(1, None), height=56, spacing=10)
        self.btn_refresh = Button(
            text="Refrescar Tasa",
            background_color=(0.16, 0.59, 0.40, 1),
            color=(1, 1, 1, 1),
            on_press=self.refresh_rate,
        )
        self.btn_basic_calc = Button(
            text="Calculadora básica",
            background_color=(0.92, 0.59, 0.16, 1),
            color=(1, 1, 1, 1),
            on_press=self.open_calculadora_basica,
        )
        extra_buttons.add_widget(self.btn_refresh)
        extra_buttons.add_widget(self.btn_basic_calc)
        self.add_widget(extra_buttons)

        hint = Label(
            text="Puedes ingresar la tasa manualmente o refrescarla automáticamente.",
            font_size="14sp",
            size_hint=(1, None),
            height=28,
            color=(0.25, 0.25, 0.25, 1),
        )
        self.add_widget(hint)

        self.current_rate = None
        self.refresh_rate()

    def get_selected_rate(self) -> float:
        rate_text = self.input_rate.text.strip()
        if rate_text:
            return parse_amount(rate_text)
        if self.current_rate is not None:
            return self.current_rate
        raise ValueError("Ingresa la tasa BCV o pulsa Refrescar Tasa.")

    def on_convert(self, *args):
        try:
            amount = parse_amount(self.input_amount.text.strip())
        except ValueError as error:
            self.result_label.text = str(error)
            return

        try:
            rate = self.get_selected_rate()
        except ValueError as error:
            self.result_label.text = str(error)
            return

        try:
            result = convert_amount(amount, rate, self.mode_spinner.text)
            self.result_label.text = format_result(result, self.mode_spinner.text)
        except ValueError as error:
            self.result_label.text = str(error)

    def on_clear(self, *args):
        self.input_amount.text = ""
        self.input_rate.text = ""
        self.result_label.text = ""
        self.rate_label.text = self.status_text

    def refresh_rate(self, *args):
        try:
            rate = get_rate_from_pybcv()
        except Exception as error:
            rate = None

        if rate is not None:
            self.current_rate = rate
            self.rate_label.text = f"Tasa BCV del día: {rate:,.2f} Bs/USD"
            return

        self.current_rate = None
        self.rate_label.text = "Tasa BCV no disponible. Ingresa manualmente."

    def open_calculadora_basica(self, *args):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        entry = TextInput(
            text="",
            multiline=False,
            halign="right",
            font_size="32sp",
            size_hint=(1, None),
            height=72,
            background_normal="",
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
        )
        result_label = Label(
            text="",
            font_size="20sp",
            size_hint=(1, None),
            height=40,
            color=(0.12, 0.12, 0.12, 1),
        )
        content.add_widget(entry)
        content.add_widget(result_label)

        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"],
        ]

        grid = GridLayout(cols=4, spacing=8, size_hint=(1, None), height=240)

        def on_button_press(value):
            if value == "=":
                self.compute_basic(entry, result_label)
                return
            entry.text += value

        for row in buttons:
            for value in row:
                btn = Button(text=value, font_size="24sp", on_press=lambda inst, v=value: on_button_press(v))
                grid.add_widget(btn)

        content.add_widget(grid)

        controls = GridLayout(cols=2, spacing=8, size_hint=(1, None), height=48)
        clear_btn = Button(text="C", on_press=lambda inst: self.on_basic_clear(entry, result_label))
        back_btn = Button(text="⌫", on_press=lambda inst: self.on_basic_backspace(entry))
        controls.add_widget(clear_btn)
        controls.add_widget(back_btn)
        content.add_widget(controls)

        popup = Popup(title="Calculadora básica", content=content, size_hint=(0.9, 0.9))
        popup.open()

    def compute_basic(self, entry: TextInput, result_label: Label):
        try:
            value = evaluate_expression(entry.text.strip())
            result_label.text = str(value)
        except Exception as error:
            result_label.text = f"Error: {error}"

    def on_basic_clear(self, entry: TextInput, result_label: Label):
        entry.text = ""
        result_label.text = ""

    def on_basic_backspace(self, entry: TextInput):
        entry.text = entry.text[:-1]


class CalculadoraAndroidApp(App):
    def build(self):
        self.title = "Calculadora BCV"
        return CalculatorScreen()


if __name__ == "__main__":
    CalculadoraAndroidApp().run()
