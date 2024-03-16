import tkinter as tk
from tkinter import filedialog

# Define the colors
COLORS = {
    'M': 'red',
    'B': 'green',
    'A': 'blue',
    'S': 'gray',
    'T': 'brown',
    'P': 'black',
    'X': 'pink',
    'K': 'yellow',
    'D': 'purple',
    'G': 'cyan',
}

COLOR_NAMES = {
    'red': 'Muro (rojo)',
    'green': 'Bosque (verde)',
    'blue': 'Agua (azul)',
    'gray': 'Suelo pedregoso (gris)',
    'brown': 'Suelo arenoso (marrón)',
    'black': 'Precipicio (negro)',
    'pink': 'Recarga (rosa)',
    'yellow': 'Bikini (amarillo)',
    'purple': 'Zapatillas (morado)',
    'cyan': 'Posicionamiento (cian)',
}

class MatrixEditor(tk.Tk):
    def __init__(self, matrix):
        super().__init__()
        self.title("Belkan Editor")
        self.matrix = matrix
        self.rows = len(matrix)
        self.cols = len(matrix[0])
        self.cell_size = 20
        self.selected_color = tk.StringVar()
        self.selected_color.set('gray')  # Default color for painting
        self.is_drawing = False

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        if screen_width / screen_height > self.cols / self.rows:
            width = int(screen_height * self.cols / self.rows * 0.8)
            height = int(screen_height * 0.8)
        else:
            width = int(screen_width * 0.8)
            height = int(screen_width * self.rows / self.cols * 0.8)

        self.geometry(f"{width}x{height}+{int((screen_width - width) / 2)}+{int((screen_height - height) / 2)}")


        self.canvas = tk.Canvas(self, bg='white', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.draw_matrix()

        # Menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.color_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Colors', menu=self.color_menu)
        for color, color_name in zip(COLORS.values(), COLOR_NAMES.values()):
            self.color_menu.add_command(label=color_name, command=lambda c=color: self.select_color(c))

        self.save_button = tk.Button(self, text="Save", command=self.save_map)
        self.save_button.pack()

        # Mouse events
        self.canvas.bind('<Button-1>', self.start_drawing)
        self.canvas.bind('<B1-Motion>', self.paint_pixel)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drawing)

        # Resize event
        self.bind("<Configure>", self.on_resize)

    def draw_matrix(self):
        self.canvas.delete('pixel')
        cell_width = self.canvas.winfo_width() // self.cols
        cell_height = self.canvas.winfo_height() // self.rows

        for y in range(self.rows):
            for x in range(self.cols):
                color = COLORS.get(self.matrix[y][x], 'white')
                self.canvas.create_rectangle(x * cell_width, y * cell_height,
                                             (x + 1) * cell_width, (y + 1) * cell_height,
                                             fill=color, outline='', tags='pixel')

    def select_color(self, color):
        self.selected_color.set(color)

    def start_drawing(self, event):
        self.is_drawing = True
        self.paint_pixel(event)

    def stop_drawing(self, event):
        self.is_drawing = False

    def paint_pixel(self, event):
        if self.is_drawing:
            x = event.x // (self.canvas.winfo_width() // self.cols)
            y = event.y // (self.canvas.winfo_height() // self.rows)
            color = self.selected_color.get()
            if 0 <= x < self.cols and 0 <= y < self.rows:
                self.matrix[y][x] = next(key for key, value in COLORS.items() if value == color)
                self.draw_matrix()

    def save_map(self):
        filename = filedialog.asksaveasfilename(defaultextension=".map",
                                                filetypes=(("Map files", "*.map"), ("All files", "*.*")))
        if filename:
            with open(filename, 'w') as f:
                f.write(f"{self.rows}\n")
                f.write(f"{self.cols}\n")
                for row in self.matrix:
                    f.write(''.join(row) + '\n')
            print("Map saved successfully.")

    def on_resize(self, event):
        self.draw_matrix()

def read_matrix_from_file(filename):
    matrix = []
    with open(filename, 'r') as f:
        rows = int(f.readline())
        cols = int(f.readline())
        for _ in range(rows):
            matrix.append(list(f.readline().strip()))
    return matrix

if __name__ == "__main__":
    filename = filedialog.askopenfilename(filetypes=(("Map files", "*.map"), ("All files", "*.*")))
    if filename:
        matrix = read_matrix_from_file(filename)
        editor = MatrixEditor(matrix)
        editor.mainloop()
