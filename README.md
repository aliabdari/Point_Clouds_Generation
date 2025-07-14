# Point_Clouds_Generation

This Repository is for generating 3d point clouds of furnished apartments along with their corresponding textual descriptions.


To generate the data, you need to get the [3DFront](https://tianchi.aliyun.com/specials/promotion/alibaba-3d-scene-dataset#) dataset, which can be obtained through this [link](https://tianchi.aliyun.com/specials/promotion/alibaba-3d-scene-dataset#download).

## Generate Point Clouds
To generate the 3D point clouds, first, it is needed to generate the obj files through the [create_obj_files.py](https://github.com/aliabdari/Point_Clouds_Generation/blob/main/generate_objs/create_obj_files.py) module. It is needed to fix the paths of the "3D-FRONT", "3D-FUTURE-model", and "3D-FRONT-texture" due to the 3DFRONT original files in the [export_obj.py](https://github.com/aliabdari/Point_Clouds_Generation/blob/main/generate_objs/export_obj.py) module, before running the "create_obj_files.py" module.

After generating the object files of the apartments, you will have "obj" and "mtl" files for each of the 3D scenes. Now you can generate RGB point clouds using [create_point_cloud_colored_non_parallel.py](https://github.com/aliabdari/Point_Clouds_Generation/blob/main/generate_point_clouds/create_point_cloud_colored_non_parallel.py) or [create_point_cloud_colored_parallel.py](https://github.com/aliabdari/Point_Clouds_Generation/blob/main/generate_point_clouds/create_point_cloud_colored_parallel.py) modules.

## Generate Textual Descriptions
To generate the Textual Descriptions for each of the apartments you can execute the [create_descriptions.py](https://github.com/aliabdari/Point_Clouds_Generation/blob/main/generate_descriptions/create_descriptions.py) module.

## Licence
This project is licensed under the MIT License - see the [LICENSE](https://github.com/aliabdari/Point_Clouds_Generation/blob/main/LICENSE) file for details.
