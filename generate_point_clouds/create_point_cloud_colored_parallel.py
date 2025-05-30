import open3d as o3d
import numpy as np
from PIL import Image
import os
from scipy.spatial import KDTree
from tqdm import tqdm
from tqdm_joblib import tqdm_joblib
from joblib import Parallel, delayed
import random


def load_texture_maps(mtl_path):
    texture_map = {}
    current_mtl = None
    mtl_dir = os.path.dirname(mtl_path)

    with open(mtl_path, 'r') as f:
        for line in f:
            if line.startswith("newmtl "):
                current_mtl = line.strip().split()[1]
            elif line.startswith("map_Kd") and current_mtl:
                texture_file = line.strip().split()[1]
                texture_path = os.path.join(mtl_dir, texture_file)
                texture_map[current_mtl] = texture_path
    return texture_map

def get_texture_color(image, uv):
    h, w = image.shape[0], image.shape[1]
    u = np.clip(uv[0], 0, 1)
    v = np.clip(1 - uv[1], 0, 1)
    px = int(u * (w - 1))
    py = int(v * (h - 1))
    return np.asarray(image[py, px]) / 255.0

def barycentric_coords(p, a, b, c):
    v0 = b - a
    v1 = c - a
    v2 = p - a
    d00 = np.dot(v0, v0)
    d01 = np.dot(v0, v1)
    d11 = np.dot(v1, v1)
    d20 = np.dot(v2, v0)
    d21 = np.dot(v2, v1)
    denom = d00 * d11 - d01 * d01
    if denom == 0:
        return np.array([1/3, 1/3, 1/3])  # fallback
    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w
    return np.array([u, v, w])

def sample_colored_points_from_obj(obj_file, num_points=50000):
    try:
        obj_path = 'export_objs' + os.sep + obj_file
        mtl_path = 'export_objs' + os.sep + obj_file.replace('.obj', '.mtl')
        output_path = 'colored_point_clouds' + os.sep + obj_file.replace('.obj', '.ply')

        # print("[INFO] Loading mesh...")
        mesh = o3d.io.read_triangle_mesh(obj_path, enable_post_processing=True)
        mesh.compute_vertex_normals()

        # print("[INFO] Sampling points from mesh...")
        pcd = mesh.sample_points_poisson_disk(number_of_points=num_points)

        # print("[INFO] Loading texture info...")
        texture_map = load_texture_maps(mtl_path)
        triangle_material_ids = np.asarray(mesh.triangle_material_ids)
        triangle_uvs = np.asarray(mesh.triangle_uvs).reshape((-1, 3, 2))
        triangles = np.asarray(mesh.triangles)
        vertices = np.asarray(mesh.vertices)

        # Load texture images
        loaded_textures = {}
        for name, path in texture_map.items():
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGB")
                    loaded_textures[name] = np.array(img)
                except Exception as e:
                    print(f"[WARNING] Failed to load texture {path}: {e}")

        # Prepare KDTree
        # print("[INFO] Building KDTree...")
        triangle_centers = np.mean(vertices[triangles], axis=1)
        kd_tree = KDTree(triangle_centers)

        # print("[INFO] Coloring points...")
        colors = []
        for point in np.asarray(pcd.points):
            _, tri_idx = kd_tree.query(point)
            tri = triangles[tri_idx]
            tri_uv = triangle_uvs[tri_idx]
            tri_xyz = vertices[tri]

            # Barycentric UV interpolation
            bc = barycentric_coords(point, tri_xyz[0], tri_xyz[1], tri_xyz[2])
            uv = bc[0] * tri_uv[0] + bc[1] * tri_uv[1] + bc[2] * tri_uv[2]

            mat_id = triangle_material_ids[tri_idx]
            material_name = list(texture_map.keys())[mat_id] if mat_id < len(texture_map) else None
            tex_img = loaded_textures.get(material_name)

            if tex_img is not None:
                color = get_texture_color(tex_img, uv)
                # print()
            else:
                color = np.array([0.5, 0.5, 0.5])  # fallback

            colors.append(color)

        pcd.colors = o3d.utility.Vector3dVector(np.array(colors))

        o3d.io.write_point_cloud(output_path, pcd)
    except:
        pass


def process_batch(ids, n_jobs=-1):
    with tqdm_joblib(tqdm(desc="Downloading Videos", total=len(ids))) as progress_bar:
        Parallel(n_jobs=n_jobs)(delayed(sample_colored_points_from_obj)(id_) for id_ in ids)


if __name__ == "__main__":
    obj_path = 'export_objs'
    mtl_path = 'export_objs'
    files = os.listdir(obj_path)
    obj_files = [x for x in os.listdir(obj_path) if '.obj' in x]

    print(len(obj_files))

    output_path = 'colored_point_clouds'
    available_point_clouds = [x.replace('.ply','.obj') for x in os.listdir(output_path)]

    remained_objs = [x for x in obj_files if x not in available_point_clouds]

    print('len(remained_objs)', len(remained_objs))
    process_batch(remained_objs, n_jobs=5)
