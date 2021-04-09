# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "GLBTextureTools",
    "author": "Lorenz Wieseke",
    "description": "",
    "blender": (2, 82, 1),
    "version": (0,1,0),
    "location": "3DView > Properties (N -KEY) > GLB Texture Tools",
    "warning": "",
    "wiki_url":    "https://docs.google.com/document/d/1w1h3ySyZG4taG01RbbDsPODsUP06cRCggxQKCt32QTk",
	"tracker_url": "https://github.com/LorenzWieseke/GLBTextureTools/issues",
    "category": "Generic"
}

import bpy
from .Functions import gui_functions


from . import auto_load

auto_load.init()
classes = auto_load.get_classes()

def register():
    auto_load.register()
    bpy.app.handlers.depsgraph_update_post.clear()    
    bpy.app.handlers.depsgraph_update_post.append(gui_functions.update_on_selection)


def unregister():
    auto_load.unregister()

