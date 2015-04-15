# Copyright (C) 2014 Louis Vottero louis.vot@gmail.com    All rights reserved.

import traceback

import maya.cmds as cmds
import util
import blendshape
import vtool.util

        
class PoseManager(object):
    

    
    def __init__(self):
        self.poses = []
        
        self.pose_group = 'pose_gr'

        if not cmds.objExists(self.pose_group):
            
            selection = cmds.ls(sl = True)
            
            self.pose_group = cmds.group(em = True, n = self.pose_group)
        
            data = util.StoreControlData(self.pose_group)
            data.set_data()
            
            if selection:
                cmds.select(selection)

    
    def is_pose(self, name):
        
        if BasePoseControl().is_a_pose(name):
            return True
        
        return False
        
    def get_pose_instance(self, pose_name):
        
        if cmds.objExists('%s.type' % pose_name):
            pose_type = cmds.getAttr('%s.type' % pose_name)
        
        if not cmds.objExists('%s.type' % pose_name):
            pose_type = 'cone'

        if pose_type == 'cone':
            pose = PoseControl()
            
        if pose_type == 'no reader':
            pose = PoseNoReader()
            
        pose.set_pose(pose_name)
        
        return pose
                        
    def get_poses(self):
        relatives = cmds.listRelatives(self.pose_group)
        
        if not relatives:
            return
        
        poses = []
        
        for relative in relatives:
            if self.is_pose(relative):
                poses.append(relative)
                
        return poses

    def get_all_pose_inbetween_target(self):
        
        poses = self.get_poses()
        
        targets = [] 
        
        for pose in poses:
            pose_instance = self.get_pose_instance(pose)
            
            target = pose_instance.get_target_name()
    
            targets.append(target)
    
        return targets
    
    def get_transform(self, name):
        pose = self.get_pose_instance(name)
        transform = pose.get_transform()
        
        return transform
        
    def get_pose_control(self, name):
        
        pose = self.get_pose_instance(name)
        
        control = pose.pose_control
        
        return control
    
    def get_mesh_index(self, name, mesh):
        pose = self.get_pose_instance(name)
        
        mesh_index = pose.get_target_mesh_index(mesh)
        
        if mesh_index != None:
            
            return mesh_index
    
    def set_default_pose(self):
        store = util.StoreControlData(self.pose_group)
        store.set_data()
        
    def set_pose_to_default(self):
        store = util.StoreControlData(self.pose_group)
        store.eval_data()
    
    def set_pose(self, pose):
        store = util.StoreControlData(pose)
        store.eval_data()
        
    def set_pose_data(self, pose):
        store = util.StoreControlData(pose)
        store.set_data()
        
    def set_poses(self, pose_list):
        
        data_list = []
        
        for pose_name in pose_list:
            
            store = util.StoreControlData(pose_name)

            data_list.append( store.eval_data(True) )
            
        store = util.StoreControlData().eval_multi_transform_data(data_list)
    
    @util.undo_chunk
    def create_cone_pose(self, name = None):
        selection = cmds.ls(sl = True, l = True)
        
        if not selection:
            return
        
        if not cmds.nodeType(selection[0]) == 'joint' or not len(selection):
            return
        
        if not name:
            joint = selection[0].split('|')
            joint = joint[-1]
            
            name = 'pose_%s' % joint
        
        pose = PoseControl(selection[0], name)
        pose_control = pose.create()
        
        self.pose_control = pose_control
        
        return pose_control

    @util.undo_chunk
    def create_no_reader_pose(self, name = None):
        #selection = cmds.ls(sl = True, l = True)
        
        #if not selection:
        #    return
        
        #if not cmds.nodeType(selection[0]) == 'joint' or not len(selection):
        #    return
        
        #if not name:
        #    joint = selection[0].split('|')
        #    joint = joint[-1]
            
        #    name = 'pose_%s' % joint
        
        name = util.inc_name('pose_no_reader_1')
        
        
        pose = PoseNoReader(name)
        pose_control = pose.create()
        
        self.pose_control = pose_control
        
        return pose_control
    
    @util.undo_chunk
    def reset_pose(self, pose_name):
        
        pose = self.get_pose_instance(pose_name)
        pose.reset_target_meshes()
    
    @util.undo_chunk
    def rename_pose(self, pose_name, new_name):
        pose = self.get_pose_instance(pose_name)
        return pose.rename(new_name)
    
    @util.undo_chunk
    def add_mesh_to_pose(self, pose_name, meshes = None):
        
        selection = None

        if not meshes == None:
            selection = cmds.ls(sl = True, l = True)
        if meshes:
            selection = meshes
        
        pose = self.get_pose_instance(pose_name)
        
        added_meshes = []
        
        if selection:
            for sel in selection:
                
                shape = util.get_mesh_shape(sel)
                
                if shape:
                    pose.add_mesh(sel)
                    added_meshes.append(sel)
                    
        return added_meshes
        
    
    def visibility_off(self, pose_name):
        pose = self.get_pose_instance(pose_name)
        pose.visibility_off(view_only = True)
        
    def toggle_visibility(self, pose_name, view_only = False, mesh_index = 0):
        pose = self.get_pose_instance(pose_name)
        pose.set_mesh_index(mesh_index)
        pose.toggle_vis(view_only)
    
    @util.undo_chunk
    def delete_pose(self, name):
        pose = self.get_pose_instance(name)
        pose.delete()
        
    def detach_poses(self):
        poses = self.get_poses()
        for pose_name in poses:
            
            pose = self.get_pose_instance(pose_name)
            pose.detach()
            
            
    def attach_poses(self):
        poses = self.get_poses()
        
        for pose_name in poses:
            
            pose = self.get_pose_instance(pose_name)
            pose.attach()
        
    @util.undo_chunk    
    def create_pose_blends(self, pose_name = None):
        
        if pose_name:
            pose = self.get_pose_instance(pose_name)
            pose.create_all_blends()
            return
        
        poses = self.get_poses()
        count = len(poses)

        progress = util.ProgressBar('adding poses ... ', count)
    
        for inc in range(count) :
            
            try:
                if progress.break_signaled():
                    break
                
                pose_name = poses[inc]
                
                pose = self.get_pose_instance(pose_name)
                
                pose.set_pose(pose_name)
                pose.create_all_blends()
                             
                cmds.refresh()
                
                progress.inc()
                progress.status('adding pose %s' % pose_name)
            
            except:
                vtool.util.show( traceback.format_exc() )
            
        progress.end()
    
    def mirror_pose(self, name):
        pose = self.get_pose_instance(name)
        mirror = pose.mirror()
        
        return mirror        
        
        

