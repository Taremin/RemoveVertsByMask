import bpy

from . import props, remove_verts_by_mask


class VIEW3D_PT_remove_verts_by_mask_panel(bpy.types.Panel):
    bl_label = 'RemoveVertsByMask'
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.taremin_rvbm

        props.RemoveVertsPanelProps.draw(context, layout)
        layout.prop(settings, 'apply_shrinkwrap_modifier')

        layout.operator(
            remove_verts_by_mask.VIEW3D_OT_remove_verts_by_mask.bl_idname)


class VIEW3D_UL_RemoveSettings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.ui_units_x = 1.0

        col = layout.column()

        row = col.row()
        row.prop(
            item, "is_folding",
            icon="TRIA_RIGHT" if item.is_folding else "TRIA_DOWN",
            icon_only=True
        )

        icon = row.icon(item.ref_mask) if item.ref_mask else 0
        if item.is_folding:
            row.prop(item, "ref_enable", text="")
            row.label(text=item.ref_object.name)
            row.label(text=item.ref_mask.name, icon_value=icon)
        else:
            row.label(text="", icon="UV_DATA")

            box = row.box()
            box.prop(item, "ref_enable", text="有効")
            box.prop(item, "ref_object", text="対象オブジェクト")
            box.prop(item, "ref_mask", text="マスクテクスチャ", icon_value=icon)
            box.prop(item, "ref_uvmap", text="UVMap", translate=False)
            box.prop(item, "ref_channel", text="チャンネル")

            row = box.row()
            row.prop(item, "ref_watermark", text="しきい値", slider=True)
            row.prop(item, "ref_depth", text="隣接距離", slider=True)
