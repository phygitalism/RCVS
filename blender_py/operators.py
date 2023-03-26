import bpy
import os
import os.path
import traceback

from . funcs import *


class RCVS_calculate(bpy.types.Operator):

    """Calculate RCVS descriptors for every OBJ in Library.\nThis may take time"""
    bl_idname = 'rcvs.calculate'
    bl_label = 'Calculate'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        base_dir = bpy.path.abspath(bpy.context.scene.rcvs.obj_path)
        files2import = findFiles(base_dir, ".obj")
        size = bpy.context.scene.rcvs.rays_enum
        totalCount = 0
        convertedCount = 0

        for filePath in files2import:
            totalCount += 1
            try:
                bpy.ops.import_scene.obj(filepath=filePath)
                bpy.ops.object.select_all(action="SELECT")
                obj = bpy.context.selected_objects[0]
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.join()

                obj.select_set(True)
                obj_prepare()
                write_rays(filePath, size,
                           bpy.context.scene.rcvs.obj_path, False)
                obj.select_set(True)
                bpy.ops.object.delete()

                for block in bpy.data.meshes:
                    if block.users < 1:
                        bpy.data.meshes.remove(block)
                convertedCount += 1

            except RuntimeError:
                print(traceback.format_exc())
        print("Converted", convertedCount, "/", totalCount)

        return {'FINISHED'}


class RCVS_search(bpy.types.Operator):
    """Search for similar objects within Library for Active Object"""
    bl_idname = 'rcvs.search'
    bl_label = 'Search'
    bl_options = {'INTERNAL'}

    def execute(self, context):
        print("*********")
        _EXECUTABLE_NAME = "rcvs_compare"

        if sys.platform == "win32":
            _EXECUTABLE_NAME += ".exe"

        base_dir = bpy.path.abspath(bpy.context.scene.rcvs.obj_path)
        rays = bpy.context.scene.rcvs.rays_enum
        length = bpy.context.scene.rcvs.nearest

        obj = bpy.context.active_object
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)

        temp_descriptor = os.path.join(
            base_dir, "RCVS_DATA", "temp_descriptor")

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked": False})
        obj_dupl = bpy.context.active_object

        obj_prepare()
        write_rays(temp_descriptor, rays,
                   bpy.context.scene.rcvs.obj_path, True)

        obj_dupl.select_set(True)
        bpy.ops.object.delete()

        for block in bpy.data.meshes:
            if block.users < 1:
                bpy.data.meshes.remove(block)

        # run comparison program written in Rust
        addon_dir = os.path.dirname(os.path.realpath(__file__))

        args = [os.path.join(addon_dir, _EXECUTABLE_NAME),
                os.path.join(bpy.path.abspath(bpy.context.scene.rcvs.obj_path), "RCVS_DATA"), rays]
        popen = subprocess.Popen(args)
        popen.wait()

        objs_to_load = readResults(base_dir, rays, length)
        loadResults(objs_to_load, base_dir, obj.location, obj.dimensions)

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # if os.path.isfile(temp_path):
        # os.remove(temp_path)

        return {'FINISHED'}
