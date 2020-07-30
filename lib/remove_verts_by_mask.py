import bpy
import bmesh
import numpy


class VIEW3D_OT_remove_verts_by_mask(bpy.types.Operator):
    bl_idname = "taremin.remove_verts_op"
    bl_label = 'Remove'

    def execute(self, context):
        settings = context.scene.taremin_rvbm
        mode = context.active_object.mode
        active = context.active_object

        # get shrinkwrap modifiers
        modifier_target_dict = {}
        if settings.apply_shrinkwrap_modifier:
            for obj in bpy.context.window.view_layer.objects:
                for mod in obj.modifiers:
                    if mod.type != 'SHRINKWRAP':
                        continue
                    if mod.target is None:
                        continue
                    if mod.target.name not in modifier_target_dict:
                        modifier_target_dict[mod.target.name] = []
                    modifier_target_dict[mod.target.name].append((obj, mod))

        for s in context.scene.taremin_rvbm.object_settings:
            if s.ref_object is None:
                continue
            if s.ref_mask is None:
                continue
            if s.ref_uvmap is None:
                continue

            if settings.apply_shrinkwrap_modifier:
                if s.ref_object.name in modifier_target_dict:
                    for (obj, mod) in modifier_target_dict[s.ref_object.name]:
                        bpy.context.window.view_layer.objects.active = obj
                        bpy.ops.object.modifier_apply(modifier=mod.name)

            self.remove(s.ref_object, s.ref_mask, s.ref_uvmap,
                        s.ref_watermark, int(s.ref_channel), s.ref_depth)

        bpy.context.window.view_layer.objects.active = active 
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

    def remove(self, obj, image, uv_name, watermark=0.0, channel=0, link_depth=2):
        # refresh bmesh
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)

        # pixels[y,x]で色が取得できる
        size = image.size

        pixels = numpy.array(image.pixels).reshape(size[1], size[0], 4)

        # get vertex uv color
        vertex_to_color = numpy.ndarray(shape=(len(bm.verts), 4))
        for (vertex_index, uvs) in self.create_vertex_uv(bm, uv_name).items():
            colors = numpy.zeros(len(uvs)*4).reshape(len(uvs), 4)
            for i in range(len(uvs)):
                uv = uvs[i]
                # get from vertex index
                pixel = self.get_pixel_by_uv_coord(
                    pixels, size[0], size[1], uv)
                colors[i] = pixel
            vertex_to_color[vertex_index] = colors.mean(axis=0)

        def select_depth(vert, max_depth=1, visited=None):
            if visited is None:
                visited = numpy.zeros(len(bm.verts), dtype=numpy.bool)
                visited[vert.index] = True

            if max_depth <= 0:
                return visited

            for e in vert.link_edges:
                v = e.other_vert(vert)
                visited[v.index] = True
                select_depth(v, max_depth-1, visited)

            return visited

        # get verts
        remove_verts = []
        bm.verts.ensure_lookup_table()
        for i in range(len(vertex_to_color)):
            visited = select_depth(bm.verts[i], max_depth=link_depth)
            tmp = vertex_to_color[visited][:, channel]
            if numpy.all(tmp <= watermark):
                remove_verts.append(bm.verts[i])

        bmesh.ops.delete(bm, geom=remove_verts, context='VERTS')

        # cleanup mesh
        bmesh.ops.delete(
            bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')

    def create_vertex_uv(self, bm, uv_name):
        uv_layer = bm.loops.layers.uv[uv_name]
        dict = {}

        for f in bm.faces:
            for l in f.loops:
                index = l.vert.index
                if index not in dict:
                    dict[index] = []
                dict[index].append(l[uv_layer].uv.copy())

        return dict

    def get_pixel_by_uv_coord(self, pixels, width, height, uv):
        return pixels[
            int(width * (uv[1] % 1)),
            int(height * (uv[0] % 1))
        ]
