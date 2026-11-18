"""
Simple calculator with a graphical interface (Tkinter).

Run with:  python calculator.py
Works with the standard library only. Keyboard input is supported too:
digits, + - * / ( ) . %, Enter or = to calculate, Backspace to delete, Esc to clear.
Mehr
"""

import ast
import operator
import tkinter as tk

# Only these operations are allowed, so user input is never executed as Python code.
ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(expression):
    """Evaluate a simple arithmetic expression such as '(2+3)*4'."""

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
            return ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPS:
            return ALLOWED_OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Invalid expression")

    return _eval(ast.parse(expression, mode="eval"))


def format_result(value):
    """Show whole numbers without '.0' and limit long decimals."""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.10g}"
    return str(value)


class CalculatorApp(tk.Tk):
    BG = "#1e1e2e"
    DISPLAY_BG = "#11111b"
    DISPLAY_FG = "#cdd6f4"
    NUMBER_BG = "#45475a"
    OPERATOR_BG = "#fab387"
    CLEAR_BG = "#f38ba8"
    EQUAL_BG = "#a6e3a1"
    TEXT_DARK = "#1e1e2e"
    TEXT_LIGHT = "#cdd6f4"

    BUTTONS = [
        ["C", "DEL", "(", ")"],
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "%", "+"],
        ["="],
    ]

    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(bg=self.BG)
        self.resizable(False, False)

        self.expression = tk.StringVar(value="0")
        self.just_evaluated = False

        self._build_display()
        self._build_buttons()
        self.bind("<Key>", self._on_key)

    # ----- layout -------------------------------------------------------
    def _build_display(self):
        display = tk.Entry(
            self,
            textvariable=self.expression,
            font=("Segoe UI", 26),
            justify="right",
            bd=0,
            bg=self.DISPLAY_BG,
            fg=self.DISPLAY_FG,
            insertbackground=self.DISPLAY_FG,
            readonlybackground=self.DISPLAY_BG,
            state="readonly",
        )
        display.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=10, pady=(10, 5), ipady=12)

    def _build_buttons(self):
        for r, row in enumerate(self.BUTTONS, start=1):
            col = 0
            for label in row:
                span = 4 if label == "=" else 1
                btn = tk.Button(
                    self,
                    text=label,
                    font=("Segoe UI", 16, "bold"),
                    bd=0,
                    height=2,
                    width=5,
                    cursor="hand2",
                    command=lambda key=label: self.on_press(key),
                    **self._button_colors(label),
                )
                btn.grid(row=r, column=col, columnspan=span, sticky="nsew", padx=4, pady=4)
                col += span

        for c in range(4):
            self.columnconfigure(c, weight=1)

    def _button_colors(self, label):
        if label == "=":
            return {"bg": self.EQUAL_BG, "fg": self.TEXT_DARK, "activebackground": self.EQUAL_BG}
        if label in ("C", "DEL"):
            return {"bg": self.CLEAR_BG, "fg": self.TEXT_DARK, "activebackground": self.CLEAR_BG}
        if label in ("/", "*", "-", "+", "%"):
            return {"bg": self.OPERATOR_BG, "fg": self.TEXT_DARK, "activebackground": self.OPERATOR_BG}
        return {"bg": self.NUMBER_BG, "fg": self.TEXT_LIGHT, "activebackground": self.NUMBER_BG}

    # ----- behaviour ----------------------------------------------------
    def on_press(self, key):
        current = self.expression.get()

        if key == "C":
            self._set("0")
            return
        if key == "DEL":
            self._set(current[:-1] or "0")
            return
        if key == "=":
            self._calculate()
            return

        if self.just_evaluated:
            # After a result: a number starts a new calculation, an operator continues with the result.
            if key.isdigit() or key == ".":
                current = "0"
            self.just_evaluated = False

        if key == "%":
            key = "/100"

        if current == "0" and key.isdigit():
            self._set(key)
        elif current == "0" and key not in (".", ")"):
            self._set(key)
        else:
            self._set(current + key)

    def _calculate(self):
        expr = self.expression.get()
        try:
            result = safe_eval(expr)
            self._set(format_result(result))
        except ZeroDivisionError:
            self._set("Cannot divide by zero")
        except (ValueError, SyntaxError, TypeError, OverflowError):
            self._set("Error")
        self.just_evaluated = True

    def _set(self, text):
        self.expression.set(text)

    def _on_key(self, event):
        mapping = {
            "Return": "=",
            "KP_Enter": "=",
            "BackSpace": "DEL",
            "Escape": "C",
            "Delete": "C",
        }
        if event.keysym in mapping:
            self.on_press(mapping[event.keysym])
        elif event.char in "0123456789.+-*/()%":
            self.on_press(event.char)
        elif event.char == "=":
            self.on_press("=")


if __name__ == "__main__":
    CalculatorApp().mainloop()
