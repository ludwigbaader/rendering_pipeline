import bpy # type: ignore
import json
import sys


main_output_path = bpy.context.scene.render.filepath

composite_output_paths = []
if bpy.context.scene.use_nodes:
    for node in bpy.context.scene.node_tree.nodes:
        if node.type == 'OUTPUT_FILE':
            composite_output_paths.append(node.base_path)

start_frame = bpy.context.scene.frame_start
end_frame = bpy.context.scene.frame_end

view_layers = []
for vl in bpy.context.scene.view_layers:
    if vl.use:
        view_layers.append(vl.name)

scene_data = {
    "main_output_path": main_output_path,
    "composite_output_paths": composite_output_paths,
    "start_frame": start_frame,
    "end_frame": end_frame,
    "view_layers": view_layers
}

f = open(sys.argv[-1], "w") # maybe pass location as argument when opening blender
f.write(json.dumps(scene_data))
f.close()
