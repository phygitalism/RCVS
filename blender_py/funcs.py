import csv
import os
import os.path
import subprocess
import time
from math import sqrt
import traceback
import sys

import bpy
import mathutils

# Find files with target extension


def findFiles(startDir, extension):
    foundFiles = []
    foundCount = 0
    for current_dir, dirs, files in os.walk(startDir):
        for file in files:
            curExt = os.path.splitext(file)[1]
            if curExt.lower() == extension.lower():
                foundCount += 1
                foundFiles.append(os.path.join(current_dir, file))

    print("Found", foundCount, extension)
    return foundFiles


# Cast rays on target object
def icoRC(icosubd, rad, raydist, normals, target):
    bpy.ops.mesh.primitive_ico_sphere_add(
        radius=rad, subdivisions=icosubd, enter_editmode=True, location=(0, 0, 0))
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
            length = sqrt((start[0]-ray[1][0]) ** 2 + (start[1] -
                                                       ray[1][1]) ** 2 + (start[2]-ray[1][2]) ** 2)
            rays.append(length / (rad * 2))
        else:
            rays.append(-1)

    result = []
    # Combine opposite rays using CSV dicts
    dictdir = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "ico_dicts")

    with open(os.path.join(dictdir, f"{size}.csv"), newline='') as csvfile:
        ico_dict_file = csv.reader(csvfile, delimiter=',')
        for row in ico_dict_file:
            result.append([rays[int(row[0])], rays[int(row[1])]])

    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[ico.name].select_set(True)
    bpy.ops.object.delete()

    return result


# Prepare object for raycasting
def obj_prepare():
    obj = bpy.context.active_object
    if obj.type == 'MESH':
        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True)
        bpy.ops.object.origin_set(
            type='ORIGIN_CENTER_OF_VOLUME', center='MEDIAN')
        max_dist = 0.0000000001
        bb = bpy.data.objects[obj.name].bound_box

        for vert in obj.data.vertices:
            dist = vert.co[0]**2 + vert.co[1]**2 + vert.co[2]**2
            if dist > max_dist:
                max_dist = dist

        obj.scale *= (1 / sqrt(max_dist))
        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True)


# Cast rays and write descriptors
def write_rays(filepath, dir, target_dir, temp):
    icodict = {"80": 2, "320": 3, "1280": 4, "5120": 4}
    icosubd = icodict[dir]
    radius = 1
    for obj in bpy.context.selected_objects:
        if obj.type != "MESH":
            continue
        # bpy.ops.object.location_clear(clear_delta=False)

        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True)

        # Cast rays on object with normals turned inside
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.object.editmode_toggle()
        result1 = icoRC(icosubd, radius, radius*2, True, obj)

        # Cast rays on object with normals turned outside
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        result2 = icoRC(icosubd, radius, radius*2, True, obj)

        final = []
        # Sort sub-lists and append them to main list
        for i in range(len(result1)):
            if result2[i][0] < result2[i][1]:
                final.append([result2[i][0], result2[i][1],
                              result1[i][0], result1[i][1]])
            else:
                final.append([result2[i][1], result2[i][0],
                              result1[i][1], result1[i][0]])

        basedir = os.path.join(bpy.path.abspath(target_dir), "RCVS_DATA", dir)

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        if temp == False:
            obj_name = str(time.time_ns())
            descriptor_path = os.path.join(basedir, obj_name)
        else:
            descriptor_path = os.path.join(bpy.path.abspath(
                target_dir), "RCVS_DATA", "temp_descriptor")

        with open(descriptor_path, "w") as descriptor:
            # Sort list by first values in sub-lists
            final.sort(key=lambda x: x[0])

            # Writing to file
            for ray in final:
                ray_str = ""
                for dist in ray:
                    ray_str += str(dist) + " "
                descriptor.write(ray_str + "\n")

        if temp == False:
            orig_dir = os.path.join(bpy.path.abspath(target_dir), "RCVS_DATA")
            if not os.path.exists(orig_dir):
                os.makedirs(orig_dir)
            with open(os.path.join(orig_dir, dir + "_paths"), "a") as fileWriter:
                fileWriter.write(
                    obj_name + ", " + os.path.relpath(filepath, bpy.path.abspath(target_dir)) + "\n")


# Read results of comparison and find corresponding files.
def readResults(base_dir, rays, length):
    foundFiles = []
    dict_path = os.path.join(base_dir, "RCVS_DATA", rays + "_paths")
    result_path = os.path.join(base_dir, "RCVS_DATA", "temp_result")
    print(dict_path)
    if not os.path.isfile(dict_path):
        return foundFiles

    top_list = {}
    with open(result_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        i = 0
        for row in reader:
            top_list[row[0].strip()] = row[1].strip()
            i += 1
            if i >= length:
                break

    top_len = len(top_list)

    with open(dict_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        found = 0
        for row in reader:
            if row[0] in top_list.keys():
                foundFiles.append([row[0], row[1].strip(), top_list[row[0]]])
                found += 1
            if found >= top_len:
                break

    foundFiles.sort(key=lambda x: x[2])
    foundFiles.reverse()

    return foundFiles


# Load result OBJs to scene.
def loadResults(objs_to_load, base_dir, loc, dims):
    posX = loc[0]
    posY = loc[1]
    posZ = loc[2]
    dimMax_orig = max(dims)
    dimMax = max(dims)

    i = 1
    for result_obj in objs_to_load:
        try:
            posX += dimMax_orig * 1.1
            file_path = base_dir + result_obj[1]
            bpy.ops.import_scene.obj(filepath=file_path)
            obj = bpy.context.selected_objects[0]
            bpy.context.view_layer.objects.active = obj
            if len(bpy.context.selected_objects) > 1:
                bpy.ops.object.join()
            obj.select_set(True)
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            obj.name = "RCVS_" + str(i) + "_" + result_obj[2]

            obj_scale = dimMax_orig / max(obj.dimensions)
            obj.scale = [obj_scale, obj_scale, obj_scale]
            dimMax = max(obj.dimensions)
            obj.location = [posX, posY, posZ]
            obj.select_set(False)
            i += 1
        except RuntimeError:
            pass
