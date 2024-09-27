import bpy, bmesh
import numpy as np
import timeit
import os

class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.coords = np.array([float(x), float(y), float(z)])
        self.x = self.coords[0]
        self.y = self.coords[1]
        self.z = self.coords[2]

    def xyz(self):
        return tuple(self.coords)
    
    def __add__(self, other):
        return Vec3(*(self.coords + other.coords))

    def __sub__(self, other):
        return Vec3(*(self.coords - other.coords))

    def __truediv__(self, scalar):
        return Vec3(*(self.coords / scalar))
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):  
            return Vec3(*(self.coords * other))
        return Vec3(*(self.coords * other.coords))
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __repr__(self):
        return f"Vec3({self.coords[0]}, {self.coords[1]}, {self.coords[2]})"


class Box:
    def __init__(self, pos: Vec3, size: Vec3):        
         self.pos = pos
         self.size = size
         self.verts = self._calc_verts()
         self.faces = np.array([
            (0, 1, 3, 2),  # Front face
            (4, 6, 7, 5),  # Back face
            (0, 2, 6, 4),  # Top face
            (1, 5, 7, 3),  # Bottom face
            (0, 4, 5, 1),  # Right face
            (2, 3, 7, 6)   # Left face
        ])
                 
    def create(self):
        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', 
            location=self.pos.xyz(), 
            scale=self.size.xyz())
            
    def _calc_verts(self):
        new_pos = self.pos - (self.size/2)
        
        verts = []
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    verts.append((
                        new_pos.x + i * self.size.x*2,
                        new_pos.y + j * self.size.y*2,
                        new_pos.z + k * self.size.z*2
                    ))
                    
        return verts

def sub_devide_box(pos, size):  
    boxes = []
    
    # Loop through all the possible x,y,z positions of the smaller boxes
    for x in range(-1, 2, 1):
        for y in range(-1, 2, 1):
            for z in range(-1, 2, 1):
                # Check if the box is in the middel
                if (abs(x) + abs(y) + abs(z)) <=1:
                    continue
                
                new_size = size/3
                b_index = Vec3(x,y,z)
                new_pos = pos + (b_index * new_size * 2)
                # Add the box to the list
                boxes.append(Box(new_pos, new_size))
                
    return boxes
      
          
def create_mesh(boxes):
    verts = []
    faces = []
    
    # Iterate through each box and collect vertices and face indices
    for b in boxes:
        start_index = len(verts)  # Calculate the starting index for this box
        verts.extend(b.verts)  # Add the vertices of the current box
        faces.extend([(face[0] + start_index, 
                       face[1] + start_index,
                       face[2] + start_index, 
                       face[3] + start_index) for face in b.faces])
                       
    # Create a new mesh and object
    mesh = bpy.data.meshes.new(name="CustomMesh")
    obj = bpy.data.objects.new(name="CustomObject", object_data=mesh)

    # Link the object to the collection
    bpy.context.collection.objects.link(obj)

    # Set the object as the active object and select it
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Create the mesh from the given vertices and faces
    mesh.from_pydata(list(verts), [], list(faces))

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Select all vertices in the mesh
    bpy.ops.mesh.select_all(action='SELECT')

    # Remove double vertices
    bpy.ops.mesh.remove_doubles()

    # Update the mesh with new data
    mesh.update()

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def menger_sponge(n, box):
    start_time = timeit.default_timer()
    boxes = [box] 
    
    for _ in range(n):
        new_boxes = [] 
        for b in boxes:
            new_boxes += sub_devide_box(b.pos, b.size)
        boxes = new_boxes
    
    print(f"A menger sponge of {n} iterations:")  
    print(f"Time to calculate the menger sponge = {timeit.default_timer() - start_time}s") 
      
    amount_boxes = len(boxes)
    print(f"amount of boxes = {amount_boxes}")
    print(f"Vertecis created = {amount_boxes*8}")
    
    start_time = timeit.default_timer()
    
    create_mesh(boxes)
    print(f"Time to create the menger sponge = {timeit.default_timer() - start_time}s")
               
# clear the console
#os.system('cls' if os.name=='nt' else 'clear')


#bpy.ops.object.select_all(action='SELECT')
#bpy.ops.object.delete(use_global=False)

size_box = 1
menger_sponge(4, Box(Vec3(), Vec3(size_box,size_box,size_box)))