class BasePoseControl(object):
    def __init__(self, description = 'pose'):
        
        self.pose_control = None

        if description:
            description = description.replace(' ', '_')

        self.description = description

        self.scale = 1
        self.mesh_index = 0
        
        self.blend_input = None
    
    #--- private
      
    def _pose_type(self):
        return 'base'
        
    def _refresh_meshes(self):
        
        meshes = self._get_corrective_meshes()
        
        for mesh in meshes:
            target_mesh = self._get_mesh_target(mesh)
            
            if target_mesh:
                
                cmds.setAttr('%s.inheritsTransform' % mesh, 0)
                util.unlock_attributes(mesh, only_keyable=True)
                
                const = cmds.parentConstraint(target_mesh, mesh)
            
                cmds.delete(const)
                
    def _refresh_pose_control(self):
        
        if not cmds.objExists(self.pose_control):
            return
        
        shapes = cmds.listRelatives(self.pose_control, s = True)
        cmds.showHidden( shapes )
        
        if not cmds.objExists('%s.enable' % self.pose_control):
            cmds.addAttr(self.pose_control, ln = 'enable', at = 'double', k = True, dv = 1, min = 0, max = 1)
            multiply = self._get_named_message_attribute('multiplyDivide2')
            
            multiply_offset = self._create_node('multiplyDivide')
        
            cmds.connectAttr('%s.outputX' % multiply, '%s.input1X' % multiply_offset)
            cmds.connectAttr('%s.enable' % self.pose_control, '%s.input2X' % multiply_offset)
        
            cmds.disconnectAttr('%s.outputX' % multiply, '%s.weight' % self.pose_control)
            cmds.connectAttr('%s.outputX' % multiply_offset, '%s.weight' % self.pose_control)
        
    def _create_top_group(self):
        top_group = 'pose_gr'
        
        if not cmds.objExists(top_group):
            top_group = cmds.group(em = True, name = top_group)

        return top_group

    def _get_name(self):
        return util.inc_name(self.description) 
    
    def _set_description(self, description):
        cmds.setAttr('%s.description' % self.pose_control, description, type = 'string' )
        self.description = description

    def _rename_nodes(self):
        
        nodes = self._get_connected_nodes()
        
        for node in nodes:
            node_type = cmds.nodeType(node)
            
            if node_type == 'transform':
                shape = util.get_mesh_shape(node)
                
                if shape:
                    node_type = cmds.nodeType(shape)
            
            cmds.rename(node, util.inc_name('%s_%s' % (node_type, self.description)))

    def _create_node(self, maya_node_type):
        node = cmds.createNode(maya_node_type, n = util.inc_name('%s_%s' % (maya_node_type, self.description)))
        
        messages = self._get_message_attributes()
        
        found = []
        
        for message in messages:
            if message.startswith(maya_node_type):
                found.append(message)
                
        inc = len(found) + 1
        
        self._connect_node(node, maya_node_type, inc)
        
        return node
        
    def _connect_node(self, node, maya_node_type, inc = 1):
        attribute = '%s%s' % (maya_node_type, inc)
        
        cmds.addAttr(self.pose_control, ln = attribute, at = 'message' )
        cmds.connectAttr('%s.message' % node, '%s.%s' % (self.pose_control, attribute))
    
    def _connect_mesh(self, mesh):
        messages = self._get_mesh_message_attributes()
        
        
        index = self.get_mesh_index(mesh)
        
        if index != None:
            return
        
        inc = len(messages) + 1
        
        self._connect_node(mesh, 'mesh', inc)

    def _get_named_message_attribute(self, name):
        
        node = util.get_attribute_input('%s.%s' % (self.pose_control, name), True)
        
        return node
        
    def _get_mesh_message_attributes(self):
        
        if not self.pose_control:
            return
        
        attributes = cmds.listAttr(self.pose_control, ud = True)
        
        messages = []
        
        for attribute in attributes:
            if attribute.startswith('mesh'):
                node_and_attribute = '%s.%s' % (self.pose_control, attribute)
            
                if cmds.getAttr(node_and_attribute, type = True) == 'message':
                    messages.append(attribute)
                
        return messages
        
    def _get_mesh_count(self):
        attrs = self._get_mesh_message_attributes()
        
        return len(attrs)
        
    def _get_corrective_meshes(self):
        
        found = []
        
        for inc in range(0, self._get_mesh_count()):
            mesh = self.get_mesh(inc)
            found.append(mesh)
            
        return found
        
        
    def _check_if_mesh_connected(self, name):
        
        for inc in range(0, self._get_mesh_count()):
            
            mesh = self.get_mesh(inc)
            
            target = self._get_mesh_target(mesh)
            if target == name:
                return True
        
        return False
    
    def _check_if_mesh_is_child(self, mesh):
        children = cmds.listRelatives(self.pose_control, f = True)
        
        for child in children:
            if child == mesh:
                return True
            
        return False
    
    def _hide_meshes(self):
        children = cmds.listRelatives(self.pose_control, f = True, type = 'transform')
        cmds.hide(children)
        
    def _get_mesh_target(self, mesh):
        if not mesh:
            return None
        
        target_mesh = cmds.getAttr('%s.mesh_pose_source' % mesh)
        
        if not cmds.objExists(target_mesh):
            target = util.get_basename(target_mesh)
            
            if cmds.objExists(target):
                target_mesh = target

        return target_mesh
        
    def _get_message_attributes(self):
        
        attributes = cmds.listAttr(self.pose_control, ud = True)
        
        messages = []
        
        for attribute in attributes:
            node_and_attribute = '%s.%s' % (self.pose_control, attribute)
            
            if cmds.getAttr(node_and_attribute, type = True) == 'message':
                messages.append(attribute)
                
        return messages
    
    def _get_connected_nodes(self):
        
        attributes = self._get_message_attributes()
        
        nodes = []
        
        for attribute in attributes:
            connected = util.get_attribute_input('%s.%s' % (self.pose_control, attribute), node_only = True)
            
            if connected:
                nodes.append(connected)
                
        return nodes

    def _create_attributes(self, control):
        
        cmds.addAttr(control, ln = 'description', dt = 'string')
        cmds.setAttr('%s.description' % control, self.description, type = 'string')
        
        #cmds.addAttr(control, ln = 'targetName', dt = 'string')
        
        
        
        cmds.addAttr(control, ln = 'control_scale', at = 'float', dv = 1)
        
        title = util.MayaEnumVariable('POSE')
        title.create(control)  
        
        pose_type = util.MayaStringVariable('type')
        pose_type.set_value(self._pose_type())
        pose_type.set_locked(True)
        pose_type.create(control)
        
        cmds.addAttr(control, ln = 'enable', at = 'double', k = True, dv = 1, min = 0, max = 1)
        cmds.addAttr(control, ln = 'weight', at = 'double', k = True, dv = 0)
        
        cmds.addAttr(control, ln = 'meshIndex', at = 'short', dv = self.mesh_index)
        cmds.setAttr('%s.meshIndex' % self.pose_control, l = True)

        #cmds.addAttr(control, ln = 'inbetweenWeight', at = 'double', min = -1, max = 1, dv = 1)

    def _create_pose_control(self):
        
        control = util.Control(self._get_name())
        control.set_curve_type('cube')
        
        control.hide_scale_and_visibility_attributes() 
        
        pose_control = control.get()
        self.pose_control = control.get()
        
        self._create_attributes(pose_control)
        
        return pose_control
    
    def _delete_connected_nodes(self):
        nodes = self._get_connected_nodes()
        if nodes:
            cmds.delete(nodes)

    def _create_shader(self, mesh):
        shader_name = 'pose_blinn'
            
        shader_name = util.apply_new_shader(mesh, type_of_shader = 'blinn', name = shader_name)
            
        cmds.setAttr('%s.color' % shader_name, 0.4, 0.6, 0.4, type = 'double3' )
        cmds.setAttr('%s.specularColor' % shader_name, 0.3, 0.3, 0.3, type = 'double3' )
        cmds.setAttr('%s.eccentricity' % shader_name, .3 )

    def _get_blendshape(self, mesh):
        
        return util.find_deformer_by_type(mesh, 'blendShape')

    def _get_current_mesh(self, mesh_index):
        mesh = None
        
        if mesh_index == None:
            mesh = self.get_mesh(self.mesh_index)
        if mesh_index != None:
            mesh = self.get_mesh(mesh_index)
            
        if not mesh:
            return
        
        return mesh
    
    def _update_inbetween(self):
        poses = PoseManager().get_poses()
        
        weights = []
        
        for pose in poses:
            pose_instance = PoseManager().get_pose_instance(pose)
            weight = pose_instance.get_inbetween_weight()
            
            weights.append(weight)
    
        for pose in poses:
            pass
    
    def _replace_side(self, string_value):
        
        if string_value == None:
            return
        
        split_value = string_value.split('|')
        
        fixed = []
        
        for value in split_value:
        
            other = ''
            start, end = vtool.util.find_special('lf_', value, 'first')
            
            if start != None:
                other = vtool.util.replace_string(value, 'rt_', start, end)
                
            start, end = vtool.util.find_special('_L', value, 'last')
            
            if start != None:
                other = vtool.util.replace_string(value, '_R', start, end)
                
            fixed.append(other)
            
        if len(fixed) == 1:
            
            return fixed[0]
        
        import string
        fixed = string.join(fixed, '|')
        
        print fixed
        
        return fixed
        
    
    #--- pose

    def is_a_pose(self, node):
        if cmds.objExists('%s.POSE' % node ):
            return True
        
        return False

    def set_pose(self, pose_name):
        
        if not cmds.objExists('%s.description' % pose_name):
            return
        
        self.description = cmds.getAttr('%s.description' % pose_name)
        self.mesh_index = cmds.getAttr('%s.meshIndex' % pose_name)
        
        self.pose_control = pose_name
        
        self._refresh_pose_control()
        self._refresh_meshes()

    def goto_pose(self):
        store = util.StoreControlData(self.pose_control)
        store.eval_data()
    
    def create(self):
        top_group = self._create_top_group()
        
        pose_control = self._create_pose_control()
        self.pose_control = pose_control
        
        cmds.parent(pose_control, top_group)
        
        store = util.StoreControlData(pose_control)
        store.set_data()
        
        return pose_control
        
    def rename(self, description):
        
        meshes = self.get_target_meshes()
        
        old_description = self.description
        
        for mesh in meshes:
            blendshape_node = self._get_blendshape(mesh)
            
            if blendshape_node:
                blend = blendshape.BlendShape(blendshape_node)
                blend.rename_target(old_description, description)

        self._set_description(description)
        
        self._rename_nodes()
        
        self.pose_control = cmds.rename(self.pose_control, self._get_name())
           
        return self.pose_control
       
    def delete(self):
        
        self.delete_blend_input()
        
        self._delete_connected_nodes()
            
        cmds.delete(self.pose_control)
    
    def select(self):
        cmds.select(self.pose_control)
        
        store = util.StoreControlData(self.pose_control)
        store.eval_data()
        

    
        
    #--- mesh
      
    def has_a_mesh(self):
        if self._get_mesh_message_attributes():
            return True
        
        return False
        
    def set_mesh_index(self, index):
        mesh_count = self._get_mesh_count()
        
        if index > mesh_count-1:
            index = 0
            
        cmds.setAttr('%s.meshIndex' % self.pose_control, l = False)
        self.mesh_index = index
        cmds.setAttr('%s.meshIndex' % self.pose_control, index)
        cmds.setAttr('%s.meshIndex' % self.pose_control, l = True)
        
    def add_mesh(self, mesh, toggle_vis = True):
        
        if mesh.find('.vtx'):
            mesh = mesh.split('.')[0]
            
        if not util.get_mesh_shape(mesh):
            return False
        
        if self._check_if_mesh_connected(mesh):
            return False
        
        if self._check_if_mesh_is_child(mesh):
            return False
        
        target_meshes = self.get_target_meshes()
        
        print 'adding', mesh, 'target meshes', target_meshes
        
        basename_mesh = util.get_basename(mesh)
        
        if mesh in target_meshes:
            print mesh, 'was not in taget meshes'
            index = self.get_target_mesh_index(mesh)
            return self.get_mesh(index)
        
        pose_mesh = cmds.duplicate(mesh, n = util.inc_name('mesh_%s_1' % self.pose_control))[0]
        
        self._create_shader(pose_mesh)
        
        util.unlock_attributes(pose_mesh)
        
        cmds.parent(pose_mesh, self.pose_control)
        
        self._connect_mesh(pose_mesh)
        
        index = self._get_mesh_count()
        
        self.set_mesh_index(index-1)
        
        string_var = util.MayaStringVariable('mesh_pose_source')
        string_var.create(pose_mesh)
        string_var.set_value(mesh)

        #self._hide_meshes()

        if toggle_vis:
            self.toggle_vis()
        
        return pose_mesh
        
    def get_mesh(self, index):
        
        mesh_attributes = self._get_mesh_message_attributes()
        
        if not mesh_attributes:
            return
        
        mesh = util.get_attribute_input('%s.%s' % (self.pose_control, mesh_attributes[index]), True)
        
        return mesh
    
    def get_target_meshes(self):
        meshes = []
        
        for inc in range(0, self._get_mesh_count()):
            mesh = self.get_mesh(inc)
            
            mesh = self.get_target_mesh(mesh)
            #mesh = cmds.getAttr('%s.mesh_pose_source' % mesh)
            if mesh:
                meshes.append(mesh)
            
        return meshes
        
    def get_target_mesh(self, mesh):
        if cmds.objExists('%s.mesh_pose_source' % mesh):
            mesh = cmds.getAttr('%s.mesh_pose_source' % mesh)
            
            if not cmds.objExists(mesh):
                
                mesh = util.get_basename(mesh)
                
        return mesh
        
    def get_target_mesh_index(self, target_mesh):
        
        
        
        
        target_meshes = self.get_target_meshes()
        
        print 'here`##########################'
        print target_mesh
        print target_meshes
        
        inc = 0
        
        for target_mesh_test in target_meshes:
            if target_mesh == target_mesh_test:
                return inc
            
            inc += 1
    
    def get_mesh_index(self, mesh):
        
        attributes = self._get_mesh_message_attributes()
        
        inc = 0
        
        for attribute in attributes:
            stored_mesh = self._get_named_message_attribute(attribute)
            
            if stored_mesh == mesh:
                return inc
            
            inc += 1       
        
    @util.undo_chunk
    def reset_target_meshes(self):
        
        count = self._get_mesh_count()
        
        for inc in range(0, count):
            
            deformed_mesh = self.get_mesh(inc)
            original_mesh = self.get_target_mesh(deformed_mesh)
            
            cmds.delete(deformed_mesh, ch = True)
            
            blendshape_node = self._get_blendshape(original_mesh)
            
            blend = blendshape.BlendShape()
                    
            if blendshape_node:
                blend.set(blendshape_node)
                
            blend.set_envelope(0)    
            
            temp_dup = cmds.duplicate(original_mesh)[0]
            
            #using blendshape because of something that looks like a bug in Maya 2015
            temp_blend = util.quick_blendshape(temp_dup, deformed_mesh)
            
            cmds.delete(temp_blend, ch = True)
            cmds.delete(temp_dup)
            
            blend.set_envelope(1)  
            
        self.create_blend() 

    def visibility_off(self, mesh = None, view_only = False):
        
        if not mesh:
            mesh = self.get_mesh(self.mesh_index)
        
        self._create_shader(mesh)
        
        cmds.hide(mesh)

        cmds.showHidden(self.get_target_mesh(mesh))
    
        if not view_only:    
            self.create_blend()
            
        
    def visibility_on(self, mesh):
        if not mesh:
            mesh = self.get_mesh(self.mesh_index)
        
        self._create_shader(mesh)
        
        cmds.showHidden(mesh)
        
        cmds.hide(self.get_target_mesh(mesh))
            
    def toggle_vis(self, view_only = False):
        mesh = self.get_mesh(self.mesh_index)
        
        if cmds.getAttr('%s.visibility' % mesh) == 1:
            self.visibility_off(mesh, view_only)
            return
        
        if cmds.getAttr('%s.visibility' % mesh) == 0:
            self.visibility_on(mesh)
            return
        
        
    #--- blend
        
    def create_all_blends(self):
        
        count = self._get_mesh_count()
        
        pose = True
        
        for inc in range(0, count):
            
            if inc > 0:
                pose = False
                
            self.create_blend(goto_pose = pose, mesh_index = inc)
        
    def create_blend(self, goto_pose = True, mesh_index = None):
        
        mesh = self._get_current_mesh(mesh_index)
        
        if not mesh:
            return
            
        target_mesh = self.get_target_mesh(mesh)
        
        if not target_mesh:
            RuntimeError('Mesh index %s, has no target mesh' % mesh_index)
            return
        
        if goto_pose:
            self.goto_pose()
        
        blend = blendshape.BlendShape()
        
        blendshape_node = self._get_blendshape(target_mesh)
        
        if blendshape_node:
            blend.set(blendshape_node)
        
        if not blendshape_node:
            blend.create(target_mesh)
        
        #blend.set_envelope(0)
        self.disconnect_blend()
        
        blend.set_weight(self.pose_control, 0)
        offset = util.chad_extract_shape(target_mesh, mesh)
        blend.set_weight(self.pose_control, 1)
        
        if blend.is_target(self.pose_control):
            blend.replace_target(self.pose_control, offset)
        
        if not blend.is_target(self.pose_control):
            blend.create_target(self.pose_control, offset)
        
        self.connect_blend()
        #blend.set_envelope(1)
                    
        util.disconnect_attribute('%s.%s' % (blend.blendshape, self.pose_control))
            
        if not cmds.isConnected('%s.weight' % self.pose_control, '%s.%s' % (blend.blendshape, self.pose_control)):
            
            cmds.connectAttr('%s.weight' % self.pose_control, '%s.%s' % (blend.blendshape, self.pose_control))
        
        cmds.delete(offset)
        
    def connect_blend(self, mesh_index = None):
        mesh = None
        
        if mesh_index == None:
            mesh = self.get_mesh(self.mesh_index)
        if mesh_index != None:
            mesh = self.get_mesh(mesh_index)
            
        if not mesh:
            return
        
        blend = blendshape.BlendShape()
        
        target_mesh = self.get_target_mesh(mesh)
        
        blendshape_node = self._get_blendshape(target_mesh)
        
        if blendshape_node:
            blend.set(blendshape_node)
        
        if self.blend_input and blend.is_target(self.pose_control):
            cmds.connectAttr(self.blend_input, '%s.%s' % (blend.blendshape, self.pose_control))
            self.blend_input = None
        """       
        if blend.is_target(self.pose_control):
            if not cmds.isConnected('%s.weight' % self.pose_control, '%s.%s' % (blend.blendshape, self.pose_control)):
                cmds.connectAttr('%s.weight' % self.pose_control, '%s.%s' % (blend.blendshape, self.pose_control))
        """     
    def disconnect_blend(self, mesh_index = None):
        mesh = None
        
        if mesh_index == None:
            mesh = self.get_mesh(self.mesh_index)
        if mesh_index != None:
            mesh = self.get_mesh(mesh_index)
            
        if not mesh:
            return
        
        blend = blendshape.BlendShape()
        
        target_mesh = self.get_target_mesh(mesh)
        
        blendshape_node = self._get_blendshape(target_mesh)
        
        if blendshape_node:
            blend.set(blendshape_node)
                
        input = util.get_attribute_input('%s.%s' % (blend.blendshape, self.pose_control))
                
        self.blend_input = input
                
        if input:
            util.disconnect_attribute('%s.%s' % (blend.blendshape, self.pose_control))
                
        #if blend.is_target(self.pose_control):
        #    if cmds.isConnected('%s.weight' % self.pose_control, '%s.%s' % (blend.blendshape, self.pose_control)):
        #        cmds.disconnectAttr('%s.weight' % self.pose_control, '%s.%s' % (blend.blendshape, self.pose_control))
       
    
    def delete_blend_input(self):
        
        outputs = util.get_attribute_outputs('%s.weight' % self.pose_control)
        
        if outputs:
            for output in outputs:
                if cmds.nodeType(output) == 'multiplyDivide':
                    
                    node = output.split('.')
                
                    found = None
                    
                    if len(node) == 2:
                        node = node[0]
                        found = node
                    
                    if found:
                        
                        output = util.get_attribute_outputs('%s.outputX' % found)
                    
                        if output and len(output) == 1:
                            output = output[0]
                
                if cmds.nodeType(output) == 'blendShape':
                    split_output = output.split('.')
                    
                    blend = blendshape.BlendShape(split_output[0])
                    
                    blend.remove_target(split_output[1])
        
    def get_blendshape(self, mesh_index = None):
        
        mesh = None
        
        if mesh_index == None:
            mesh = self.get_mesh(self.mesh_index)
        if mesh_index != None:
            mesh = self.get_mesh(mesh_index)
            
        if not mesh:
            return
        
        target_mesh = self.get_target_mesh(mesh)
        
        blendshape_node = self._get_blendshape(target_mesh)
        
        return blendshape_node
        
    #--- attributes
        
    def set_target_name(self, string_value):
        
        self.target_name = string_value
        
        if not cmds.objExists('%s.targetName' % self.pose_control):
            cmds.addAttr(self.pose_control, ln = 'targetName', dt = 'string')
        
        if string_value == None:
            return
        
        cmds.setAttr('%s.targetName' % self.pose_control, string_value, type = 'string')
        
    def get_target_name(self):
        
        target_name = cmds.getAttr('%s.targetName' % self.pose_control)
        
        return target_name
        
    def set_inbetween_weight(self, value):
        
        self.inbetween_weight = value
        
        if not cmds.objExists('%s.inbetweenWeight' % self.pose_control):
            cmds.addAttr(self.pose_control, ln = 'inbetweenWeight', at = 'float', min = -1, max = 1)
        
        if value == None:
            return
        
        cmds.setAttr('%s.inbetweenWeight' % self.pose_control, value)
        
    def get_inbetween_weight(self):
        
        return cmds.getAttr('%s.inbetweenWeight' % self.pose_control)

