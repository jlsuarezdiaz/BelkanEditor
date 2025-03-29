import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import matplotlib.colors as mcolors


# Define the colors
COLORS = {
    # 'M': 'red',
    # 'B': 'green',
    # 'A': 'blue',
    # 'S': 'gray',
    # 'C': 'brown',
    # 'P': 'black',
    # 'X': 'pink',
    # 'K': 'yellow',
    # 'D': 'purple',
    # 'G': 'cyan',
    # 'T': 'lightgreen',
    'P': (0.15, 0.15, 0.15),
    'B': (0.0, 1.0, 0.0),
    'C': (0.3, 0.25, 0.2),
    'A': (0.0, 0.0, 1.0),
    'S': (0.6, 0.6, 0.6),
    'M': (0.6, 0.0, 0.0),
    'T': (0.5, 0.8, 0.0),
    'K': (1.0, 1.0, 0.0),
    'D': (0.5, 0.0, 0.5),
    'X': (1.0, 0.0, 1.0),
    'G': (0.0, 1.0, 1.0),
}

COLOR_NAMES = {
    'P': 'Precipicio (negro)',
    'B': 'Bosque (verde)',
    'C': 'Camino (marrón)',
    'A': 'Agua (azul)',
    'S': 'Sendero (gris)',
    'M': 'Obstáculo (rojo)',
    'T': 'Matorral (verde feo)',
    'K': 'Bikini (amarillo)',
    'D': 'Zapatillas (morado)',
    'X': 'Puesto base (magenta)',
    'G': 'Posicionamiento (cyan)'

}

# HEIGHT_SHADES = {}
# for key, color_name in COLORS.items():
#     rgb = mcolors.to_rgb(color_name)  # Convertir el nombre de color a RGB (valores entre 0 y 1)
#     shades = []
#     for i in range(6):
#         factor = 1 + i * 0.1  # Aumentar el brillo según la altura
#         brightened_rgb = tuple(min(1, c * factor) for c in rgb)  # Asegurar que no pase de 1
#         shades.append(mcolors.to_hex(brightened_rgb))  # Convertir de vuelta a hexadecimal
#     HEIGHT_SHADES[color_name] = shades

HEIGHT_SHADES = {}
for key, rgb in COLORS.items():
    shades = []
    for i in range(6):
        # factor = 1 + i * 0.1  # Increase brightness
        factor = 0.5 + (i / 10)
        brightened_rgb = tuple(min(1.0, c * factor) for c in rgb)  # Ensure values stay ≤ 1.0
        hex_color = mcolors.to_hex(brightened_rgb)  # Convert to hex
        shades.append(hex_color)
    hex_base_color = mcolors.to_hex(rgb)  # Convert base RGB to hex
    HEIGHT_SHADES[hex_base_color] = shades  # Store with hex as key



