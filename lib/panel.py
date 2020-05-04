import bpy

from . import props, remove_verts_by_mask


class VIEW3D_PT_remove_verts_by_mask_panel(bpy.types.Panel):
    bl_label = 'RemoveVertsByMask'
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        props.RemoveVertsPanelProps.draw(context, layout)
        layout.operator(
            remove_verts_by_mask.VIEW3D_OT_remove_verts_by_mask.bl_idname)


class VIEW3D_UL_RemoveSettings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        col = layout.column()
        row = col.row()
        row.ui_units_x = 1.0
        row.label(text="", icon="UV_DATA")
        col = row.column()

        row = col.row()
        row.prop(item, "ref_object", text="")
        icon = col.icon(item.ref_mask) if item.ref_mask else 0
        row.prop(item, "ref_mask", text="", icon_value=icon)
        row.prop(item, "ref_uvmap", text="", translate=False)

        row = col.row()
        row.prop(item, "ref_channel", text="")
        row.prop(item, "ref_watermark", text="しきい値", slider=True)
        row.prop(item, "ref_depth", text="隣接距離", slider=True)