class PoseNoReader(BasePoseControl):
    
    def _pose_type(self):
        return 'no reader'
    
    def _create_attributes(self, control):
        
        super(PoseNoReader, self)._create_attributes(control)
        
        pose_input = util.MayaStringVariable('weightInput')
        #pose_input.set_locked(True)
        pose_input.create(control)
    
    def _multiply_weight(self, destination):

        multiply = self._get_named_message_attribute('multiplyDivide1')
        
        if not multiply:
            multiply = self._create_node('multiplyDivide')
        
            cmds.connectAttr('%s.weight' % self.pose_control, '%s.input1X' % multiply)
            cmds.connectAttr('%s.enable' % self.pose_control, '%s.input2X' % multiply)
        
        cmds.connectAttr('%s.outputX' % multiply, destination)
    
    def _connect_weight_input(self, attribute):
        
        weight_attr = '%s.weight' % self.pose_control
        
        input_attr = util.get_attribute_input(weight_attr)
        
        if attribute == input_attr:
            return
        
        cmds.connectAttr(attribute, weight_attr)
    
    def create_blend(self, goto_pose = True, mesh_index = None):
        
        mesh = self._get_current_mesh(mesh_index)
        
        if not mesh:
            return
            
        target_mesh = self.get_target_mesh(mesh)
        
        if not target_mesh:
            RuntimeError('Mesh index %s, has no target mesh' % mesh_index)
            return
        
        if goto_pose:
            self.goto_pose()
        
        blend = blendshape.BlendShape()
        
        blendshape_node = self._get_blendshape(target_mesh)
        
        if blendshape_node:
            blend.set(blendshape_node)
        
        if not blendshape_node:
            blend.create(target_mesh)
        
        #blend.set_envelope(0)
        self.disconnect_blend()
        blend.set_weight(self.pose_control, 0)
        
        offset = util.chad_extract_shape(target_mesh, mesh)
        
        blend.set_weight(self.pose_control, 1)
        self.connect_blend()
        #blend.set_envelope(1)
        
        if blend.is_target(self.pose_control):
            blend.replace_target(self.pose_control, offset)
        
        if not blend.is_target(self.pose_control):
            blend.create_target(self.pose_control, offset)
                
        blend_attr = '%s.%s' % (blend.blendshape, self.pose_control)
        weight_attr = '%s.weight' % self.pose_control
        input_attr = util.get_attribute_input(blend_attr)
            
        util.disconnect_attribute(blend_attr)
            
        if input_attr:
            weight_input = util.get_attribute_input(weight_attr)
            
            if not weight_input:
                
                multiply_node = self._get_named_message_attribute('multiplyDivide1')
                
                pose_input = input_attr.split('.')[0]
                
                if not pose_input == multiply_node:
                    
                    self.set_input(input_attr)
                    #self._connect_weight_input(input_attr)
                    
                
                #if multiply_node:
                #    self.set_input(input_attr)
        
        if input_attr != weight_attr:
            
            self._multiply_weight(blend_attr)
        
        cmds.delete(offset)
        
    
    def set_input(self, attribute):
        
        if attribute == 'multiplyDivide_pose_no_reader_1.outputX':
            raise
        
        self.weight_input = attribute
        
        if not cmds.objExists('%s.weightInput' % self.pose_control):
            
            cmds.addAttr(self.pose_control, ln = 'weightInput', dt = 'string')
            
            if not attribute:
                attribute = ''
        
        cmds.setAttr('%s.weightInput' % self.pose_control, attribute, type = 'string')
        
        if not util.is_attribute_numeric(attribute):
            util.disconnect_attribute('%s.weight' % self.pose_control)
            return
        
        self._connect_weight_input(attribute)
        
        
    def get_input(self):
        
        attribute = util.get_attribute_input('%s.weightInput' % self.pose_control, node_only = True)
        
        if attribute:
            return attribute
        
        return cmds.getAttr('%s.weightInput' % self.pose_control)

    def attach(self):
        attribute = self.get_input()
        self.set_input(attribute)
        
    def detach(self):
        
        util.disconnect_attribute('%s.weight' % self.pose_control)
        

        
    def mirror(self):
        
        description = self.description
        
        skin = None
        blendshape_node = None
        
        if not description:
            self._set_description(self.pose_control)
        
        if description:
            description = description.replace(' ', '_')
        
        other_pose = self._replace_side(self.pose_control)
        
        if not cmds.objExists(other_pose):
            return
        
        other_pose_instance = PoseNoReader()
        other_pose_instance.set_pose(other_pose)
        
        other_target_meshes = []
        
        input_meshes = {}

        for inc in range(0, self._get_mesh_count()):
            mesh = self.get_mesh(inc)
            target_mesh = self.get_target_mesh(mesh)
            
            index = other_pose_instance.get_target_mesh_index(target_mesh)
            
            if index != None:
                other_mesh = other_pose_instance.get_mesh(index)
            
            if index == None:
                other_mesh = other_pose_instance.add_mesh(target_mesh)
            
            other_mesh = target_mesh
            
            if not other_mesh:
                continue
            
            other_mesh_duplicate = cmds.duplicate(other_mesh, n = 'duplicate_corrective_temp_%s' % other_mesh)[0]
            
            split_name = target_mesh.split('|')
            
            other_target_mesh = self._replace_side(split_name[-1])
            
            if not other_target_mesh or not cmds.objExists(other_target_mesh):
                other_target_mesh = target_mesh
            
            
            skin = util.find_deformer_by_type(target_mesh, 'skinCluster')
            blendshape_node = util.find_deformer_by_type(target_mesh, 'blendShape')
            
            cmds.setAttr('%s.envelope' % skin, 0)
            cmds.setAttr('%s.envelope' % blendshape_node, 0)
            
            other_target_mesh_duplicate = cmds.duplicate(other_target_mesh, n = other_target_mesh)[0]
            
            home = cmds.duplicate(target_mesh, n = 'home')[0]

            mirror_group = cmds.group(em = True)
            cmds.parent(home, mirror_group)
            cmds.parent(other_mesh_duplicate, mirror_group)
            cmds.setAttr('%s.scaleX' % mirror_group, -1)
            
            
            util.create_wrap(home, other_target_mesh_duplicate)
            
            cmds.blendShape(other_mesh_duplicate, home, foc = True, w = [0, 1])
            
            cmds.delete(other_target_mesh_duplicate, ch = True)
            
            input_meshes[other_target_mesh] = other_target_mesh_duplicate
            other_target_meshes.append(other_target_mesh)        
        
            cmds.delete(mirror_group, other_mesh_duplicate)
        
            #print home
            
        
        if skin:
            cmds.setAttr('%s.envelope' % skin, 1)
        if blendshape_node:
            cmds.setAttr('%s.envelope' % blendshape_node, 1)
        
        other_pose_instance.goto_pose()
        
        inc = 0
        
        for mesh in other_target_meshes:
            
            index = other_pose_instance.get_target_mesh_index(mesh)
            if index == None:
                continue
            
            input_mesh = other_pose_instance.get_mesh(index)
            
            
            if not input_mesh:
                continue
            
            fix_mesh = input_meshes[mesh]
            
            cmds.blendShape(fix_mesh, input_mesh, foc = True, w = [0,1])
            
            
            other_pose_instance.create_blend(False)
            
            cmds.delete(input_mesh, ch = True)
            cmds.delete(fix_mesh)
            inc += 1
        
        return other_pose_instance.pose_control

