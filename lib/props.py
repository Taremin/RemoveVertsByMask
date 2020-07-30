import bpy


def poll(context, obj):
    return obj.type == 'MESH'


class RemoveVertsByMaskProps(bpy.types.PropertyGroup):
    def get_ref_uvmap(self, context):
        if self.ref_object is None:
            return []

        settings = context.scene.taremin_rvbm
        # スペースはtranslate=Falseでも翻訳されてしまうのを防ぐ
        return [(uvmap.name, uvmap.name + ' ', uvmap.name + ' ', 'UV', i) for (i, uvmap) in enumerate(self.ref_object.data.uv_layers)]

    ref_object: bpy.props.PointerProperty(type=bpy.types.Object, poll=poll)
    ref_mask: bpy.props.PointerProperty(type=bpy.types.Image)
    ref_watermark: bpy.props.FloatProperty(min=0.0, max=1.0)
    ref_channel: bpy.props.EnumProperty(
        items=(
            ('0', 'Red', 'Red channel'),
            ('1', 'Green', 'Green channel'),
            ('2', 'Blue', 'Blue channel'),
            ('3', 'Alpha', 'Alpha channel')
        ),
        description='マスクテクスチャの対象チャンネル')
    ref_uvmap: bpy.props.EnumProperty(items=get_ref_uvmap)
    ref_depth: bpy.props.IntProperty(
        default=2, min=0, soft_max=20, step=1, description='隣接頂点を確認する距離')


class RemoveVertsPanelProps(bpy.types.PropertyGroup):
    object_settings: bpy.props.CollectionProperty(
        type=RemoveVertsByMaskProps)
    object_settings_index: bpy.props.IntProperty(
        name="Active Index", default=-1)
    apply_shrinkwrap_modifier: bpy.props.BoolProperty(
        name="Apply Shrinkwrap Modifier",
        default=False,
        description="削除対象のオブジェクトがシュリンクラップモディファイアの対象になっていた場合に自動で適用します"
    )

    @classmethod
    def draw(cls, context, layout):
        settings = context.scene.taremin_rvbm
        row = layout.row()
        row.label(text="Settings")

        row = layout.row()
        col = row.column()
        col.template_list(
            "VIEW3D_UL_RemoveSettings",
            "test",  # TODO
            settings,
            "object_settings",
            settings,
            "object_settings_index",
            type="DEFAULT",
        )
        col = row.column(align=True)
        col.operator(RemoveVerts_OT_Add.bl_idname,
                     text="", icon="ADD")
        col.operator(RemoveVerts_OT_Remove.bl_idname,
                     text="", icon="REMOVE")

###############################################################################
# Props Operator
###############################################################################


class RemoveVerts_OT_Add(bpy.types.Operator):
    bl_idname = "taremin.remove_verts_add"
    bl_label = "Add Entry"
    bl_description = 'hoge'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.taremin_rvbm
        settings.object_settings.add()
        settings.object_settings_index = len(settings.object_settings) - 1
        return {'FINISHED'}


class RemoveVerts_OT_Remove(bpy.types.Operator):
    bl_idname = "taremin.remove_verts_remove"
    bl_label = "Remove Entry"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene.taremin_rvbm.object_settings_index >= 0

    def execute(self, context):
        settings = context.scene.taremin_rvbm
        settings.object_settings.remove(settings.object_settings_index)
        max_index = len(settings.object_settings) - 1
        if settings.object_settings_index > max_index:
            settings.object_settings_index = max_index
        return {'FINISHED'}
