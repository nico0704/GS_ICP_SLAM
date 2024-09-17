# Projektbeschreibung

## Aufteilung der Aufgaben 
- Algorithmus (Nico, Leon, Johanna)
    - Algorithmus aufsetzen (Nico)
    - eigenen Datensatz erstellen (Leon & Johanna)
    - Algorithmus anpassen für eigenen Datensatz (Nico, Leon & Johanna)
- Blender/Unity (Tim, Alex)

## Vorgehen
1. Aufsetzen des Algorithmus 
- hat einige Probleme an den Hochschulrechnern ergeben
- durch ausprobieren verschiedener Lösungen aber schlussendlich funktioniert, indem "Docker Run"-Befehl angepasst wurde 
- weiteres Problem, dass auch bei jedem Neustart des PCs ein Problem ist, ist dass Grafikkarte nicht auf Docker-Container gefunden wird -> auch hier Lösung gefunden (TODO: Link zur Seite)
2. Austesten des Algorithmus mithilfe der zwei gegebenen Datensätze TUM und REPLICA
- TUM lief problemlos durch, allerdings mit deutlich schlechteren Ergebnisse als in Paper gezeigt
- REPLICA lief gar nicht, da Pfade im Code falsch angegeben waren 
- mehr zu den erzielten Ergebnissen in "Ergebnisse"
3. Kamerakalibrierung
- zunächst versucht eigene Kamerakalibrierung zu Erstellen in Python-Skript [camera_calibrate.py](docker_folder/camera_calibrate.py)
- allerdings später festgestellt, dass die Werte zum Teil nicht stimmen können
- deshalb Kalibrierungsparameter aus Kamera ausgelesen
- dabei aber festgestellt, dass Tiefenwerte nicht angegeben werden können -> allerdings Seite gefunden, auf der 
Angaben zu Tiefenparametern für diese Kamera zu finden sind (TODO: Link zur Seite) 
- auf Basis der Kalibrierungsparameter wird config-Datei erstellt
4. Eigenen Datensatz erstellen
- zum Erstellen des eigenen Datensatz Python-Skript [image_grabber.py](docker_folder/image_grabber.py) erstellt
- mithilfe der "Realsense Depth Camera D435" Datensatz aufgenommen
5. Austesten des Algorithmus auf eigenen Daten
- im Verlauf des Testens festgestellt, dass Algorithmus überhaupt nicht dafür ausgelegt ist, eigene Daten zu verwenden [https://github.com/Lab-of-AI-and-Robotics/GS_ICP_SLAM/issues/36](https://github.com/Lab-of-AI-and-Robotics/GS_ICP_SLAM/issues/36)
- deshalb entsprechenden Code für eigenen Datensatz eingebaut
- dazu wurden folgende Dateien verändert:
    - [gs_icp_slam.py](gs_icp_slam.py)
    - [mp_Mapper.py](mp_Mapper.py)
    - [mp_Tracker.py](mp_Tracker.py)
- eine Anleitung zum Ausführen des Algorithmus auf eigenen Daten befindet sich hier: [README](docker_folder/README.md)
6. Beschreibung der Änderungen
- grundsätzlich sind die Änderungen jeweils unter "custom" zu finden
    1. gs_icp_slam.py
        - [line 77](gs_icp_slam.py#L77)
