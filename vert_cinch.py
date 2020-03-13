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
    "version": (1, 1, 0),
    "blender": (2, 82, 0),
    "location": "Mesh Edit Context Menu",
    "warning": "",
    "description": "Move selected verts toward each other. In Rows or Pairs",
    "category": "Mesh",
}

import bpy
import bmesh
import mathutils

def main(self,context):
    me = bpy.context.object.data
    bm = bmesh.from_edit_mesh(me)       

    for s in bm.select_history:
        print(type(s).__name__)

        if(type(s).__name__ != "BMVert"):
            self.report({'ERROR_INVALID_INPUT'},"Make a vertex selection only")
            return

    if len(bm.select_history) == 0:
        self.report({'ERROR_INVALID_INPUT'},"Make individual vertex selections, circle and box select do not work")
        return

    sct = 0
    for v in bm.verts:
        if v.select:
            sct = sct + 1
    
    if sct != len(bm.select_history):
        self.report({'ERROR_INVALID_INPUT'},"Make individual vertex selections")
        return


    verts = len(bm.select_history)
    last  = verts-1

    if self.grouping == 'PAIRS':
        if(verts % 2) != 0:
            self.report({'ERROR_INVALID_INPUT'},"Odd number of verts selected. Last will be ignored")
        
        center = bm.select_history[0]
        for idx,val in enumerate(bm.select_history):

            if self.target == 'LAST': 
                if (idx % 2) == 0 and idx+1 <= last:          
                    val.co = val.co.lerp(bm.select_history[idx+1].co,self.distance)
            if self.target == 'FIRST': 
                if (idx % 2) == 1 and idx <= last:          
                    val.co = val.co.lerp(bm.select_history[idx-1].co,self.distance)   
            if self.target == 'MIDDLE': 
                if (idx % 2) == 0 and idx+1 <= last:   
                    center = val.co.lerp(bm.select_history[idx+1].co,0.5)
                    val.co = val.co.lerp(center,self.distance)   
                if (idx % 2) == 1 and idx <= last:   
                    val.co = val.co.lerp(center,self.distance)  

    elif self.grouping == 'ROWS':
        half = verts // 2
        
        if self.target == 'LAST': 
            for idx,val in enumerate(bm.select_history):
                if idx < half:
                    val.co = val.co.lerp(bm.select_history[idx+half].co,self.distance)
        if self.target == 'FIRST': 
            for idx,val in enumerate(bm.select_history):
                if idx >= half:
                    val.co = val.co.lerp(bm.select_history[idx-half].co,self.distance)  

        if self.target == 'MIDDLE': 
            for idx,val in enumerate(bm.select_history):
                if idx < half:
                    center = val.co.lerp(bm.select_history[idx+half].co,0.5)
                    bm.select_history[idx].co      = bm.select_history[idx].co.lerp(center,self.distance)
                    bm.select_history[idx+half].co = bm.select_history[idx+half].co.lerp(center,self.distance)                
            
    
    elif self.grouping == 'CLUSTER':
        if self.target == 'FIRST': 
            for idx,val in enumerate(bm.select_history):
                if idx != 0:
                    val.co = val.co.lerp(bm.select_history[0].co,self.distance)
        elif self.target == 'LAST':        
            for idx,val in enumerate(bm.select_history):
                if idx != last:
                    val.co = val.co.lerp(bm.select_history[last].co,self.distance)
        elif self.target == "MIDDLE":
            center = mathutils.Vector((0.0, 0.0, 0.0))
            for idx,val in enumerate(bm.select_history):
                center = center + val.co
            center.x = center.x / verts
            center.y = center.y / verts
            center.z = center.z / verts
            for idx,val in enumerate(bm.select_history):
                val.co = val.co.lerp(center,self.distance)


               
    bmesh.update_edit_mesh(me) 


from bpy.props import (
        BoolProperty,
        FloatProperty,
        EnumProperty
        )


class VertCinch(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.vert_cinch"
    bl_label = "Vertex Cinch"
    bl_options = {'REGISTER', 'UNDO'}
    

### TODO - Add a menu of Pairs, To Last, To First, Strips
    
    grouping: EnumProperty(
                name="Grouping",
                description="Vertex Grouping",
                default="PAIRS",
                items=(
                    ('PAIRS','Pairs','Cinch every other vertex selected'),
                    ('ROWS','Rows','Cinch first half of selecte to 2nd half'),
                    ('CLUSTER','Cluster','Cinch all selected to one vertex')
                )
    )
    target: EnumProperty(
                name="Target",
                description="Cinch Target",
                default="FIRST",
                items=(
                    ('FIRST','First','Cinch to First Vertex or Row'),
                    ('LAST','Last','Cinch to Last Vertex or Row'),
                    ('MIDDLE','Middle','Cinch to Midpoint')
                )
    )

    distance: FloatProperty(
            name="Distance",
            description="Cinching Distance",
            min=0.00, max=1.0,
            default=1.0,
            )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        main(self,context)
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.operator(VertCinch.bl_idname, icon='MESH_DATA')
    
    
def register():
    bpy.utils.register_class(VertCinch)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)


def unregister():
    bpy.utils.unregister_class(VertCinch)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(menu_func)

if __name__ == "__main__":
    register()
