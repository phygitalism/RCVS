import bpy


# UI Properties
class RCVS_Properties(bpy.types.PropertyGroup):
    rays = [
        ("80", "80", "", 80),
        ("320", "320", "", 320),
        ("1280", "1280", "", 1280),
        ("5120", "5120", "", 5120),
    ]

    obj_path: bpy.props.StringProperty(
        default="//", subtype="DIR_PATH", description="Path to read OBJ files")
    rays_enum: bpy.props.EnumProperty(
        items=rays, default="1280", description="Number of rays")
    nearest: bpy.props.IntProperty(
        default=5, min=1, soft_max=20, description="Number of most similar objects in result")


# UI
class OBJECT_PT_RCVS_Panel_Settings(bpy.types.Panel):
    bl_label = "RCVS Settings"
    bl_idname = "OBJECT_PT_RCVS_Panel_Settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        box = layout.box()

        col = box.column()
        col.label(text="OBJ Library:")
        col.prop(context.scene.rcvs, 'obj_path', text="")
        row = box.row()
        row.prop(context.scene.rcvs, 'rays_enum', text="Rays")
        row.alert = True
        row.operator("RCVS.calculate", icon='MESH_ICOSPHERE')


class OBJECT_PT_RCVS_Panel(bpy.types.Panel):
    bl_label = "RCVS"
    bl_idname = "OBJECT_PT_RCVS_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        if bpy.context.active_object.type == 'MESH':
            col.active = True
            col.label(text="Search for similar to Active Object:")
            row = layout.row(align=True)
            row.prop(context.scene.rcvs, 'nearest', text="Nearest")
            row.operator("RCVS.search", icon='VIEWZOOM')
        else:
            col.active = False
            col.label(text="Active Object type has to be Mesh.")
