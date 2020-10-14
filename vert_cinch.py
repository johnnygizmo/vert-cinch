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

#Now working with selection by PAIR OR 4 Extremities around 2 open loop (shortest path)

bl_info = {
    "name": "VertCinch",
    "author": "Johnny Matthews",
    "version": (1, 1, 1),
    "blender": (2, 82, 0),
    "location": "Mesh Edit Context Menu",
    "warning": "",
    "description": "Move selected verts toward each other. In Rows or Pairs",
    "category": "Mesh",
}

import bpy
import bmesh
import mathutils
from bpy.props import (
        BoolProperty,
        FloatProperty,
        EnumProperty
        )

def main(self,context):
    me = bpy.context.object.data
    bm = bmesh.from_edit_mesh(me) 
    bm.verts.ensure_lookup_table()
    hist = bm.select_history
    history = hist[:]
    history0 = hist[:]
    len_history = len(history)    
    len_history = len(history)    
    sel = [v for v in bm.verts if v.select]
    len_sel = len(sel)

##TODO UPDATE UVS    
    # uv_layer = bm.loops.layers.uv.verify()
    # dest = bm.loops.layers.uv.verify()
    # uv_verts = {}   
    # for face in bm.faces:
        # for loop in face.loops:
            # # uv = loop[uv_lay].uv
            # if loop.vert not in uv_verts:
                # uv_verts[loop.vert] = [loop[uv_layer]]
            # else:
                # uv_verts[loop.vert].append(loop[uv_layer])
                
            # bm.verts.index_update()
            # bm.verts.ensure_lookup_table()


        # layer = bm_to_add.loops.layers.uv.verify()
        # dest = bm.loops.layers.uv.verify()
        # for face in bm_to_add.faces:
            # f = add_face(tuple(bm.verts[i.index + offset] for i in face.verts))
            # f.material_index = face.material_index
            # for j, loop in enumerate(face.loops):
                # f.loops[j][dest].uv = loop[layer].uv
        # bm.faces.index_update()
        


    for item in hist:
        if not isinstance(item, bmesh.types.BMVert):
            self.report({'ERROR'}, "Select Vertices only") #or BAD SELECTION?
            return {'CANCELLED'}
        
    if len_history == 0:
        self.report({'ERROR'},"Select verts with Shift")
        return {'CANCELLED'}

    if len_sel != len_history:
        self.report({'ERROR'},"Select verts with Shift")
        return {'CANCELLED'}

#--Sequences--#
    def deselect():
        for f in bm.edges:
            f.select = False
        for e in bm.edges:
            e.select = False
        for v in bm.verts:
            v.select = False
        bm.select_flush(False)
        
    def path(v1, v2):
        v1.select = True
        v2.select = True
        bpy.ops.mesh.shortest_path_select()
        path = [v for v in bm.verts if v.select]
        path_copy = path.copy()
        return path_copy

    def sorted_path(path_copy, v1, v2,):
        sorted_path = [v1]

        while len(path_copy) > 1:
            v = sorted_path[-1]
            for e in v.link_edges:
                if e.other_vert(v) in path_copy:
                    path_copy.remove(v)
                    sorted_path.append(e.other_vert(v))
        if v2 not in sorted_path:
            sorted_path.append(v2)

        return sorted_path

    if len_history == 4:
        if self.group != 'PAIRS':
            deselect()
            path_1 = path(history[0], history[1])
            # if len(path_1) >= :
            sorted_path_1 = sorted_path(path_1, history[0], history[1])
            deselect()
            path_2 = path(history[2], history[3])
            sorted_path_2 = sorted_path(path_2, history[2], history[3])
            deselect()
            history = sorted_path_1+sorted_path_2
            len_history = len(history)
            bm.select_history.clear()
            for v in history:
                v.select=True
                bm.select_history.add(v)
        else:
            pass

    nf = len(bm.faces)
    layer = bm.loops.layers.uv.verify()
    for i, face in enumerate(bm.faces[nf:]):
        for j, loop in enumerate(face.loops):
            loop[layer].uv = uvs[i][j]

#--Pairs--#
    if self.group == 'PAIRS':                
        idx_last  = len_history-1
        for i,v in enumerate(history):

            if self.target == 'LAST': 
                if (i % 2) == 0 and i < idx_last:          
                    v.co = v.co.lerp(history[i+1].co,self.distance)
            if self.target == 'FIRST': 
                if (i % 2) == 1 and i <= idx_last:          
                    v.co = v.co.lerp(history[i-1].co,self.distance)   
            if self.target == 'MIDDLE': 
                if (i % 2) == 0 and i < idx_last:
                    center = v.co.lerp(history[i+1].co,0.5)
                    v.co = v.co.lerp(center,self.distance)   
                if (i % 2) == 1 and i <= idx_last:   
                    v.co = v.co.lerp(center,self.distance)

                    
#--Rows--#
    if self.group == 'ROWS':
        half = len_history // 2
        
        if self.target == 'LAST': 
            for i,v in enumerate(history):
                if i < half:
                    v.co = v.co.lerp(history[i+half].co,self.distance)
        if self.target == 'FIRST': 
            for i,v in enumerate(history):
                if i >= half:
                    v.co = v.co.lerp(history[i-half].co,self.distance)  

        if self.target == 'MIDDLE': 
            for i,v in enumerate(history):
                if i < half:
                    center = v.co.lerp(history[i+half].co,0.5)
                    history[i].co      = history[i].co.lerp(center,self.distance)
                    history[i+half].co = history[i+half].co.lerp(center,self.distance)                
            
#--Cluster--#    
    if self.group == 'CLUSTER':
        idx_last  = len_history-1
        if self.target == 'FIRST': 
            for i,v in enumerate(history):
                if i != 0:
                    v.co = v.co.lerp(history[0].co,self.distance)
        elif self.target == 'LAST':        
            for i,v in enumerate(history):
                if i != idx_last:
                    v.co = v.co.lerp(history[idx_last].co,self.distance)
        elif self.target == "MIDDLE":
            center = mathutils.Vector((0.0, 0.0, 0.0))
            for i,v in enumerate(history):
                center = center + v.co
            center.x = center.x / len_history
            center.y = center.y / len_history
            center.z = center.z / len_history
            for i,v in enumerate(history):
                v.co = v.co.lerp(center,self.distance)

    if self.merge:
        if self.distance==1:            
            bmesh.ops.remove_doubles(bm, verts=history, dist=0.0001)

    bm.normal_update()           
    bmesh.update_edit_mesh(me) 


class VertCinch(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "mesh.vert_cinch"
    bl_label = "Multi Merge"
    bl_options = {'REGISTER', 'UNDO'}

    group: EnumProperty(
                name="By",
                description="Vertex group",
                default="ROWS",
                items=(
                    ('ROWS','Rows','Between the 2 rows (after selecting 4 extremities)'),
                    ('PAIRS','Pairs','Following selected Pairs'),
                    ('CLUSTER','Every','all selected to first,last,center'),
                ))
    target: EnumProperty(
                name="To",
                description="Cinch Target",
                default="MIDDLE",
                items=(
                    ('FIRST','At First','Lerp or merge to First Vertex or Row'),
                    ('MIDDLE','At Center','Lerp or merge to Center'),
                    ('LAST','At Last','Lerp or merge to Last Vertex or Row'),
                ))
    distance: FloatProperty(
            name="Distance",
            description="Cinching Distance",
            min=0, max=1,
            default=0,
            )
    merge: BoolProperty(
            name="Merge",
            description="Merge",
            default=True,
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
