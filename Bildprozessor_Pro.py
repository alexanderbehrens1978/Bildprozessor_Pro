import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk, ImageFilter, ImageOps, ImageChops
from pdf2image import convert_from_path  # Für PDF-Unterstützung
import json
import os
import subprocess
import sys


class ImageProcessorApp:
	def __init__(self, root):
		self.root = root
		self.root.title("Bildprozessor Pro 20.02.2025 von Alexander Behrens info@alexanderbehrens.com")

		# Standardmäßig ist der Poppler-Pfad leer
		self.poppler_path = ""
		# Standardwert für die angezeigte Einstellungsdatei
		self.settings_file_name = "Keine Einstellungen geladen"

		# Versuche, eine settings.json im Programmordner zu laden
		self.load_default_settings()

		self.create_menu()

		# Variablen initialisieren
		self.original_image = None
		self.processed_image = None
		self.filename = None
		self.layer_vars = []
		# Filteroptionen in gewünschter Reihenfolge: 1. Negativ, 2. Multiplikation, 3. Helligkeit
		self.filter_options = ["Negativ", "Multiplikation", "Helligkeit"]

		self.create_widgets()
		self.create_layers_ui()

	def load_default_settings(self):
		prog_path = os.path.dirname(os.path.abspath(__file__))
		settings_file = os.path.join(prog_path, "settings.json")
		if os.path.exists(settings_file):
			try:
				with open(settings_file, "r") as f:
					settings = json.load(f)
				self.poppler_path = settings.get("poppler_path", "")
				self.default_layer_settings = settings.get("layers", [])
				self.settings_file_name = os.path.basename(settings_file)
			except Exception as e:
				messagebox.showerror("Fehler", f"Einstellungen konnten nicht geladen werden: {str(e)}")
		else:
			self.default_layer_settings = []

	def create_menu(self):
		menu_bar = tk.Menu(self.root)

		# Datei-Menü
		file_menu = tk.Menu(menu_bar, tearoff=0)
		file_menu.add_command(label="Bild laden", command=self.load_image)
		file_menu.add_command(label="Bild speichern", command=self.save_image)
		file_menu.add_separator()
		file_menu.add_command(label="Einstellungen laden", command=self.load_settings)
		file_menu.add_command(label="Einstellungen speichern", command=self.save_settings)
		file_menu.add_separator()
		file_menu.add_command(label="Beenden", command=self.root.quit)
		menu_bar.add_cascade(label="Datei", menu=file_menu)

		# Einstellungen-Menü
		settings_menu = tk.Menu(menu_bar, tearoff=0)
		settings_menu.add_command(label="Poppler Pfad setzen", command=self.set_poppler_path)
		settings_menu.add_command(label="Poppler installieren", command=self.install_poppler)
		menu_bar.add_cascade(label="Einstellungen", menu=settings_menu)

		self.root.config(menu=menu_bar)

	def set_poppler_path(self):
		# Standardmäßig wird der Programmordner als initiales Verzeichnis gesetzt
		prog_path = os.path.dirname(os.path.abspath(__file__))
		path = filedialog.askdirectory(title="Wähle den Poppler-Library-Bin-Ordner", initialdir=prog_path)
		if path:
			self.poppler_path = path
			messagebox.showinfo("Poppler Pfad", f"Poppler Pfad gesetzt auf:\n{self.poppler_path}")

	def install_poppler(self):
		try:
			if sys.platform.startswith("win"):
				# Für Windows: Verwende Chocolatey
				try:
					subprocess.check_call(["choco", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
				except Exception:
					self.show_poppler_url()  # Öffnet das Fenster mit auswählbarem Link
					return
				subprocess.check_call(["choco", "install", "poppler", "-y"])
				messagebox.showinfo("Poppler Installation", "Poppler wurde erfolgreich installiert.")
			elif sys.platform.startswith("linux"):
				subprocess.check_call(["sudo", "apt-get", "install", "poppler-utils", "-y"])
				messagebox.showinfo("Poppler Installation", "Poppler wurde erfolgreich installiert.")
			elif sys.platform.startswith("darwin"):
				try:
					subprocess.check_call(["brew", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
				except Exception:
					messagebox.showerror("Fehler",
										 "Homebrew ist nicht installiert.\nBitte installiere Homebrew oder installiere Poppler manuell.")
					return
				subprocess.check_call(["brew", "install", "poppler"])
				messagebox.showinfo("Poppler Installation", "Poppler wurde erfolgreich installiert.")
			else:
				messagebox.showerror("Fehler",
									 "Automatische Installation von Poppler wird für dein Betriebssystem nicht unterstützt. Bitte installiere Poppler manuell.")
		except Exception as e:
			messagebox.showerror("Fehler", f"Fehler bei der Installation von Poppler: {str(e)}")

	def show_poppler_url(self):
		# Neues Fenster mit auswählbarem Text (URL) zur Poppler-Windows-Version
		top = tk.Toplevel(self.root)
		top.title("Poppler Download URL")
		tk.Label(top,
				 text="Chocolatey ist nicht installiert.\nBitte installiere Chocolatey oder installiere Poppler manuell.\nKopiere folgenden Link für den Download:",
				 justify="left").pack(padx=10, pady=10)
		# Entry-Feld mit der URL, damit sie ausgewählt und kopiert werden kann
		url = "https://github.com/oschwartz10612/poppler-windows/releases/"
		entry = tk.Entry(top, width=60)
		entry.insert(0, url)
		entry.pack(padx=10, pady=5)
		tk.Button(top, text="Schließen", command=top.destroy).pack(pady=10)

	def create_widgets(self):
		main_frame = tk.Frame(self.root)
		main_frame.pack(fill=tk.BOTH, expand=True)

		# Top-Bereich: Anzeige von Bilddatei und Einstellungsdatei
		top_frame = tk.Frame(main_frame)
		top_frame.pack(fill=tk.X, padx=10, pady=5)
		self.filename_label = tk.Label(top_frame, text="Kein Bild geladen", anchor="w")
		self.filename_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
		self.settings_label = tk.Label(top_frame, text="Einstellungen: " + self.settings_file_name, anchor="e")
		self.settings_label.pack(side=tk.RIGHT)

		# Vorschaufenster-Bereich
		preview_frame = tk.Frame(main_frame)
		preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		# Linker Bereich für Originalbild
		left_frame = tk.Frame(preview_frame)
		left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.left_canvas = self.create_image_canvas(left_frame)

		# Rechter Bereich für bearbeitetes Bild
		right_frame = tk.Frame(preview_frame)
		right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
		self.right_canvas = self.create_image_canvas(right_frame)

	def create_image_canvas(self, parent):
		frame = tk.Frame(parent)
		frame.pack(fill=tk.BOTH, expand=True)
		# Standardhöhe auf 480 Pixel gesetzt – beide Canvas sind gleich hoch
		canvas = tk.Canvas(frame, bg="white", height=480)
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
		layers_frame = tk.Frame(self.root)
		layers_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

		for i in range(5):
			sub_frame = tk.Frame(layers_frame, borderwidth=1, relief=tk.GROOVE)
			sub_frame.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

			label = tk.Label(sub_frame, text=f"Filter {i + 1}", font=("Arial", 10, "bold"))
			label.grid(row=0, column=0, columnspan=2, pady=(2, 5))

			enabled_var = tk.BooleanVar(value=False)
			chk = tk.Checkbutton(sub_frame, variable=enabled_var, command=self.update_image)
			chk.grid(row=1, column=0, sticky="w", padx=5)

			filter_var = tk.StringVar()
			cb = ttk.Combobox(sub_frame, textvariable=filter_var, values=self.filter_options, state="readonly",
							  width=10)
			cb.current(0)
			cb.grid(row=1, column=1, padx=5, pady=2)

			strength_var = tk.DoubleVar(value=1.0)
			slider = tk.Scale(sub_frame, from_=0.1, to=10.0, resolution=0.1, orient=tk.HORIZONTAL,
							  variable=strength_var, command=self.update_image, length=150)
			slider.grid(row=2, column=0, columnspan=2, padx=5, pady=(2, 5))

			self.layer_vars.append((enabled_var, filter_var, strength_var))

		# Wende Default-Layer-Einstellungen an, falls vorhanden
		if self.default_layer_settings:
			for setting in self.default_layer_settings:
				layer_idx = setting["layer"] - 1
				if layer_idx < len(self.layer_vars):
					enabled_var, filter_var, strength_var = self.layer_vars[layer_idx]
					enabled_var.set(setting.get("enabled", False))
					filter_var.set(setting.get("filter", self.filter_options[0]))
					strength_var.set(setting.get("strength", 1.0))
			self.update_image()

	def load_image(self):
		file_path = filedialog.askopenfilename(
			filetypes=[("Bilder/PDFs", "*.png *.jpg *.jpeg *.pdf"), ("Alle Dateien", "*.*")]
		)
		if file_path:
			try:
				if file_path.lower().endswith(".pdf"):
					if not self.poppler_path:
						messagebox.showerror("Fehler",
											 "Poppler Pfad ist nicht gesetzt. Bitte setze den Poppler Pfad unter 'Einstellungen'.")
						return
					pages = convert_from_path(file_path, dpi=200, poppler_path=self.poppler_path)
					self.original_image = pages[0]
				else:
					self.original_image = Image.open(file_path).convert("RGB")
				self.filename = os.path.basename(file_path)
				self.filename_label.config(text=self.filename)
				self.show_image(self.original_image, self.left_canvas)
				self.update_image()
				# Passe die Höhe des rechten Vorschaubereichs an die des linken an
				self.left_canvas.update_idletasks()
				h = self.left_canvas.winfo_height()
				self.right_canvas.config(height=h)
			except Exception as e:
				messagebox.showerror("Fehler", f"Konnte Bild laden: {str(e)}")

	def save_settings(self):
		settings = {
			"poppler_path": self.poppler_path,
			"layers": []
		}
		for idx, (enabled_var, filter_var, strength_var) in enumerate(self.layer_vars):
			settings["layers"].append({
				"layer": idx + 1,
				"enabled": enabled_var.get(),
				"filter": filter_var.get(),
				"strength": strength_var.get()
			})
		prog_path = os.path.dirname(os.path.abspath(__file__))
		file_path = os.path.join(prog_path, "settings.json")
		try:
			with open(file_path, "w") as f:
				json.dump(settings, f, indent=4)
			self.settings_file_name = os.path.basename(file_path)
			self.settings_label.config(text="Einstellungen: " + self.settings_file_name)
			messagebox.showinfo("Erfolg", "Einstellungen erfolgreich gespeichert.")
		except Exception as e:
			messagebox.showerror("Fehler", f"Speichern fehlgeschlagen: {str(e)}")

	def load_settings(self):
		prog_path = os.path.dirname(os.path.abspath(__file__))
		file_path = filedialog.askopenfilename(
			initialdir=prog_path,
			filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")],
			title="Einstellungen laden"
		)
		if file_path:
			try:
				with open(file_path, 'r') as f:
					settings = json.load(f)
				self.poppler_path = settings.get("poppler_path", "")
				for setting in settings.get("layers", []):
					layer_idx = setting["layer"] - 1
					if layer_idx < len(self.layer_vars):
						enabled_var, filter_var, strength_var = self.layer_vars[layer_idx]
						enabled_var.set(setting.get("enabled", False))
						filter_var.set(setting.get("filter", self.filter_options[0]))
						strength_var.set(setting.get("strength", 1.0))
				self.settings_file_name = os.path.basename(file_path)
				self.settings_label.config(text="Einstellungen: " + self.settings_file_name)
				messagebox.showinfo("Erfolg", "Einstellungen erfolgreich geladen.")
				self.update_image()
			except Exception as e:
				messagebox.showerror("Fehler", f"Laden fehlgeschlagen: {str(e)}")

	def apply_filter(self, img, filter_name, strength=1.0):
		try:
			if filter_name == "Negativ":
				return ImageOps.invert(img)
			elif filter_name == "Multiplikation":
				overlay = Image.new("RGB", img.size, (
					int(255 * strength), int(255 * strength), int(255 * strength)
				))
				return ImageChops.multiply(img, overlay)
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