class PoseControl(BasePoseControl):
    def __init__(self, transform = None, description = 'pose'):
                
        super(PoseControl, self).__init__(description)
        
        if transform:
            transform = transform.replace(' ', '_')
        
        self.transform = transform
        
        self.axis = 'X'
    
    def _pose_type(self):
        return 'cone'
    
    def _get_color_for_axis(self):
        if self.axis == 'X':
            return 13
            
        if self.axis == 'Y':
            return 14    
            
        if self.axis == 'Z':
            return 6
    
    def _get_axis_rotation(self):
        if self.axis == 'X':
            return [0,0,-90]
        
        if self.axis == 'Y':
            return [0,0,0]
        
        if self.axis == 'Z':
            return [90,0,0]
          
    def _get_twist_axis(self):
        if self.axis == 'X':
            return [0,1,0]
        
        if self.axis == 'Y':
            return [1,0,0]
        
        if self.axis == 'Z':
            return [1,0,0]
        
    def _get_pose_axis(self):
        if self.axis == 'X':
            return [1,0,0]
        
        if self.axis == 'Y':
            return [0,1,0]
        
        if self.axis == 'Z':
            return [0,0,1]
        
    def _create_pose_control(self):
        pose_control = super(PoseControl, self)._create_pose_control()
         
        self._position_control(pose_control)
        
            
        match = util.MatchSpace(self.transform, pose_control)
        match.translation_rotation()
        
        parent = cmds.listRelatives(self.transform, p = True)
        
        if parent:
            cmds.parentConstraint(parent[0], pose_control, mo = True)
            cmds.setAttr('%s.parent' % pose_control, parent[0], type = 'string')
        
        return pose_control
        
    def _position_control(self, control):
        control = util.Control(control)
        
        control.set_curve_type('pin_point')
        
        control.rotate_shape(*self._get_axis_rotation())
        
        scale = self.scale + 5
        control.scale_shape(scale,scale,scale)
        
        control.color( self._get_color_for_axis() )
        
    def _set_axis_vectors(self):
        pose_axis = self._get_pose_axis()
        
        self._lock_axis_vector_attributes(False)
        
        cmds.setAttr('%s.axisRotateX' % self.pose_control, pose_axis[0])
        cmds.setAttr('%s.axisRotateY' % self.pose_control, pose_axis[1])
        cmds.setAttr('%s.axisRotateZ' % self.pose_control, pose_axis[2])
        
        twist_axis = self._get_twist_axis()
        
        cmds.setAttr('%s.axisTwistX' % self.pose_control, twist_axis[0])
        cmds.setAttr('%s.axisTwistY' % self.pose_control, twist_axis[1])
        cmds.setAttr('%s.axisTwistZ' % self.pose_control, twist_axis[2])
        
        self._lock_axis_vector_attributes(True)
        
    def _lock_axis_vector_attributes(self, bool_value):
        axis = ['X','Y','Z']
        attributes = ['axisTwist', 'axisRotate']
        
        for a in axis:
            for attribute in attributes:
                cmds.setAttr('%s.%s%s' % (self.pose_control, attribute, a), l = bool_value)
        
    def _create_attributes(self, control):
        super(PoseControl, self)._create_attributes(control)
    
        cmds.addAttr(control, ln = 'translation', at = 'double', k = True, dv = 1)
        cmds.addAttr(control, ln = 'rotation', at = 'double', k = True, dv = 1)
        
        cmds.addAttr(control, ln = 'twistOffOn', at = 'double', k = True, dv = 1, min = 0, max = 1)
        cmds.addAttr(control, ln = 'maxDistance', at = 'double', k = True, dv = 1)
        cmds.addAttr(control, ln = 'maxAngle', at = 'double', k = True, dv = 90)
        cmds.addAttr(control, ln = 'maxTwist', at = 'double', k = True, dv = 90)
        
        title = util.MayaEnumVariable('AXIS_ROTATE')
        title.create(control)
        
        pose_axis = self._get_pose_axis()
        
        cmds.addAttr(control, ln = 'axisRotateX', at = 'double', k = True, dv = pose_axis[0])
        cmds.addAttr(control, ln = 'axisRotateY', at = 'double', k = True, dv = pose_axis[1])
        cmds.addAttr(control, ln = 'axisRotateZ', at = 'double', k = True, dv = pose_axis[2])
        
        title = util.MayaEnumVariable('AXIS_TWIST')
        title.create(control)
        
        twist_axis = self._get_twist_axis()
        
        cmds.addAttr(control, ln = 'axisTwistX', at = 'double', k = True, dv = twist_axis[0])
        cmds.addAttr(control, ln = 'axisTwistY', at = 'double', k = True, dv = twist_axis[1])
        cmds.addAttr(control, ln = 'axisTwistZ', at = 'double', k = True, dv = twist_axis[2])
        
        cmds.addAttr(control, ln = 'joint', dt = 'string')
        
        cmds.setAttr('%s.joint' % control, self.transform, type = 'string')
        
        cmds.addAttr(control, ln = 'parent', dt = 'string')
        
        self._lock_axis_vector_attributes(True)
         
    #--- math nodes 
        
    def _create_distance_between(self):
        distance_between = self._create_node('distanceBetween')
        
        cmds.connectAttr('%s.worldMatrix' % self.pose_control, 
                         '%s.inMatrix1' % distance_between)
            
        cmds.connectAttr('%s.worldMatrix' % self.transform, 
                         '%s.inMatrix2' % distance_between)
        
        return distance_between
        
        
    def _create_multiply_matrix(self, moving_transform, pose_control):
        multiply_matrix = self._create_node('multMatrix')
        
        cmds.connectAttr('%s.worldMatrix' % moving_transform, '%s.matrixIn[0]' % multiply_matrix)
        cmds.connectAttr('%s.worldInverseMatrix' % pose_control, '%s.matrixIn[1]' % multiply_matrix)
        
        return multiply_matrix
        
    def _create_vector_matrix(self, multiply_matrix, vector):
        vector_product = self._create_node('vectorProduct')
        
        cmds.connectAttr('%s.matrixSum' % multiply_matrix, '%s.matrix' % vector_product)
        cmds.setAttr('%s.input1X' % vector_product, vector[0])
        cmds.setAttr('%s.input1Y' % vector_product, vector[1])
        cmds.setAttr('%s.input1Z' % vector_product, vector[2])
        cmds.setAttr('%s.operation' % vector_product, 3)
        
        return vector_product
        
    def _create_angle_between(self, vector_product, vector):
        angle_between = self._create_node('angleBetween')
        
        cmds.connectAttr('%s.outputX' % vector_product, '%s.vector1X' % angle_between)
        cmds.connectAttr('%s.outputY' % vector_product, '%s.vector1Y' % angle_between)
        cmds.connectAttr('%s.outputZ' % vector_product, '%s.vector1Z' % angle_between)
        
        cmds.setAttr('%s.vector2X' % angle_between, vector[0])
        cmds.setAttr('%s.vector2Y' % angle_between, vector[1])
        cmds.setAttr('%s.vector2Z' % angle_between, vector[2])
        
        return angle_between
        
    def _remap_value_angle(self, angle_between):
        remap = self._create_node('remapValue')
        
        cmds.connectAttr('%s.angle' % angle_between, '%s.inputValue' % remap)
        
        cmds.setAttr('%s.value[0].value_Position' % remap, 0)
        cmds.setAttr('%s.value[0].value_FloatValue' % remap, 1)
        
        cmds.setAttr('%s.value[1].value_Position' % remap, 1)
        cmds.setAttr('%s.value[1].value_FloatValue' % remap, 0)
        
        cmds.setAttr('%s.inputMax' % remap, 180)
        
        return remap
    
    def _remap_value_distance(self, distance_between):
        remap = cmds.createNode('remapValue', n = 'remapValue_distance_%s' % self.description)
        
        cmds.connectAttr('%s.distance' % distance_between, '%s.inputValue' % remap)
        
        cmds.setAttr('%s.value[0].value_Position' % remap, 0)
        cmds.setAttr('%s.value[0].value_FloatValue' % remap, 1)
        
        cmds.setAttr('%s.value[1].value_Position' % remap, 1)
        cmds.setAttr('%s.value[1].value_FloatValue' % remap, 0)
        
        cmds.setAttr('%s.inputMax' % remap, 1)
        
        return remap        
        
    def _multiply_remaps(self, remap, remap_twist):
        
        multiply = self._create_node('multiplyDivide')
        
        cmds.connectAttr('%s.outValue' % remap, '%s.input1X' % multiply)
        cmds.connectAttr('%s.outValue' % remap_twist, '%s.input2X' % multiply)
        
        blend = self._create_node('blendColors')
        
        cmds.connectAttr('%s.outputX' % multiply, '%s.color1R' % blend)
        cmds.connectAttr('%s.outValue' % remap, '%s.color2R' % blend)
        
        
        cmds.connectAttr('%s.twistOffOn' % self.pose_control, ' %s.blender' % blend)
        
        return blend
    
    def _create_pose_math_nodes(self, multiply_matrix, axis):
        vector_product = self._create_vector_matrix(multiply_matrix, axis)
        angle_between = self._create_angle_between(vector_product, axis)
        
        if self._get_pose_axis() == axis:
            cmds.connectAttr('%s.axisRotateX' % self.pose_control, '%s.input1X' % vector_product)
            cmds.connectAttr('%s.axisRotateY' % self.pose_control, '%s.input1Y' % vector_product)
            cmds.connectAttr('%s.axisRotateZ' % self.pose_control, '%s.input1Z' % vector_product)
            
            cmds.connectAttr('%s.axisRotateX' % self.pose_control, '%s.vector2X' % angle_between)
            cmds.connectAttr('%s.axisRotateY' % self.pose_control, '%s.vector2Y' % angle_between)
            cmds.connectAttr('%s.axisRotateZ' % self.pose_control, '%s.vector2Z' % angle_between)
            
        if self._get_twist_axis() == axis:
            cmds.connectAttr('%s.axisTwistX' % self.pose_control, '%s.input1X' % vector_product)
            cmds.connectAttr('%s.axisTwistY' % self.pose_control, '%s.input1Y' % vector_product)
            cmds.connectAttr('%s.axisTwistZ' % self.pose_control, '%s.input1Z' % vector_product)
            
            cmds.connectAttr('%s.axisTwistX' % self.pose_control, '%s.vector2X' % angle_between)
            cmds.connectAttr('%s.axisTwistY' % self.pose_control, '%s.vector2Y' % angle_between)
            cmds.connectAttr('%s.axisTwistZ' % self.pose_control, '%s.vector2Z' % angle_between)            
        
        remap = self._remap_value_angle(angle_between)
        
        return remap
        
    def _create_pose_math(self, moving_transform, pose_control):
        multiply_matrix = self._create_multiply_matrix(moving_transform, pose_control)
        
        pose_axis = self._get_pose_axis()
        twist_axis = self._get_twist_axis()
        
        remap = self._create_pose_math_nodes(multiply_matrix, pose_axis)
        remap_twist = self._create_pose_math_nodes(multiply_matrix, twist_axis)
        
        blend = self._multiply_remaps(remap, remap_twist)
        
        cmds.connectAttr('%s.maxAngle' % pose_control, '%s.inputMax' % remap)
        cmds.connectAttr('%s.maxTwist' % pose_control, '%s.inputMax' % remap_twist)
        
        distance = self._create_distance_between()
        remap_distance = self._remap_value_distance(distance)
        
        cmds.connectAttr('%s.maxDistance' % self.pose_control, '%s.inputMax' % remap_distance)
        
        self._key_output('%s.outValue' % remap_distance, '%s.translation' % self.pose_control)
        self._key_output('%s.outputR' % blend, '%s.rotation' % self.pose_control)
        
    def _key_output(self, output_attribute, input_attribute, values = [0,1]):
        
        cmds.setDrivenKeyframe(input_attribute,
                               cd = output_attribute, 
                               driverValue = values[0], 
                               value = 0, 
                               itt = 'linear', 
                               ott = 'linear')
    
        cmds.setDrivenKeyframe(input_attribute,
                               cd = output_attribute,  
                               driverValue = values[1], 
                               value = 1, 
                               itt = 'linear', 
                               ott = 'linear')  
    
    def _multiply_weight(self):
        
        multiply = self._create_node('multiplyDivide')
        
        cmds.connectAttr('%s.translation' % self.pose_control, '%s.input1X' % multiply)
        cmds.connectAttr('%s.rotation' % self.pose_control, '%s.input2X' % multiply)
        
        multiply_offset = self._create_node('multiplyDivide')
        
        cmds.connectAttr('%s.outputX' % multiply, '%s.input1X' % multiply_offset)
        cmds.connectAttr('%s.enable' % self.pose_control, '%s.input2X' % multiply_offset)
        
        cmds.connectAttr('%s.outputX' % multiply_offset, '%s.weight' % self.pose_control)

    def _get_parent_constraint(self):
        constraint = util.ConstraintEditor()
        constraint_node = constraint.get_constraint(self.pose_control, 'parentConstraint')
        
        return constraint_node 
        
    def set_axis(self, axis_name):
        self.axis = axis_name
        self._position_control(self.pose_control)
        
        self._set_axis_vectors()
        
    def get_transform(self):
        matrix = self._get_named_message_attribute('multMatrix1')
        
        transform = util.get_attribute_input('%s.matrixIn[0]' % matrix, True)
        
        if not transform:
            transform = cmds.getAttr('%s.joint' % self.pose_control)
        
        self.transform = transform
        
        return transform

    def get_parent(self):
        
        constraint_node = self._get_parent_constraint()
        
        parent = None
        
        if constraint_node:
            constraint = util.ConstraintEditor()
            targets = constraint.get_targets(constraint_node)
            if targets:
                parent = targets[0]
        
        if not parent:
            parent = cmds.getAttr('%s.parent' % self.pose_control)
        
        return parent 
    
    def set_transform(self, transform, set_string_only = False):
        if not cmds.objExists('%s.joint' % self.pose_control):
            cmds.addAttr(self.pose_control, ln = 'joint', dt = 'string')
        
        cmds.setAttr('%s.joint' % self.pose_control, transform, type = 'string')
        
        if not set_string_only:
            matrix = self._get_named_message_attribute('multMatrix1')
            distance = self._get_named_message_attribute('distanceBetween1')
        
            if not cmds.isConnected('%s.worldMatrix' % transform, '%s.matrixIn[0]' % matrix):
                cmds.connectAttr('%s.worldMatrix' % transform, '%s.matrixIn[0]' % matrix)
            if not cmds.isConnected('%s.worldMatrix' % transform, '%s.inMatrix2' % distance):
                cmds.connectAttr('%s.worldMatrix' % transform, '%s.inMatrix2' % distance)
                
    def set_parent(self, parent, set_string_only = False):
        if not cmds.objExists('%s.parent' % self.pose_control):
            cmds.addAttr(self.pose_control, ln = 'parent', dt = 'string')
            
        if not parent:
            parent = ''
        
        cmds.setAttr('%s.parent' % self.pose_control, parent, type = 'string')
    
        if not set_string_only:
            
            constraint = self._get_parent_constraint()
            cmds.delete(constraint)    
            
            if parent:
                cmds.parentConstraint(parent, self.pose_control, mo = True)
    
    def detach(self):
        
        parent = self.get_parent()
        self.set_parent(parent, True)
        
        transform = self.get_transform()
        self.set_transform(transform, True)
        
        constraint = self._get_parent_constraint()
        if constraint:
            cmds.delete(constraint)
        
        self.delete_blend_input()
            
    def attach(self):
        transform = self.get_transform()
        parent = self.get_parent()
        
        self.set_transform(transform)
        self.set_parent(parent)
    
    def create(self):
        pose_control = super(PoseControl, self).create()
        
        self._create_pose_math(self.transform, pose_control)
        self._multiply_weight()
        
        self.pose_control = pose_control
        
        return pose_control
    
    def visibility_off(self, mesh = None, view_only = False):
        super(PoseControl, self).visibility_off(mesh, view_only)
    
    def mirror(self):
        
        transform = self.get_transform()
        
        description = self.description
        
        skin = None
        blendshape_node = None
        
        if not description:
            self._set_description(self.pose_control)
        
        if description:
            description = description.replace(' ', '_')
        
        other_transform = self._replace_side(transform)
        
        if not cmds.objExists(other_transform):
            return
        
        other_pose = self._replace_side(self.pose_control)
        other_description = self._replace_side(description)
        
        if not cmds.objExists(other_pose):
            return
        
        other_target_meshes = []
        input_meshes = {}

        for inc in range(0, self._get_mesh_count()):
            mesh = self.get_mesh(inc)
            
            
            other_mesh = cmds.duplicate(mesh)[0]
            
            new_name = mesh.replace('_L', '_R')
            
            other_mesh = cmds.rename(other_mesh, new_name)
            
            target_mesh = self.get_target_mesh(mesh)
            split_name = target_mesh.split('|')
            other_target_mesh = split_name[-1][:-1] + 'R'
            
            skin = util.find_deformer_by_type(target_mesh, 'skinCluster')
            blendshape_node = util.find_deformer_by_type(target_mesh, 'blendShape')
            
            cmds.setAttr('%s.envelope' % skin, 0)
            cmds.setAttr('%s.envelope' % blendshape_node, 0)
            
            if not cmds.objExists(other_target_mesh):
                other_target_mesh = target_mesh
                
            other_target_mesh_duplicate = cmds.duplicate(other_target_mesh, n = other_target_mesh)[0]
            
            home = cmds.duplicate(target_mesh, n = 'home')[0]

            mirror_group = cmds.group(em = True)
            cmds.parent(home, mirror_group)
            cmds.parent(other_mesh, mirror_group)
            cmds.setAttr('%s.scaleX' % mirror_group, -1)
            
            util.create_wrap(home, other_target_mesh_duplicate)
            
            cmds.blendShape(other_mesh, home, foc = True, w = [0, 1])
            
            cmds.delete(other_target_mesh_duplicate, ch = True)
            
            input_meshes[other_target_mesh] = other_target_mesh_duplicate
            other_target_meshes.append[other_target_mesh]
            
            cmds.delete(mirror_group, other_mesh)
            
        
        if skin:
            cmds.setAttr('%s.envelope' % skin, 1)
        if blendshape_node:
            cmds.setAttr('%s.envelope' % blendshape_node, 1)
          
        if cmds.objExists(other_pose):
            pose = PoseControl()
            pose.set_pose(other_pose)
            
            pose.goto_pose()
        
        if not cmds.objExists(other_pose):
        
            store = util.StoreControlData(self.pose_control)
            store.eval_mirror_data()
            
            pose = PoseControl(other_transform, other_description)
            pose.create()

        twist_on_value = cmds.getAttr('%s.twistOffOn' % self.pose_control)
        distance_value = cmds.getAttr('%s.maxDistance' % self.pose_control)
        angle_value = cmds.getAttr('%s.maxAngle' % self.pose_control)
        maxTwist_value = cmds.getAttr('%s.maxTwist' % self.pose_control)
        
        cmds.setAttr('%s.twistOffOn' % pose.pose_control, twist_on_value)
        cmds.setAttr('%s.maxDistance' % pose.pose_control, distance_value)
        cmds.setAttr('%s.maxAngle' % pose.pose_control, angle_value)
        cmds.setAttr('%s.maxTwist' % pose.pose_control, maxTwist_value)
        
        inc = 0
        
        for mesh in other_target_meshes:
            pose.add_mesh(mesh, False)
            input_mesh = pose.get_mesh(inc)
            
            fix_mesh = input_meshes[mesh]
            
            cmds.blendShape(fix_mesh, input_mesh, foc = True, w = [0,1])
            
            pose.create_blend(False)
            
            cmds.delete(input_mesh, ch = True)
            cmds.delete(fix_mesh)
            inc += 1
        
        return pose.pose_control
                

class ComboControl(BasePoseControl):
    def __init__(self, pose_list = None, description = 'combo'):
        super(ComboControl, self).__init__(description)
        
        self.pose_list = pose_list
        
    def _connect_poses(self):
        last_multiply = None
        
        for inc in range(0, len( self.pose_list ) ):
            pose = self.pose_list[inc]
            
            self._connect_node(pose, 'pose', inc)
            
            multiply = self._create_node('multiplyDivide')
            
            cmds.connectAttr('%s.weight' % pose, '%s.input1X' % multiply)
            
            if last_multiply:
                cmds.connectAttr('%s.outputX' % last_multiply, '%s.input2X' % multiply)
    
            last_multiply = multiply 
            
        cmds.connectAttr('%s.outputX' % last_multiply, '%s.weight' % self.pose_control)
       
    def create(self):
        
        super(ComboControl, self).create()
        
        self._connect_poses()
