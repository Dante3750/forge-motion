import bpy, addon_utils, importlib, sys
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.extensions.repo_refresh_all() if hasattr(bpy.ops.extensions,'repo_refresh_all') else None
addon_utils.enable("bl_ext.user_default.mpfb", default_set=True, persistent=True)
M = "bl_ext.user_default.mpfb"
def imp(mod, key): return getattr(importlib.import_module(M + "." + mod), key)
HumanService = imp("services.humanservice", "HumanService")
TargetService = imp("services.targetservice", "TargetService")
HOP = imp("entities.objectproperties", "HumanObjectProperties")
