# Dokumentation zur Änderung des Algorithmus für eigene Datensätze

## Vorgehen 
1. Aufsetzen des Algorithmus 
    - hat einige Probleme an den Hochschulrechnern ergeben
    - durch ausprobieren verschiedener Lösungen aber schlussendlich funktioniert, indem "Docker Run"-Befehl angepasst wurde 
    - weiteres Problem, dass auch bei jedem Neustart des PCs ein Problem ist, ist dass Grafikkarte nicht auf Docker-Container gefunden wird -> auch hier Lösung gefunden ([Nvidia Developer Forum](https://forums.developer.nvidia.com/t/new-computer-install-gpu-docker-error/266084/6))
2. Austesten des Algorithmus mithilfe der zwei gegebenen Datensätze TUM und REPLICA
    - TUM lief problemlos durch, allerdings mit deutlich schlechteren Ergebnisse als in Paper gezeigt
    - REPLICA lief gar nicht, da Pfade im Code falsch angegeben waren 
    - mehr zu den erzielten Ergebnissen in "Ergebnisse"
3. Kamerakalibrierung
    - zunächst versucht eigene Kamerakalibrierung zu Erstellen in Python-Skript [camera_calibrate.py](docker_folder/camera_calibrate.py)
    - allerdings später festgestellt, dass die Werte zum Teil nicht stimmen können
    - deshalb Kalibrierungsparameter aus Kamera ausgelesen
    - dabei aber festgestellt, dass Tiefenwerte nicht angegeben werden können -> allerdings Seite gefunden, auf der 
    Angaben zu Tiefenparametern für diese Kamera zu finden sind ([Intel real sense support](https://support.intelrealsense.com/hc/en-us/community/posts/360050711414-Does-the-depth-scale-of-the-D435-change-with-each-run-each-frame-or-is-it-fixed)) 
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
        - [traj_utils.py](utils/traj_utils.py)
    - zum Ausführen des eigenen Algorithmus mit Docker wurde der [docker_folder](docker_folder) mit folgenden Änderungen angepasst: 
        - eine Anleitung zum Ausführen des Algorithmus auf eigenen (Live-)Daten befindet sich hier: [README](docker_folder/README.md)
        - das [Dockerfile](docker_folder/Dockerfile) wurde vollständig überarbeitet
        - zum Bauen des Docker-Containers mit funktionierender Rerun-Konfiguration wurde das [run](docker_folder/run.sh)-Skript erstellt
        - zum Installieren der Submodule auf dem Container wurde das [submodules](docker_folder/install_submodules.sh)-Skript erstellt
6. Beschreibung der Änderungen
    - grundsätzlich sind die Änderungen jeweils unter "custom" zu finden
    1. gs_icp_slam.py
        - [line 77](gs_icp_slam.py#L77): da Algorithmus mit ground-truth-Posen arbeitet und diese für custom-Datensatz nicht existiert, daher wird für custom Datensatz eigene "Startpose" verwendet (genauer in traj_utils.py)
        - [line 154](gs_icp_slam.py#L154): Einlesen der Bilder für custom-Datensatz in Funktion "get_test_image"
        - [line 154](gs_icp_slam.py#L238): Auslesen der Bildordner für custom-Datensatz in Funktion "get_image_dirs"
    2. mp_Mapper.py
        - [line 61](mp_Mapper.py#L61): auch hier wird eigene "Startpose" gesetzt, da für eigenen Datensatz keine ground-truth-Posen vorhanden
        - [line 275](mp_Mapper.py#L275): hierbei wurde die Funktion "calc_2d_metric" für das custom-Dataset ausgeschlossen 
        - [line 340](mp_Mapper.py#L340): auch hier werden die Bildordner eingelesen, daher auch hier Funktion "get_image_dirs" für custom-Datensatz angepasst 
    3. mp_Tracker.py
         - [line 57](mp_Tracker.py#L57): auch hier wird eigene "Startpose" gesetzt, da für eigenen Datensatz keine ground-truth-Posen vorhanden
        - [line 335 & 340](mp_Tracker.py#L335): da im eigenen Datensatz keine Daten zur Evaluation vorhanden sind, werden hier die Evaluationsansätze für den custom-Datensatz ausgeschlossen
        - [line 367](mp_Mapper.py#L367): auch hier werden die Bilder eingelesen, daher auch hier Funktion "get_images" für custom-Datensatz angepasst 
    4. traj_utils.py
        - [line 25](utils/traj_utils.py#L25): hier wird die Funktion zum Laden der Posen für den custom-Datensatz aufgerufen
        - [line 65](utils/traj_utils.py#L65): hier werden dann die entsprechenden Posen geladen -> Algorithmus nutzt dazu eigentlich die ground-truth-daten, da es die aber für einen custom Datensatz nicht gibt, wird ein Vektor bestehend aus 1en als Posenliste gesetzt
7. Austesten von TUM mit eigenem Code
    - Code ist grundsätzlich durchgelaufen, aber mit dem eigenen Datensatz keine schönen Ergebnisse geliefert
    - deshalb Code mit TUM-Daten ausprobiert, um zu sehen, ob Code grundsätzlich funktioniert 
    - Ergebnis: liefert das gleiche Ergebnis, wie der eigentliche Algorithmus
8. Nutzung von Live-Daten
    - verschiedene Datensätze aufgenommen und ausprobiert
    - allerdings nie wirklich schönes Ergebnisse
    - deshalb versucht Live-Daten zu nutzen, um direkt sehen zu können, wo Algorithmus scheitert 
    - dazu wurden folgende Dateien erstellt:
        - [mp_Tracker_live.py](mp_Tracker_live.py)
        - [gs_icp_slam_live.py](gs_icp_slam_live.py)
        - [camera.py](camera.py)
9. Verbesserung der Ergebnisse: 
    - Kamerakalibierung angepasst -> zunächst ausgelesenen Werte haben nicht gestimmt 
    - durch GUI von Realsense herausgefunden, dass Tiefenkalibrierungsdaten genutzt werden müssen
    - zusätzlich durch ausprobieren herausgefunden, dass folgende Default-Parameter für Replica optimiert sind [line 245](gs_icp_slam.py#L245)
    - dabei hat Änderung der max_correspondence_distance (von 0.02 auf 0.1) am meisten Verbesserung gebracht
10. Evaluation
    - Replica-Datensätze ausgeführt und mit Ergebnissen des Papers verglichen -> Fazit: Stimmen nahezu überein (detailierte Ergebnisse in [Übersichtsdokument](README_GRUPPE2.md)
    - TUM-Datensätze evaluiert, dabei erst im Nachhinein festgestellt, dass Default-Parameter für TUM in (tum.sh)[tum.sh] stehen -> deshalb unsere Ergebnisse möglicherweise leicht verfälscht
    - für eigene Datensätze ist FPS: 13 -> andere Evaluationswerte nicht möglich, da keine ground-truth-Daten vorhanden   

## Ergebnisse für Custom-Dataset
<img src="3D_Visualization/rerun/gang.gif" width="640" height="480" />
GIF Custom Gang<br><br>
<img src="3D_Visualization/rerun/gang_2.gif" width="640" height="480" />
GIF Custom Gang2<br><br>
