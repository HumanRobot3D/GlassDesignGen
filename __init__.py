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
    "name" : "GlassDesignsGen",
    "author" : "Arthur B",
    "description" : "",
    "blender" : (2, 92, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy

from . main_script import MY_OT_GenerateGlassDesign
from . ui_panel import MY_PT_Panel 

classes = (
    MY_OT_GenerateGlassDesign, 
    MY_PT_Panel)

register, unregister = bpy.utils.register_classes_factory(classes)