class MatrixEditor(tk.Tk):
    def __init__(self, terrain_matrix, height_matrix):
        super().__init__()
        self.title("Belkan Editor")
        self.terrain_matrix = terrain_matrix
        self.height_matrix = height_matrix
        self.rows = len(terrain_matrix)
        self.cols = len(terrain_matrix[0])
        self.cell_size = 20
        self.selected_color_char = tk.StringVar()
        self.selected_color_char.set('S')
        self.selected_color = tk.StringVar(value='gray')
        self.selected_color.set((0.6, 0.6, 0.6))  # Default color for painting
        self.selected_height = tk.IntVar(value=0)
        self.mode = "color"
        self.show_text = True
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

        # Color menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)
        self.color_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Colors', menu=self.color_menu)
        # for color, color_name in zip(COLORS.values(), COLOR_NAMES.values()):
        #     self.color_menu.add_command(label=color_name, command=lambda c=color: self.select_color(c))
        for char, color in COLORS.items():
            mname = COLOR_NAMES.get(char, char)
            full_name = f"[{char}] {mname}"
            self.color_menu.add_command(label=full_name, command=lambda c=char: self.select_color(c))

        # Height menu
        self.height_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='Heights', menu=self.height_menu)
        for h in range(6):
            self.height_menu.add_command(label=f"Height {h}", command=lambda v=h: self.select_height(v))

        self.toggle_mode_button = tk.Button(self, text="Toggle Mode", command=self.toggle_mode)
        self.toggle_mode_button.pack()
        
        self.toggle_text_button = tk.Button(self, text="Toggle Text", command=self.toggle_text)
        self.toggle_text_button.pack()

        self.save_button = tk.Button(self, text="Save", command=self.save_map)
        self.save_button.pack()

        self.rotate_button = tk.Button(self, text="Rotate 90°", command=self.rotate_matrix)
        self.rotate_button.pack(side=tk.RIGHT)
        
        self.vertical_symmetry_button = tk.Button(self, text="Vertical Symmetry", command=self.vertical_symmetry)
        self.vertical_symmetry_button.pack(side=tk.RIGHT)
        
        self.horizontal_symmetry_button = tk.Button(self, text="Horizontal Symmetry", command=self.horizontal_symmetry)
        self.horizontal_symmetry_button.pack(side=tk.RIGHT)

        self.resize_button = tk.Button(self, text="Resize", command=self.resize_map)
        self.resize_button.pack(side=tk.RIGHT)

        self.fill_with_black_button = tk.Button(self, text="Fill with borders", command=self.fill_with_black)
        self.fill_with_black_button.pack(side=tk.RIGHT)


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
                #base_color = COLORS.get(self.terrain_matrix[y][x], 'white')
                base_color = mcolors.to_hex(COLORS.get(self.terrain_matrix[y][x], (1.0, 1.0, 1.0)))
                shaded_color = HEIGHT_SHADES[base_color][self.height_matrix[y][x]]
                self.canvas.create_rectangle(
                    x * cell_width, y * cell_height,
                    (x + 1) * cell_width, (y + 1) * cell_height,
                    fill=shaded_color, outline='', tags='pixel')
                if self.show_text:
                    self.canvas.create_text(
                        x * cell_width + cell_width//2, y * cell_height + cell_height//2,
                        text=f"{self.terrain_matrix[y][x]}/{self.height_matrix[y][x]}",
                        fill='black', font=('Arial', 10, 'bold')
                    )

    def update_single_cell(self, x, y):
        """Updates only the affected cell instead of redrawing everything."""
        cell_width = self.canvas.winfo_width() // self.cols
        cell_height = self.canvas.winfo_height() // self.rows
        # base_color = COLORS.get(self.terrain_matrix[y][x], 'white')
        base_color = mcolors.to_hex(COLORS.get(self.terrain_matrix[y][x], (1.0, 1.0, 1.0)))
        shaded_color = HEIGHT_SHADES[base_color][self.height_matrix[y][x]]
        
        self.canvas.create_rectangle(
            x * cell_width, y * cell_height,
            (x + 1) * cell_width, (y + 1) * cell_height,
            fill=shaded_color, outline='', tags=f'cell_{x}_{y}'
        )
        
        if self.show_text:
            self.canvas.create_text(
                x * cell_width + cell_width//2, y * cell_height + cell_height//2,
                text=f"{self.terrain_matrix[y][x]}/{self.height_matrix[y][x]}",
                fill='black', font=('Arial', 10, 'bold'), tags=f'text_{x}_{y}'
            )


    def select_color(self, color):
        self.selected_color.set(COLORS[color])
        self.selected_color_char.set(color)
        self.mode = "color"

    def select_height(self, height):
        self.selected_height.set(height)
        self.mode = "height"
    
    def toggle_mode(self):
        self.mode = "height" if self.mode == "color" else "color"

    def toggle_text(self):
        """Alterna la visibilidad de los caracteres en el mapa."""
        self.show_text = not self.show_text
        self.draw_matrix()  # Redibujar el mapa con el nuevo estado

    def start_drawing(self, event):
        self.is_drawing = True
        self.paint_pixel(event)

    def stop_drawing(self, event):
        self.is_drawing = False

    def paint_pixel(self, event):
        if self.is_drawing:
            x = event.x // (self.canvas.winfo_width() // self.cols)
            y = event.y // (self.canvas.winfo_height() // self.rows)
            if 0 <= x < self.cols and 0 <= y < self.rows:
                if self.mode == "color":
                    # self.terrain_matrix[y][x] = next(k for k, v in COLORS.items() if v == self.selected_color.get())
                    self.terrain_matrix[y][x] = self.selected_color_char.get()
                else:
                    self.height_matrix[y][x] = self.selected_height.get()
                # self.draw_matrix()
                self.update_single_cell(x, y)  # 🚀 Update only this cell

    def save_map(self):
        filename = filedialog.asksaveasfilename(defaultextension=".map",
                                                filetypes=(("Map files", "*.map"), ("All files", "*.*")))
        if filename:
            with open(filename, 'w') as f:
                f.write(f"{self.rows}\n")
                f.write(f"{self.cols}\n")
                for row in self.terrain_matrix:
                    f.write(''.join(row) + '\n')
                for row in self.height_matrix:
                    f.write(''.join(map(str, row)) + '\n')
            print("Map saved successfully.")

    def on_resize(self, event):
        self.draw_matrix()

    def rotate_matrix(self):
        self.terrain_matrix = list(zip(*self.terrain_matrix[::-1]))
        self.terrain_matrix = [list(row) for row in self.terrain_matrix]
        self.height_matrix = list(zip(*self.height_matrix[::-1]))
        self.height_matrix = [list(row) for row in self.height_matrix]
        self.rows, self.cols = self.cols, self.rows
        self.draw_matrix()

    def vertical_symmetry(self):
        for row in self.terrain_matrix:
            row[:] = row[::-1]
        for row in self.height_matrix:
            row[:] = row[::-1]
        self.draw_matrix()

    def horizontal_symmetry(self):
        self.terrain_matrix.reverse()
        self.height_matrix.reverse()
        self.draw_matrix()

    def resize_map(self):
        new_rows = simpledialog.askinteger("Resize", "Enter number of rows:")
        if new_rows:
            # new_cols = simpledialog.askinteger("Resize", "Enter number of columns:")
            new_cols = new_rows
            if new_cols:
                old_matrix = self.terrain_matrix
                self.terrain_matrix = [['S'] * new_cols for _ in range(new_rows)]
                for y in range(min(new_rows, self.rows)):
                    for x in range(min(new_cols, self.cols)):
                        self.terrain_matrix[y][x] = old_matrix[y][x]
                old_matrix = self.height_matrix
                self.height_matrix = [[0] * new_cols for _ in range(new_rows)]
                for y in range(min(new_rows, self.rows)):
                    for x in range(min(new_cols, self.cols)):
                        self.height_matrix[y][x] = old_matrix[y][x]
                self.rows = new_rows
                self.cols = new_cols
                self.draw_matrix()

    def fill_with_black(self):
        for y in range(self.rows):
            for x in range(self.cols):
                if y < 3 or y >= self.rows - 3 or x < 3 or x >= self.cols - 3:
                    self.terrain_matrix[y][x] = 'P'
        self.draw_matrix()


def read_matrix_from_file(filename):
    with open(filename, 'r') as f:
        rows = int(f.readline())
        cols = int(f.readline())
        terrain_matrix = [list(f.readline().strip()) for _ in range(rows)]
        
        try:
            height_matrix = [list(map(int, f.readline().strip().strip())) for _ in range(rows)]
            # for row in height_matrix:
            #     print(len(row))
            # Check if the height matrix has the correct dimensions
            if any(len(row) != cols for row in height_matrix):
                raise ValueError
        except ValueError:
            height_matrix = [[0] * cols for _ in range(rows)]
    
    return terrain_matrix, height_matrix

if __name__ == "__main__":
    filename = filedialog.askopenfilename(filetypes=[("Map files", "*.map"), ("All files", "*.*")])
    if filename:
        terrain_matrix, height_matrix = read_matrix_from_file(filename)
        editor = MatrixEditor(terrain_matrix, height_matrix)
        editor.mainloop()
