import struct

# File paths
input_ply = "scene.ply"
output_ply = "output.ply"

# Number of additional "f_rest_" fields (45 fields)
f_rest_count = 45

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

# Create a new header with the additional fields
new_header = []
for line in header:
    if "property float opacity" in line:
        # Insert the new "f_rest_" fields before "opacity"
        new_header += [f"property float f_rest_{i}" for i in range(f_rest_count)]
    new_header.append(line)

# Write the new PLY file with the additional "f_rest_" fields
with open(output_ply, 'wb') as f:
    # Write the new header
    f.write("\n".join(new_header).encode('utf-8') + b"\n")
    
    # Write the modified vertex data
    for vertex in vertices:
        # Original structure: x, y, z, nx, ny, nz, f_dc_0, f_dc_1, f_dc_2, opacity, scale_0, scale_1, scale_2, rot_0, rot_1, rot_2, rot_3
        # New structure: x, y, z, nx, ny, nz, f_dc_0, f_dc_1, f_dc_2, [f_rest_0...f_rest_43], opacity, scale_0, scale_1, scale_2, rot_0, rot_1, rot_2, rot_3
        new_vertex_data = vertex[:9] + (0.0,) * f_rest_count + vertex[9:]
        f.write(struct.pack("<" + "f" * len(new_vertex_data), *new_vertex_data))

print(f"Conversion complete. New PLY file saved as: {output_ply}")
