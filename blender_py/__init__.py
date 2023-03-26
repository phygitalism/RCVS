import os.path
import sys
import bpy


from . operators import RCVS_calculate, RCVS_search
from . ui import RCVS_Properties, OBJECT_PT_RCVS_Panel_Settings, OBJECT_PT_RCVS_Panel
#from . funcs import *

_EXECUTABLE_NAME = "rcvs_compare"

if sys.platform == "win32":
    _EXECUTABLE_NAME += ".exe"

bl_info = {
    "name": "RCVS",
    "description": "Ray Cast Visual Search. Search for the most similar objects to Active Object in library.",
    "author": "Roman Chumak",
    "version": (0, 0, 1, 1),
    "blender": (2, 80, 0),
    "location": "Properties / Object & Scene",
    "category": "Object"}


def register():
    bpy.utils.register_class(RCVS_Properties)
    bpy.types.Scene.rcvs = bpy.props.PointerProperty(type=RCVS_Properties)
    bpy.utils.register_class(RCVS_calculate)
    bpy.utils.register_class(RCVS_search)
    bpy.utils.register_class(OBJECT_PT_RCVS_Panel)
    bpy.utils.register_class(OBJECT_PT_RCVS_Panel_Settings)

    if sys.platform != "win32":
        os.chmod(os.path.join(os.path.dirname(
            os.path.realpath(__file__)), _EXECUTABLE_NAME), 7770)


def unregister():
    del bpy.types.Scene.rcvs
    bpy.utils.unregister_class(RCVS_Properties)
    bpy.utils.unregister_class(RCVS_calculate)
    bpy.utils.unregister_class(RCVS_search)
    bpy.utils.unregister_class(OBJECT_PT_RCVS_Panel)
    bpy.utils.unregister_class(OBJECT_PT_RCVS_Panel_Settings)


if __name__ == "__main__":
    register()
