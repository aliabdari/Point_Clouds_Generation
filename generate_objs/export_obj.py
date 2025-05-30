import blenderproc as bproc
import math
import argparse
import os
import numpy as np
import time
import bpy


parser = argparse.ArgumentParser()
parser.add_argument("--front", help="Path to the 3D front file",
                    default='../../dataset/3D-FRONT/0a71be67-5024-4b9c-a53f-da0aaa294963.json',
                    required=False)
parser.add_argument("--future_folder", help="Path to the 3D Future Model folder.",
                    default='../../dataset/3D-FUTURE-model',
                    required=False)
parser.add_argument("--front_3D_texture_path", help="Path to the 3D FRONT texture folder.",
                    default='../../dataset/3D-FRONT-texture',
                    required=False)
parser.add_argument("--output_dir", default='./export_test', required=False, help="Path to where the data should be saved")
args = parser.parse_args()

if not os.path.exists(args.front) or not os.path.exists(args.future_folder):
    raise Exception("One of the two folders does not exist!")

start_time = time.time()

bproc.init()
mapping_file = bproc.utility.resolve_resource(os.path.join("front_3D", "3D_front_mapping.csv"))
mapping = bproc.utility.LabelIdMapping.from_csv(mapping_file)

# set the light bounces
bproc.renderer.set_light_bounces(diffuse_bounces=200, glossy_bounces=200, max_bounces=200,
                                 transmission_bounces=200, transparent_max_bounces=200)

# load the front 3D objects
loaded_objects = bproc.loader.load_front3d(
    json_path=args.front,
    future_model_path=args.future_folder,
    front_3D_texture_path=args.front_3D_texture_path,
    label_mapping=mapping
)

# Init sampler for sampling locations inside the loaded front3D house
bpy.ops.export_scene.obj(filepath=args.output_dir)


