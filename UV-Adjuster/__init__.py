bl_info = {
    "name": "UV Adjuster",
    "description": "Script to modify uv stuff easier.",
    "author": "sneakyevil",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "UV Editing > Sidebar > UV Adjuster",
    "warning": "",
    "support": "COMMUNITY",
    "category": "UV",
}

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty, PointerProperty
from bpy.types import Panel, Menu, Operator, PropertyGroup, AddonPreferences

class UVAdjusterProperty(PropertyGroup):
    m_Type: EnumProperty( name = "Type", description = "Choose adjust mode",
        items = (
            ( "move", "Move", "" ),
            ( "scale", "Scale", "" ),
            ( "image", "Image", "Adjust uv based on new image size and image offset" ),
            ( "normalize", "Normalize", "Tries to adjust uv to '0.0 - 1.0' range" ),
        ),
        default = "move",
    )
    m_MoveX: FloatProperty(name="x:", description="Horizontal move value", default=0.0, min=-1.0, max=1.0)
    m_MoveY: FloatProperty(name="y:", description="Vertical move value", default=0.0, min=-1.0, max=1.0)
    m_ScaleX: FloatProperty(name="x:", description="Horizontal scale value", default=1.0, min=0.0, max=2.0)
    m_ScaleY: FloatProperty(name="y:", description="Vertical scale value", default=1.0, min=0.0, max=2.0)
    # Image
    m_ImageX: IntProperty(name="x:", description="Horizontal image position", default=0, min=0)
    m_ImageY: IntProperty(name="y:", description="Vertical image position", default=0, min=0)
    m_ImageWidth: IntProperty(name="w:", description="Image width size", default=512, min=8)
    m_ImageHeight: IntProperty(name="h:", description="Image height size", default=512, min=8)
    m_ImageOldWidth: IntProperty(name="old w:", description="Old Image width size", default=256, min=8)
    m_ImageOldHeight: IntProperty(name="old h:", description="Old Image height size", default=256, min=8)

class UVAdjusterPanel(Panel):
    bl_label = "UV Adjuster"
    bl_idname = "UVADJUSTER_PT_PANEL"
    bl_category = "UV Adjuster"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        m_UVAdjusterProps = context.scene.UVAdjusterProps

        layout.prop(m_UVAdjusterProps, "m_Type")
        if m_UVAdjusterProps.m_Type == "move":
            row = layout.row(align=True)   
            row.prop(m_UVAdjusterProps, "m_MoveX")
            row.prop(m_UVAdjusterProps, "m_MoveY")
        elif m_UVAdjusterProps.m_Type == "scale":
            row = layout.row(align=True)   
            row.prop(m_UVAdjusterProps, "m_ScaleX")
            row.prop(m_UVAdjusterProps, "m_ScaleY")
        elif m_UVAdjusterProps.m_Type == "image":
            row = layout.row(align=True)   
            row.prop(m_UVAdjusterProps, "m_ImageX")
            row.prop(m_UVAdjusterProps, "m_ImageY")
            row = layout.row(align=True)   
            row.prop(m_UVAdjusterProps, "m_ImageWidth")
            row.prop(m_UVAdjusterProps, "m_ImageHeight")
            row = layout.row(align=True)   
            row.prop(m_UVAdjusterProps, "m_ImageOldWidth")
            row.prop(m_UVAdjusterProps, "m_ImageOldHeight")

        layout.operator("uv_adjuster.processbtn")

class UVAdjusterProcess(Operator):
    bl_label = "Process"
    bl_idname = "uv_adjuster.processbtn"
    bl_description = "Process settings on selected object"
    
    def execute(self, context):
        m_UVAdjusterProps = context.scene.UVAdjusterProps
        m_SelectedObject = bpy.context.active_object
        if m_SelectedObject and m_SelectedObject.type == "MESH":
            m_ObjectMode = bpy.context.object.mode
            bpy.ops.object.mode_set(mode="OBJECT")

            m_ActiveUVLayer = m_SelectedObject.data.uv_layers.active
            if m_ActiveUVLayer:
                m_MoveX, m_MoveY = (0.0, 0.0)
                m_ScaleX, m_ScaleY = (1.0, 1.0)
                if m_UVAdjusterProps.m_Type == "move":
                    m_MoveX, m_MoveY = (m_UVAdjusterProps.m_MoveX, m_UVAdjusterProps.m_MoveY * -1.0)
                elif m_UVAdjusterProps.m_Type == "scale":
                    m_ScaleX, m_ScaleY = (m_UVAdjusterProps.m_ScaleX, m_UVAdjusterProps.m_ScaleY)
                elif m_UVAdjusterProps.m_Type == "image":
                    m_MoveX  (m_UVAdjusterProps.m_ImageX / m_UVAdjusterProps.m_ImageWidth)
                    m_MoveY = (1.0 - ((m_UVAdjusterProps.m_ImageY +  m_UVAdjusterProps.m_ImageOldHeight) / m_UVAdjusterProps.m_ImageHeight))
                    m_ScaleX, m_ScaleY = (m_UVAdjusterProps.m_ImageOldWidth / m_UVAdjusterProps.m_ImageWidth, m_UVAdjusterProps.m_ImageOldHeight / m_UVAdjusterProps.m_ImageHeight)
                elif m_UVAdjusterProps.m_Type == "normalize":
                    for m_Data in m_ActiveUVLayer.data:
                        while (m_Data.uv.x > 1.0):
                            m_Data.uv.x -= 1.0
                              
                        while (m_Data.uv.x < 0.0):
                            m_Data.uv.x += 1.0

                        while (m_Data.uv.y > 1.0):
                            m_Data.uv.y -= 1.0
                              
                        while (m_Data.uv.y < 0.0):
                            m_Data.uv.y += 1.0

                for m_Data in m_ActiveUVLayer.data:
                    m_Data.uv.x *= m_ScaleX
                    m_Data.uv.y *= m_ScaleY
                    m_Data.uv.x += m_MoveX
                    m_Data.uv.y += m_MoveY

            bpy.ops.object.mode_set(mode=m_ObjectMode)
            self.report({ "INFO" }, "Processing finished.")
        else:
            self.report({ "ERROR" }, "You need to select mesh object!")

        return {"FINISHED"}

g_Classes = [ UVAdjusterProperty, UVAdjusterPanel, UVAdjusterProcess ]

def register():
    for m_Class in g_Classes:
        bpy.utils.register_class(m_Class)

    bpy.types.Scene.UVAdjusterProps = PointerProperty(type=UVAdjusterProperty)

def unregister():
    for m_Class in g_Classes:
        bpy.utils.unregister_class(m_Class)

    del bpy.types.Scene.UVAdjusterProps

if __name__ == "__main__":
    register()
