# schlechte Scans lesbar machen

pip install Pillow

pip install pdf2image

Zum erstellen der exe Datei

pip install pyinstaller

pyinstaller --clean -w --add-data "C:\Users\axell\source\Bildprozessor_Pro\poppler\Library;poppler_bin" Bildprozessor_Pro.py

Im Ordner dist\Bildprozessor_Pro liegt die Bildprozessor_Pro.exe Datei zum ausführen. Den Ordner _internal braucht das Programm zum arbeiten.

Im vor dem ersteller einer neuen Exe Datei den dist Ordner löschen
