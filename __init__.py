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
    "version": (0,0,4),
    "location": "",
    "warning": "",
    "category": "Generic"
}

from . import Functions, Panels, Properties, Operators, Bake,Help

def register():
    Functions.register()
    Panels.register()
    Properties.register()
    Operators.register()
    Bake.register()
    Help.register()


def unregister():
    Functions.unregister()
    Panels.unregister()
    Properties.unregister()
    Operators.unregister()
    Bake.unregister()
    Help.unregister()
    

# from . import auto_load

# auto_load.init()
# classes = auto_load.get_classes()

# def register():
#     auto_load.register()

# def unregister():
#     auto_load.unregister()
