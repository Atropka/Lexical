import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import re

# Определяем типы токенов
TOKEN_TYPES = [
    ('FLOAT', r'\d+(\.\d+)?([eE][+-]?\d+)?'),  # Числа с плавающей точкой
    ('IDEN', r'([A-Za-z_][A-Za-z0-9_]*)'),  # Идентификаторы
    ('ASSIGN', r':='),  # Знак присваивания
    ('ADD', r'\+'),  # Оператор сложения
    ('SUB', r'-'),  # Оператор вычитания
    ('MUL', r'\*'),  # Оператор умножения
    ('DIV', r'/'),  # Оператор деления
    ('LPAREN', r'\('),  # Левая круглая скобка
    ('RPAREN', r'\)'),  # Правая круглая скобка
    ('SEMICOLON', r';'),  # Точка с запятой
    ('WHITESPACE', r'\s+'),  # Пробелы, табуляция, новые строки (игнорируем)
    ('COMMENTS', r'#([A-Za-z_][A-Za-z0-9_]*)')  # Комментарии
]

# Объединяем регулярные выражения в одно
TOKEN_REGEX = '|'.join(f'(?P<{token_type}>{pattern})' for token_type, pattern in TOKEN_TYPES)
token_regex = re.compile(TOKEN_REGEX)


class LexerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лексический Анализатор Бухтияров_М_А ИС42")

        # Основной фрейм для размещения элементов
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левый фрейм для текстового ввода
        input_frame = tk.Frame(main_frame)
        input_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 5))

        # Правый фрейм для таблицы токенов
        output_frame = tk.Frame(main_frame)
        output_frame.grid(row=0, column=1, sticky="nswe", padx=(5, 0))

        # Настройка текстового поля для ввода
        self.text_input = tk.Text(input_frame, height=30, width=50)
        self.text_input.pack(fill=tk.BOTH, expand=True)

        # Кнопки для загрузки файла и анализа
        button_frame = tk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.load_button = tk.Button(button_frame, text="Загрузить файл", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.analyze_button = tk.Button(button_frame, text="Анализировать", command=self.analyze)
        self.analyze_button.pack(side=tk.LEFT, padx=5)

        # Настройка таблицы для отображения токенов
        self.tree = ttk.Treeview(output_frame, columns=('No', 'Наименование', 'Значение'), show='headings')
        self.tree.heading('No', text='Порядковый номер')
        self.tree.heading('Наименование', text='Наименование')
        self.tree.heading('Значение', text='Значение')
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Настройка размеров колонок
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def load_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.text_input.delete(1.0, tk.END)
                self.text_input.insert(tk.END, file.read())

    def analyze(self):
        input_text = self.text_input.get("1.0", tk.END).strip()
        if not self.validate_expressions(input_text):
            return
        tokens = self.lexer(input_text)
        self.display_tokens(tokens)

    def lexer(self, input_text):
        tokens = []
        for match in token_regex.finditer(input_text):
            token_type = match.lastgroup
            token_value = match.group(token_type)
            if token_type != 'WHITESPACE' and token_type != 'COMMENTS':  # Игнорируем пробелы и комментарии
                tokens.append((token_type, token_value))
        return tokens

    def validate_expressions(self, text):
        # Определение шаблонов для недопустимых выражений
        invalid_patterns = [
            (r'\*\*', "Две операции умножения подряд"),
            (r'\.\.', "Две точки в числе"),
            (r'//', "Две операции деления подряд"),
            (r'--', "Два минуса подряд"),
            (r'\+\+', "Два плюса подряд"),
            (r'\(\s*\)', "Пустые круглые скобки"),
            (r'\;\s*\;', "Две точки с запятой подряд"),
            (r'[eE]{2,}', "Некорректное число с экспоненциальной нотацией (двойное e/E)"),
            (r'(?<![eE])\d+\.\d+[eE][-+]?\d*\.\d+', "Некорректное число с плавающей точкой в экспоненциальной части"),
            (r'[eE][-+]{2,}\d+', "Некорректное число с двойным знаком в экспоненциальной части"),
            # (r'(?<!\d)(\d+[A-Za-z_])', "Число перед идентификатором без оператора"),
            (r'[^;]\s*\n', "Отсутствие точки с запятой"),
        ]

        for pattern, error_desc in invalid_patterns:
            match = re.search(pattern, text)
            if match:
                error_text = match.group(0)  # Найденное выражение, вызвавшее ошибку
                for row in self.tree.get_children():
                    self.tree.delete(row)
                messagebox.showerror("Ошибка", f"Неправильное выражение: '{error_text}' — {error_desc}")
                return False
        return True

    def display_tokens(self, tokens):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for idx, (token_type, token_value) in enumerate(tokens, start=1):
            self.tree.insert('', 'end', values=(idx, token_type, token_value))


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = LexerApp(root)
    root.mainloop()
