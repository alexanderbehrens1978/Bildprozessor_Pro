from PIL import Image, ImageDraw

def create_multi_size_icon(filename="bildprozessor_pro.ico", base_size=(256, 256)):
    # Erstelle ein Basisbild in der Größe base_size (hier 256x256)
    base = Image.new("RGB", base_size, "white")
    draw = ImageDraw.Draw(base)
    # Zeichne auf die rechte Hälfte ein schwarzes Rechteck
    draw.rectangle((base_size[0] // 2, 0, base_size[0], base_size[1]), fill="black")
    # Speichere das Bild als ICO-Datei mit mehreren Größen
    base.save(filename, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])

if __name__ == "__main__":
    create_multi_size_icon()
    print("Icon-Datei 'bildprozessor_pro.ico' wurde erstellt.")
