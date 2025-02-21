# schlechte Scans lesbar machen

pip install Pillow

pip install pdf2image

![image](https://github.com/user-attachments/assets/36c7908a-8193-4dba-b861-a94dfa493b12)


Zum erstellen der exe Datei

pip install pyinstaller

Das Programm läuft mit beiden Befehlen. Der erste mag für Debug besser sein.

pyinstaller --clean -w --add-data "C:\Users\axell\source\Bildprozessor_Pro\poppler\Library;poppler_bin" --icon=bildprozessor_pro.ico Bildprozessor_Pro.py

pyinstaller --clean -w --add-data "C:\Users\axell\source\Bildprozessor_Pro\poppler\Library;poppler_bin" --icon=bildprozessor_pro.ico Bildprozessor_Pro.py --onefile


Im Ordner dist\Bildprozessor_Pro liegt die Bildprozessor_Pro.exe Datei zum ausführen. Den Ordner _internal braucht das Programm zum arbeiten.

Im vor dem ersteller einer neuen Exe Datei den dist Ordner löschen
