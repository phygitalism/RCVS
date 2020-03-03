import bpy
import os
from math import sqrt
import csv


print("-----START--------")
#Icosphere properties
#icosubd:
#5 -> 5120 X 2 rays
#4 -> 1280 X 2 rays
#3 ->  320 X 2 rays
#2 ->   80 X 2 rays
icosubd = 4
size = 1280 #name of directory
radius = 1




def icoRC(icosubd, rad, raydist, normals, target):
    icorad = rad
    bpy.ops.mesh.primitive_ico_sphere_add(radius=icorad, subdivisions=icosubd, enter_editmode=True, location=(0, 0, 0))
    bpy.ops.mesh.normals_make_consistent(inside=normals)
    bpy.ops.object.editmode_toggle()
    

    ico = bpy.context.active_object
    mesh = bpy.data.meshes[ico.data.name]
    rays = []
    size = len(mesh.polygons)
    for poly in mesh.polygons:
        normal = poly.normal
        start = poly.center
        
        ray = target.ray_cast(start, normal, distance=raydist)
      
        if ray[0] == True:
            length = sqrt((start[0]-ray[1][0]) ** 2 + (start[1]-ray[1][1]) ** 2 + (start[2]-ray[1][2]) ** 2)
            rays.append(length / (radius *2))
        else:
            rays.append(-1)
            
        
    result = []
    #Combine opposite rays using CSV dicts
    dictdir = os.path.dirname(bpy.data.filepath) + "/ico_dicts/"
    with open(dictdir+str(size)+'.csv', newline='') as csvfile:
        ico_dict_file = csv.reader(csvfile, delimiter=',')
        for row in ico_dict_file:
            result.append([rays[int(row[0])], rays[int(row[1])]])
            
            
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[ico.name].select_set(True) 
    bpy.ops.object.delete() 
    
    return result
   
   
    
    
#Batch preparation of objects by scale and origin 
def batch_prepare():   
    for obj in bpy.context.selected_objects:
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        max_dist = 0
        bb = bpy.data.objects[obj.name].bound_box
        
        for vert in obj.data.vertices:
            dist = vert.co[0]**2 + vert.co[1]**2 + vert.co[2]**2
            if dist > max_dist:
                max_dist = dist
        
        obj.scale *= (1 / sqrt(max_dist))



def write_rays(dir):  
    for obj in bpy.context.selected_objects:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        
        #Cast rays on object with normals turned inside   
        bpy.context.view_layer.objects.active  = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.object.editmode_toggle()
        result1 = icoRC(icosubd, radius, radius*2, True, obj)
        
        #Cast rays on object with normals turned outside 
        bpy.context.view_layer.objects.active  = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        result2 = icoRC(icosubd, radius, radius*2, True, obj)
        
        final = []
        #Sort sub-lists and append them to main list
        for i in range(0, len(result1)):
            if result2[i][0] < result2[i][1]:
                final.append([result2[i][0], result2[i][1], result1[i][0], result1[i][1]])
            else:
                final.append([result2[i][1], result2[i][0], result1[i][1], result1[i][0]])
        
        
        
     
        basedir = os.path.dirname(bpy.data.filepath) + "/rays/" + str(size) + "/" 
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        file = open(basedir + "/" + obj.name,"w")
        
        final.sort(key=lambda x: x[0]) #Sort list by first values in sub-lists
     
        #Writing to file   
        for ray in final:
            ray_str = ""
            for dist in ray:   
                ray_str += str(dist) + " "
            file.write(ray_str + "\n")

        file.close()
        
    
    
batch_prepare()
write_rays(size)

print("******finished*****")