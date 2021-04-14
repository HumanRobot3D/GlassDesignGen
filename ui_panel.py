import bpy

class MY_PT_Panel(bpy.types.Panel):
    bl_idname = "MY_PT_Panel"
    bl_label = "GlassDesignGen"
    bl_category = "GlassDesignGen"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        
        layout = self.layout

        row = layout.row()
        row.operator('view3d.generateglassdesign', text="Generate")