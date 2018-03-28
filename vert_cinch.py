# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "VertCinch",
    "author": "Johnny Matthews",
    "version": (1, 0, 0),
    "blender": (2, 79, 1),
    "location": "View3D > Toolbar and View3D > Specials (W-key)",
    "warning": "",
    "description": "Move selected verts toward each other. To last selected or in Pairs",
    "category": "Mesh",
}

import bpy
import bmesh

def main(self,context,distance,pairs):
    me = bpy.context.object.data
    bm = bmesh.from_edit_mesh(me)   

    for s in bm.select_history:
        if(type(s).__name__ != "BMVert"):
            self.report({'ERROR_INVALID_INPUT'},"Not All Selections Were Verts")
            return


    last = len(bm.select_history)-1
    if pairs == False:
        for idx,val in enumerate(bm.select_history):
            if idx != last:
                val.co = val.co.lerp(bm.select_history[last].co,distance)
    else:
        for idx,val in enumerate(bm.select_history):
            if (idx % 2) == 0 and idx+1 <= last:
                val.co = val.co.lerp(bm.select_history[idx+1].co,distance)
    
    
               
    bmesh.update_edit_mesh(me) 


from bpy.props import (
        BoolProperty,
        FloatProperty
        )


class VertCinch(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.vert_cinch"
    bl_label = "Pull Selected Verts Together"
    bl_options = {'REGISTER', 'UNDO'}
    
    pairs    = BoolProperty(
        name = "Cinch Pairs",
        description = "Cinch every other selected vert",
        default = True  
    )
    
    distance = FloatProperty(
            name="Distance",
            description="Cinching Distance",
            min=0.00, max=1.0,
            default=1.0,
            )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(self,context,self.distance,self.pairs)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(VertCinch.bl_idname, icon='MESH_DATA')
    
    
def register():
    bpy.utils.register_class(VertCinch)
    bpy.types.VIEW3D_MT_edit_mesh_specials.prepend(menu_func)


def unregister():
    bpy.utils.unregister_class(VertCinch)
    bpy.types.VIEW3D_MT_edit_mesh_specials.remove(menu_func)

if __name__ == "__main__":
    register()

    # test call
    bpy.ops.mesh.vert_cinch()
