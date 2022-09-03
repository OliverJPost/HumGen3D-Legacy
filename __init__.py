'''
    Created by Oliver J Post & Alexander Lashko

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name" : "LEGACY Human Generator 3D",
    "author" : "Oliver J. Post & Alexander Lashko",
    "description" : "Legacy version of Human Generator 3D for manipulating humans made with 3.0 or before",
    "blender" : (2, 83, 0),
    "version" : (3, 0, 5), #RELEASE update version number
    "location" : "Add-On Sidepanel > HumGen",
    "wiki_url": "http://humgen3d.com",
    "tracker_url": "http://humgen3d.com",
    "warning" : "",
    "category" : ""
}


import bpy  # type: ignore
import bpy.utils.previews  # type: ignore # Has to be imported like this, otherwise returns error for some users
from bpy.app.handlers import persistent  # type: ignore

from .core.settings.HG_PROPS import HG_OBJECT_PROPS, HG_SETTINGS
from .user_interface import HG_BATCH_UILIST, HG_UTILITY_UILISTS


########### startup procedure #########
@persistent
def HG_start(dummy):
    """Runs the activating class when a file is loaded or blender is opened
    """    
def _initiate_preview_collections():
    #initiate preview collections
    pcoll_names = [
    'humans',
    'poses',
    'outfit',
    'footwear',
    'hair',
    'face_hair',
    'expressions',
    'patterns',
    'textures'
    ]
    
    for pcoll_name in pcoll_names:
        preview_collections.setdefault(
            f"pcoll_{pcoll_name}",
            bpy.utils.previews.new()
            )
    bpy.ops.hg3d_legacy.activate()


from .HG_CLASSES import hg_classes


def register():
    #RELEASE remove print statements
    for cls in hg_classes:    
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.HG3D_LEGACY = bpy.props.PointerProperty(type=HG_SETTINGS) #Main props

    #load handler
    if not HG_start in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(HG_start)

def unregister():
    for cls in hg_classes:
        bpy.utils.unregister_class(cls)
    
    #remove handler
    if HG_start in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(HG_start)

    bpy.types.VIEW3D_MT_add.remove(add_hg_primitive_menu)

    preview_collections.clear()

if __name__ == "__main__":
    register()
