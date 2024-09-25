import struct

# File paths
input_ply = "scene.ply"
output_ply = "output.ply"

# Number of additional "f_rest_" fields for Unity mode (45 fields)
f_rest_count = 45
# Assumption for the spherical harmonic coefficient of the zeroth order
C0 = 0.28209479177387814

# Mode: either "blender" or "unity"
mode = "blender"  # Change this to "unity" for Unity mode

# Function for calculating RGB values from f_dc_0, f_dc_1, f_dc_2
def calculate_rgb(f_dc_0, f_dc_1, f_dc_2):
    # Calculate R, G, B from the f_dc_ values
    R = 0.5 + C0 * f_dc_0
    G = 0.5 + C0 * f_dc_1
    B = 0.5 + C0 * f_dc_2
    
    # Clamping the values to the range [0, 1]
    R = max(0, min(1, R))
    G = max(0, min(1, G))
    B = max(0, min(1, B))
    
    # Conversion to the range [0, 255]
    R = int(R * 255)
    G = int(G * 255)
    B = int(B * 255)
    
    return R, G, B

# Function to read binary data in Little Endian format
def read_vertex_data(file, vertex_count, vertex_format):
    vertices = []
    for _ in range(vertex_count):
        vertex_data = struct.unpack(vertex_format, file.read(struct.calcsize(vertex_format)))
        vertices.append(vertex_data)
    return vertices

# Open the PLY file and read the header
with open(input_ply, 'rb') as f:
    # Read the header
    header = []
    line = f.readline().decode('utf-8').strip()  # Remove leading/trailing whitespace
    while 'end_header' not in line:  # Check for the 'end_header' marker
        header.append(line)
        line = f.readline().decode('utf-8').strip()
    
    # Add the last 'end_header' line
    header.append(line)
    
    # Extract the number of vertex data entries
    vertex_count = int([line for line in header if "element vertex" in line][0].split()[-1])
    
    # Read the format of the vertex data based on the original structure
    # The original structure is organized as follows:
    # x, y, z, nx, ny, nz, f_dc_0, f_dc_1, f_dc_2, opacity, scale_0, scale_1, scale_2, rot_0, rot_1, rot_2, rot_3
    vertex_format = "<fff fff fff f fff ffff"

    # Read the vertex data
    vertices = read_vertex_data(f, vertex_count, vertex_format)

# Create a new header based on the selected mode
new_header = []
if mode == "blender":
    # Create the new header for Blender mode
    new_header = [
        "ply",
        "format binary_little_endian 1.0",
        f"element vertex {vertex_count}",
        "property float x",
        "property float y",
        "property float z",
        "property uchar red",
        "property uchar green",
        "property uchar blue",
        "property float nx",
        "property float ny",
        "property float nz",
        "end_header"
    ]
elif mode == "unity":
    for line in header:
        if "property float opacity" in line:
            # Insert the new "f_rest_" fields before "opacity" in Unity mode
            new_header += [f"property float f_rest_{i}" for i in range(f_rest_count)]
        new_header.append(line)

# Write the new PLY file with the selected mode changes
with open(output_ply, 'wb') as f:
    # Write the new header
    f.write("\n".join(new_header).encode('utf-8') + b"\n")
    
    if mode == "unity":
        # In Unity mode, we modify the vertex data by adding f_rest_ fields
        for vertex in vertices:
            # Original structure: x, y, z, nx, ny, nz, f_dc_0, f_dc_1, f_dc_2, opacity, scale_0, scale_1, scale_2, rot_0, rot_1, rot_2, rot_3
            # New structure: x, y, z, nx, ny, nz, f_dc_0, f_dc_1, f_dc_2, [f_rest_0...f_rest_43], opacity, scale_0, scale_1, scale_2, rot_0, rot_1, rot_2, rot_3
            new_vertex_data = vertex[:9] + (0.0,) * f_rest_count + vertex[9:]
            f.write(struct.pack("<" + "f" * len(new_vertex_data), *new_vertex_data))
    elif mode == "blender":
        # In Blender mode, convert f_dc_0, f_dc_1, f_dc_2 to RGB (uchar)
        for vertex in vertices:
            # Extract the original float values for f_dc_0, f_dc_1, f_dc_2
            x, y, z = vertex[:3]
            nx, ny, nz = vertex[3:6]
            f_dc_0, f_dc_1, f_dc_2 = vertex[6:9]

            # Convert f_dc_0, f_dc_1, f_dc_2 to uchar (range 0-255)
            red, green, blue = calculate_rgb(f_dc_0, f_dc_1, f_dc_2)

            # Pack the data into the new format (x, y, z, red, green, blue, nx, ny, nz)
            new_vertex_data = (x, y, z, red, green, blue, nx, ny, nz)
            f.write(struct.pack("<fffBBBfff", *new_vertex_data))

print(f"Conversion complete in {mode} mode. New PLY file saved as: {output_ply}")
