import importlib
import inspect
import sys
from pathlib import Path

import bpy

bl_info = {
    'name': 'Remove Vertices by Mask',
    'category': '3D View',
    'author': 'Taremin',
    'location': 'View 3D > Tools',
    'description': "",
    'version': (0, 0, 2),
    'blender': (2, 80, 0),
    'wiki_url': '',
    'tracker_url': '',
    'warning': '',
}

# モジュール読み込み
module_names = [
    "remove_verts_by_mask",
    "props",
    "panel"
]
namespace = globals()
for name in module_names:
    fullname = '{}.{}.{}'.format(__package__, "lib", name)
    if fullname in sys.modules:
        namespace[name] = importlib.reload(sys.modules[fullname])
    else:
        namespace[name] = importlib.import_module(fullname)

# クラスの登録
register_classes = [
    # このファイル内のBlenderクラス
]

for module in module_names:
    for module_class in [obj for name, obj in inspect.getmembers(namespace[module], inspect.isclass) if hasattr(obj, "bl_rna")]:
        register_classes.append(module_class)


def register():
    for cls in register_classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.taremin_rvbm = bpy.props.PointerProperty(
        type=props.RemoveVertsPanelProps)


def unregister():
    for cls in register_classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.taremin_rvbm
    Path(__file__).touch()


if __name__ == '__main__':
    register()
