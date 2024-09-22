# Visualisierung der GS_ICP_SLAM Ergebnisse

## PLY-Converter

Die PLY Files, die der GS_ICP_SLAM ausgibt, sind nicht mit den Gaussing/PLY Plugins von Blender und Unity kompatibel und müssen daher angepasst werden. Das Format der GS_ICP_SLAM PLY Files muss in ein gültiges Format konvertiert werden. Dazu haben wir den [PLY-Converter](./ply_converter.py) geschrieben. Dieser wandelt die GS_ICP_SLAM PLY Files in ein gültiges Format für Blender oder Unity um.

### GS_ICP_SLAM PLY Format

Der GS_ICP_SLAM gibt als Output die PLY Files in folgendem Format aus:

```
ply
format binary_little_endian 1.0
element vertex 1719756
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float f_dc_0
property float f_dc_1
property float f_dc_2
property float opacity
property float scale_0
property float scale_1
property float scale_2
property float rot_0
property float rot_1
property float rot_2
property float rot_3
end_header
```

### Blender PLY Format

Das [Import-PLY-As-Verts](https://github.com/TombstoneTumbleweedArt/import-ply-as-verts) Addon in Blender, mit dem wir PLY Files in Blender importieren können, erwartet folgendes PLY Format:

```
ply
format binary_little_endian 1.0
element vertex 1719756
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
property float nx
property float ny
property float nz
end_header
```

Mit dem [PLY-Converter](./ply_converter.py) wird der Header entsprechend angepasst und die Farbwerte der einzelnen Vertices auf einen Bereich von 0 bis 255 skaliert und in uchar-Werte umgewandelt.

### Unity PLY Format

Das [UnityGaussianSplatting](https://github.com/aras-p/UnityGaussianSplatting) Package in Unity, mit dem Gaussians in Unity gerendert werden können, erwartet folgendes PLY Format:

```
ply
format binary_little_endian 1.0
element vertex 1719756
property float x
property float y
property float z
property float nx
property float ny
property float nz
property float f_dc_0
property float f_dc_1
property float f_dc_2
property float f_rest_0
...
property float f_rest_44
property float opacity
property float scale_0
property float scale_1
property float scale_2
property float rot_0
property float rot_1
property float rot_2
property float rot_3
end_header
```

Das Package erwartet f_rest properties von 0 bis 45 für jeden Vertex. Der [PLY-Converter](./ply_converter.py) passt den Header entsprechend an und fügt bei allen Vertices die 45 f_rest properties mit dem initialen Wert 0.0 hinzu.

## Blender

### Setup

Software:
- Blender 4.1.1

Addons:
- [Import-PLY-As-Verts](https://github.com/TombstoneTumbleweedArt/import-ply-as-verts)

### Vorgehen

1. Importieren von PLY Files in Blender
   - Zunächst musste ein Weg gefunden werden, PLY Files in Blender zu importieren --> [Import-PLY-As-Verts](https://github.com/TombstoneTumbleweedArt/import-ply-as-verts) Addon.
   - Die GS_ICP_SLAM PLY haben mit dem Addon nicht funktioniert, da das Addon ein anderes PLY Format erwartet.
   - Mit dem [PLY-Converter](#ply-converter) werden die PLY Files nun in das erwartete Format konvertiert und können in Blender importiert werden.
   - Die Gaussians werden in Blender als Vertices importiert/repräsentiert.
2. Rendern von Gaussians/Vertices

   Die Vertices können mit zwei verschieden Methoden gerendert werden:

   **Render as Point Cloud**

    - Vertices werden als Points gerendert.
    - Farbe der Points werden durch die Farbattribute der jeweiligen Vertices festgelegt.
    - Diese Methode ist effizienter, da keine wirkliche Geometrie/Mesh erzeugt wird. Allerdings kann so die Punktwolke nicht im Viewport gerendert werden.

   **Instancing**

   - Vertices werden als Mesh gerendert.
   - Für jeden Vertex ein Cube(Würfel) instanziiert.
   - Farbe der Cubes werden durch die Farbattribute der jeweiligen Vertices festgelegt.
   - Diese Methode ist rechenintensiver, allerdings können die Vertices/Cubes auch im Viewport gerendert werden.

3. Rendern der GS_ICP_SLAM Ergebnisse
   - Zunächst wurden für das TUM und das REPLICA Datenset die Ergebnisse des GS_ICP_SLAM in Blender mit beiden Methoden gerendert

### Ergebnisse



## Unity VR

### Setup

Software:
- Unity Editor 2022.3.7f1 (Built-in Render Pipeline)
- Meta Quest Link

Packages:
- [UnityGaussianSplatting](https://github.com/aras-p/UnityGaussianSplatting)

Hardware:
- Quest 3

### Vorgehen

1. Unity VR Template
   - 
2. Unity URP Projekt
3. Unity Built-in Render Pipeline Projekt

### Ergebnisse

## PLY Files

Die PLY Files sind teilsweise zu groß, um sie in diesem Repo hochladen zu können. Daher können die PLY Files über diesen [Link](https://workupload.com/archive/zUcR5VaSbQ) heruntergeladen werden (Verfügbar bis Ende Oktober 2024, danach wieder auf Anfrage).

## Blender File

Da auch die Blender File durch die importierten PLY Files zu groß ist, um sie in diesem Repo hochladen zu können, kann sie über diesen [Link]() heruntergeladen werden (Verfügbar bis Ende Oktober 2024, danach wieder auf Anfrage)