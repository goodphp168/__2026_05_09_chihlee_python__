import tkinter as tk
from tkinter import ttk


class CalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('計算機')
        self.root.resizable(False, False)

        self.expression = ''

        self.create_widgets()

    def create_widgets(self) -> None:
        self.display_var = tk.StringVar(value='0')
        display = ttk.Entry(
            self.root,
            textvariable=self.display_var,
            font=('Segoe UI', 20),
            justify=tk.RIGHT,
            state='readonly',
        )
        display.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=5, pady=5)

        buttons = [
            ('C', 1, 0), ('←', 1, 1), ('%', 1, 2), ('÷', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('×', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('±', 5, 0), ('0', 5, 1), ('.', 5, 2), ('=', 5, 3),
        ]

        for text, row, col in buttons:
            cmd = self.get_command(text)
            btn = ttk.Button(self.root, text=text, command=cmd)
            btn.grid(row=row, column=col, sticky='nsew', padx=2, pady=2, ipadx=10, ipady=10)

        for i in range(6):
            self.root.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)

    def get_command(self, text: str):
        commands = {
            'C': self.clear,
            '←': self.backspace,
            '=': self.calculate,
            '±': self.negate,
        }
        return commands.get(text, lambda t=text: self.append(t))

    def append(self, char: str) -> None:
        operator_map = {'×': '*', '÷': '/'}
        self.expression += operator_map.get(char, char)
        self.display_var.set(self.expression)

    def clear(self) -> None:
        self.expression = ''
        self.display_var.set('0')

    def backspace(self) -> None:
        self.expression = self.expression[:-1]
        self.display_var.set(self.expression or '0')

    def negate(self) -> None:
        if not self.expression or self.expression == '0':
            return
        if self.expression.startswith('-'):
            self.expression = self.expression[1:]
        else:
            self.expression = '-' + self.expression
        self.display_var.set(self.expression)

    def calculate(self) -> None:
        try:
            result = eval(self.expression)
            self.expression = str(result)
            self.display_var.set(self.expression)
        except Exception:
            self.display_var.set('錯誤')
            self.expression = ''


def main():
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
