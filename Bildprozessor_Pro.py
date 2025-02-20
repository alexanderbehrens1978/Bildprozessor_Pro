import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageOps, ImageChops
import json
import os


class ImageProcessorApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Bildprozessor Pro 20.02.2025 von Alexander Behrens info@alexanderbehrens.com")

		self.create_menu()

		# Variablen initialisieren
		self.original_image = None
		self.processed_image = None
		self.filename = None
		self.layer_vars = []
		# Reduziere die Filteroptionen auf 5
		self.filter_options = ["Blur", "Negativ", "Multiplikation", "Kontrast", "Helligkeit"]

		self.create_widgets()
		self.create_layers_ui()

	def create_menu(self):
		menu_bar = tk.Menu(self.root)
		file_menu = tk.Menu(menu_bar, tearoff=0)
		file_menu.add_command(label="Bild laden", command=self.load_image)
		file_menu.add_command(label="Bild speichern", command=self.save_image)
		file_menu.add_separator()
		file_menu.add_command(label="Einstellungen laden", command=self.load_settings)
		file_menu.add_command(label="Einstellungen speichern", command=self.save_settings)
		file_menu.add_separator()
		file_menu.add_command(label="Beenden", command=self.root.quit)
		menu_bar.add_cascade(label="Datei", menu=file_menu)
		self.root.config(menu=menu_bar)

	def create_widgets(self):
		main_frame = tk.Frame(self.root)
		main_frame.pack(fill=tk.BOTH, expand=True)

		# Linker Bereich für Originalbild
		left_frame = tk.Frame(main_frame)
		left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

		self.filename_label = tk.Label(left_frame, text="Kein Bild geladen", fg="gray")
		self.filename_label.pack(anchor="nw")
		self.left_canvas = self.create_image_canvas(left_frame)

		# Rechter Bereich für bearbeitetes Bild
		right_frame = tk.Frame(main_frame)
		right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
		self.right_canvas = self.create_image_canvas(right_frame)

	def create_image_canvas(self, parent):
		# Rahmen für Canvas und Scrollbars
		frame = tk.Frame(parent)
		frame.pack(fill=tk.BOTH, expand=True)
		canvas = tk.Canvas(frame, bg="white")
		canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
		scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
		scrollbar_y.grid(row=0, column=1, sticky="ns")
		scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
		scrollbar_x.grid(row=1, column=0, sticky="ew")
		canvas.config(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)
		return canvas

	def create_layers_ui(self):
		# Kompakte, horizontale Anordnung der 5 Filter-Steuerungen
		layers_frame = tk.Frame(self.root)
		layers_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

		for i in range(5):
			sub_frame = tk.Frame(layers_frame, borderwidth=1, relief=tk.GROOVE)
			sub_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

			# Überschrift für den Filter
			label = tk.Label(sub_frame, text=f"Filter {i + 1}", font=("Arial", 10, "bold"))
			label.grid(row=0, column=0, columnspan=2, pady=(2, 5))

			# Aktivierungs-Checkbox
			enabled_var = tk.BooleanVar(value=False)
			chk = tk.Checkbutton(sub_frame, variable=enabled_var, command=self.update_image)
			chk.grid(row=1, column=0, sticky="w", padx=5)

			# Filter-Auswahl (Combobox)
			filter_var = tk.StringVar()
			cb = ttk.Combobox(sub_frame, textvariable=filter_var, values=self.filter_options, state="readonly",
							  width=10)
			cb.current(0)
			cb.grid(row=1, column=1, padx=5, pady=2)

			# Schieberegler für Filter-Stärke
			strength_var = tk.DoubleVar(value=1.0)
			slider = tk.Scale(sub_frame, from_=0.1, to=10.0, resolution=0.1, orient=tk.HORIZONTAL,
							  variable=strength_var, command=self.update_image, length=150)
			slider.grid(row=2, column=0, columnspan=2, padx=5, pady=(2, 5))

			self.layer_vars.append((enabled_var, filter_var, strength_var))

	def load_image(self):
		file_path = filedialog.askopenfilename(
			filetypes=[("Bilder", "*.png *.jpg *.jpeg"), ("Alle Dateien", "*.*")]
		)
		if file_path:
			try:
				self.original_image = Image.open(file_path).convert("RGB")
				self.filename = os.path.basename(file_path)
				self.filename_label.config(text=self.filename, fg="black")
				self.show_image(self.original_image, self.left_canvas)
				self.update_image()
			except Exception as e:
				messagebox.showerror("Fehler", f"Konnte Bild nicht laden: {str(e)}")

	def save_settings(self):
		settings = []
		for idx, (enabled_var, filter_var, strength_var) in enumerate(self.layer_vars):
			settings.append({
				"layer": idx + 1,
				"enabled": enabled_var.get(),
				"filter": filter_var.get(),
				"strength": strength_var.get()
			})

		file_path = filedialog.asksaveasfilename(
			defaultextension=".json",
			filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")],
			title="Einstellungen speichern"
		)

		if file_path:
			try:
				with open(file_path, "w") as f:
					json.dump(settings, f, indent=4)
				messagebox.showinfo("Erfolg", "Einstellungen erfolgreich gespeichert.")
			except Exception as e:
				messagebox.showerror("Fehler", f"Speichern fehlgeschlagen: {str(e)}")

	def load_settings(self):
		file_path = filedialog.askopenfilename(
			filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")],
			title="Einstellungen laden"
		)

		if file_path:
			try:
				with open(file_path, 'r') as f:
					settings = json.load(f)

				for setting in settings:
					layer_idx = setting["layer"] - 1
					enabled_var, filter_var, strength_var = self.layer_vars[layer_idx]
					enabled_var.set(setting["enabled"])
					filter_var.set(setting["filter"])
					strength_var.set(setting["strength"])

				messagebox.showinfo("Erfolg", "Einstellungen erfolgreich geladen.")
				self.update_image()
			except Exception as e:
				messagebox.showerror("Fehler", f"Laden fehlgeschlagen: {str(e)}")

	def apply_filter(self, img, filter_name, strength=1.0):
		try:
			if filter_name == "Blur":
				return img.filter(ImageFilter.GaussianBlur(strength))
			elif filter_name == "Negativ":
				return ImageOps.invert(img)
			elif filter_name == "Multiplikation":
				overlay = Image.new("RGB", img.size, (
					int(255 * strength), int(255 * strength), int(255 * strength)
				))
				return ImageChops.multiply(img, overlay)
			elif filter_name == "Kontrast":
				return ImageOps.autocontrast(img, cutoff=strength * 10)
			elif filter_name == "Helligkeit":
				return ImageOps.autocontrast(img, cutoff=strength * 10)
			else:
				return img.copy()
		except Exception as e:
			messagebox.showerror("Fehler", f"Fehler beim Anwenden des Filters: {str(e)}")
			return img.copy()

	def update_image(self, *args):
		if self.original_image:
			img = self.original_image.copy()
			for enabled_var, filter_var, strength_var in self.layer_vars:
				if enabled_var.get():
					img = self.apply_filter(img, filter_var.get(), strength_var.get())
			self.processed_image = img
			self.show_image(img, self.right_canvas)

	def show_image(self, image, canvas):
		canvas.delete("all")
		photo = ImageTk.PhotoImage(image)
		# Zeichne das Bild mit 10 Pixel Abstand (oben und links)
		canvas.create_image(10, 10, image=photo, anchor="nw")
		canvas.image = photo
		width, height = image.size
		canvas.config(scrollregion=(0, 0, width + 20, height + 20))

	def save_image(self):
		if self.processed_image:
			filter_info = []
			for i, (enabled_var, filter_var, strength_var) in enumerate(self.layer_vars):
				if enabled_var.get():
					filter_info.append(f"{i + 1}_{filter_var.get()}_{strength_var.get():.1f}")

			default_name = ""
			if self.filename:
				base = os.path.splitext(self.filename)[0]
				default_name = f"{base}_" + "_".join(filter_info) if filter_info else base

			file_path = filedialog.asksaveasfilename(
				defaultextension=".png",
				filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Alle Dateien", "*.*")],
				title="Bild speichern",
				initialfile=default_name
			)

			if file_path:
				try:
					self.processed_image.save(file_path)
					messagebox.showinfo("Erfolg", "Bild erfolgreich gespeichert.")
				except Exception as e:
					messagebox.showerror("Fehler", f"Speichern fehlgeschlagen: {str(e)}")


if __name__ == "__main__":
	root = tk.Tk()
	app = ImageProcessorApp(root)
	root.mainloop()
