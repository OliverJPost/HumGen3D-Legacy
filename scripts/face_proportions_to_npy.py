import os

import bpy
import numpy as np
from HumGen3D.backend.preferences.preference_func import get_prefs


def main():
    body = bpy.data.objects["HG_Body"]
    vert_count = len(body.data.vertices)
    body_coordinates = np.empty(vert_count * 3, dtype=np.float64)
    body.data.vertices.foreach_get("co", body_coordinates)

    for sk in body.data.shape_keys.key_blocks:
        if not sk.name.startswith("ff_"):
            continue

        prefix_dict = {
            "u_skull": ("ff_a", "ff_b"),
            "eyes": "ff_c",
            "l_skull": "ff_d",
            "nose": "ff_e",
            "mouth": "ff_f",
            "chin": "ff_g",
            "cheeks": "ff_h",
            "jaw": "ff_i",
            "ears": "ff_j",
            "custom": "ff_x",
        }

        for name, code in prefix_dict.items():
            if sk.name.startswith(code):
                category = name

        sk_coordinates = np.empty(vert_count * 3, dtype=np.float64)
        sk.data.foreach_get("co", sk_coordinates)

        relative_coordinates = sk_coordinates - body_coordinates

        save_name = sk.name[5:]
        path = os.path.join(get_prefs().filepath, "face_proportions", category)

        if not os.path.exists(path):
            os.makedirs(path)

        np.save(os.path.join(path, save_name), relative_coordinates)
        print("saved to", path)