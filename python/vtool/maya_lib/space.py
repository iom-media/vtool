# Copyright (C) 2014 Louis Vottero louis.vot@gmail.com    All rights reserved.

import vtool.util
import api

if vtool.util.is_in_maya():
    import maya.cmds as cmds
    
import core
import attr
    
    #do not import geo
    



class PinXform(object):
    """
    This allows you to pin a transform so that its parent and child are not affected by any edits.
    """
    def __init__(self, xform_name):
        self.xform = xform_name
        self.delete_later = []

    def pin(self):
        """
        Create the pin constraints on parent and children.
        """
        parent = cmds.listRelatives(self.xform, p = True, f = True)
        
        if parent:
            
            parent = parent[0]
            
            
            pin = cmds.duplicate(parent, po = True, n = core.inc_name('pin1'))[0]
            
            try:
                cmds.parent(pin, w = True)
            except:
                pass
            
            #pin = cmds.group(em = True, n = 'pin1')    
            #MatchSpace(parent, pin).translation_rotation()
            
            constraint = cmds.parentConstraint(pin, parent, mo = True)[0]
            self.delete_later.append(constraint)
            self.delete_later.append(pin)
        
        children = cmds.listRelatives(self.xform, f = True)
        
        if not children:
            return
        
        for child in children:
            
            pin = cmds.duplicate(child, po = True, n = core.inc_name('pin1'))[0]
            
            try:
                cmds.parent(pin, w = True)
            except:
                pass
            
            constraint = cmds.parentConstraint(pin, child, mo = True)[0]
            self.delete_later.append(constraint)
            self.delete_later.append(pin)
            
    def unpin(self):
        """
        Remove the pin. This should be run after pin.
        """
        if self.delete_later:
            cmds.delete(self.delete_later)
        
    def get_pin_nodes(self):
        """
        Return
            (list): List of nodes involved in the pinning. Ususally includes constraints and empty groups.
        """
        return self.delete_later

class MatchSpace(object):
    """
    Used to match transformation between two transform node.
    Can be used as follows:
    MatchSpace('transform1', 'transform2').translation_rotation()
    
    Args
        
        source_transform (str): The name of a transform.
        target_transform (str): The name of a transform.
        
    
    """
    
    def __init__(self, source_transform, target_transform):
        self.source_transform = source_transform
        self.target_transform = target_transform
    
    def _get_translation(self):
        return cmds.xform(self.source_transform, q = True, t = True, ws = True)
    
    def _get_rotation(self):
        return cmds.xform(self.source_transform, q = True, ro = True, ws = True)
    
    def _get_rotate_pivot(self):
        return cmds.xform(self.source_transform, q = True, rp = True, os = True)
    
    def _get_scale_pivot(self):
        return cmds.xform(self.source_transform, q = True, sp = True, os = True)
    
    def _get_world_rotate_pivot(self):
        return cmds.xform(self.source_transform, q = True, rp = True, ws = True)
    
    def _get_world_scale_pivot(self):
        return cmds.xform(self.source_transform, q = True, sp = True, ws = True)
    
    def _set_translation(self, translate_vector = []):
        if not translate_vector:
            translate_vector = self._get_translation()
            
        cmds.xform(self.target_transform, t = translate_vector, ws = True)
    
    def _set_rotation(self, rotation_vector = []):
        if not rotation_vector:
            rotation_vector = self._get_rotation()
            
        cmds.xform(self.target_transform, ro = rotation_vector, ws = True)
        
    def _set_rotate_pivot(self, rotate_pivot_vector = []):
        if not rotate_pivot_vector:
            rotate_pivot_vector = self._get_rotate_pivot()
        cmds.xform(self.target_transform, rp = rotate_pivot_vector, os = True)
        
    def _set_world_rotate_pivot(self, rotate_pivot_vector = []):
        if not rotate_pivot_vector:
            rotate_pivot_vector = self._get_world_rotate_pivot()
        cmds.xform(self.target_transform, rp = rotate_pivot_vector, ws = True)
        
    def _set_scale_pivot(self, scale_pivot_vector = []):
        if not scale_pivot_vector:
            scale_pivot_vector = self._get_scale_pivot()
        cmds.xform(self.target_transform, sp = scale_pivot_vector, os = True)
    
    def _set_world_scale_pivot(self, scale_pivot_vector = []):
        if not scale_pivot_vector:
            scale_pivot_vector = self._get_world_scale_pivot()
        cmds.xform(self.target_transform, rp = scale_pivot_vector, ws = True)
        
    def translation(self):
        """
        Match just the translation
        """
        self._set_translation()
        
    def rotation(self):
        """
        Match just the rotation
        """
        self._set_rotation()
        
    def translation_rotation(self):
        """
        Match translation and rotation.
        """
                
        self._set_scale_pivot()
        self._set_rotate_pivot()
        
        self._set_translation()
        
        self._set_rotation()
        
    def translation_to_rotate_pivot(self):
        """
        Match translation of target to the rotate_pivot of source.
        """
        
        translate_vector = self._get_rotate_pivot()
        self._set_translation(translate_vector)
        
    def rotate_scale_pivot_to_translation(self):
        """
        Match the rotate and scale pivot of target to the translation of source.
        """
        
        position = self._get_translation()
        
        cmds.move(position[0], 
                  position[1],
                  position[2], 
                  '%s.scalePivot' % self.target_transform, 
                  '%s.rotatePivot' % self.target_transform, 
                  a = True)
        
    def pivots(self):
        """
        Match the pivots of target to the source.
        """
        self._set_rotate_pivot()
        self._set_scale_pivot()
        
    def world_pivots(self):
        """
        Like pivots, but match in world space.
        """
        self._set_world_rotate_pivot()
        self._set_world_scale_pivot()

class ConstraintEditor():
    """
    Convenience class for editing constraints.
    """
    constraint_parent = 'parentConstraint'
    constraint_point = 'pointConstraint'
    constraint_orient = 'orientConstraint'
    constraint_scale = 'scaleConstraint'
    constraint_aim = 'aimConstraint'
    
    editable_constraints = ['parentConstraint',
                            'pointConstraint',
                            'orientConstraint',
                            'scaleConstraint',
                            'aimConstraint'
                            ]
    
    def _get_constraint_type(self, constraint):
        return cmds.nodeType(constraint)
        
        
        
    def get_weight_names(self, constraint):
        #CBB
        
        constraint_type = self._get_constraint_type(constraint)
        
        if constraint_type == 'scaleConstraint':
        
            found_attributes = []
                
            weights = cmds.ls('%s.target[*]' % constraint)
            
            attributes = cmds.listAttr(constraint, k = True)
                        
            for attribute in attributes:
                for inc in range(0, len(weights)):
                    if attribute.endswith('W%i' % inc):
                        found_attributes.append(attribute)
                        break
            
            return found_attributes
        
        return eval('cmds.%s("%s", query = True, weightAliasList = True, )' % (constraint_type, constraint))

    def get_weight_count(self, constraint):
        """
        Get the number of inputs weights (transforms) feeding int the constraint.
        
        Args
            constraint (str): The name of a constraint.
        """
        return len(cmds.ls('%s.target[*]' % constraint))
    
    def get_constraint(self, transform, constraint_type):
        """
        Find a constraint on the transform.
        
        Args
            transform (str): The name of a transform that is constrained.
            constraint_type (str): The type of constraint to search for. Eg. parentConstraint, orientConstraint, pointConstraint, etc.
            
        Retrun 
            str: The name of the constraint.
        """
        
        constraint = eval('cmds.%s("%s", query = True)' % (constraint_type, transform) )
        
        return constraint
    
    def get_transform(self, constraint):
        """
        Get the transform that the constraint is constraining.
        
        Args
            constraint (str): The name of the constraint.
        
        Return
            str: The name of the transform that is being constrained.
        """
        transform = attr.get_attribute_input('%s.constraintParentInverseMatrix' % constraint)
        
        if not transform:
            return
        
        new_thing = transform.split('.')
        return new_thing[0]
    
    def get_targets(self, constraint):
        """
        Get the transforms influencing the constraint.
        
        Args
            constraint (str): The name of the constraint.
            
        Return
            list: The names of the transforms affecting the constraint.
        """
        transform = self.get_transform(constraint)
        constraint_type = self._get_constraint_type(constraint)
        
        return eval('cmds.%s("%s", query = True, targetList = True)' % (constraint_type,
                                                                        transform) )
        
    def remove_target(self, target, constraint):
        """
        Remove a target from a constraint. 
        This only works if the constraint has all its original connections intact.
        
        Args
            target (str): The name of the transform target to remove.
            constraint (str): The name of a constraint that has target affecting it.
            
        """
        transform = self.get_transform(constraint)
        constraint_type = self._get_constraint_type(constraint)
        
        return eval('cmds.%s("%s", "%s", remove = True)' % (constraint_type,
                                                            target, 
                                                            transform) )
        
    def set_interpolation(self, int_value, constraint):
        """
        Set the interpolation type of the constraint.
        
        Args
            int_value (int): index of the interpolation type.
            constraint (str): The name of a constraint. Probably "parentConstraint" or "orientConstraint".
        """
        
        cmds.setAttr('%s.interpType' % constraint, int_value)
        
    def create_switch(self, node, attribute, constraint):
        """
        Create a switch over all the target weights.
        
        Args
            node (str): The name of the node to add the switch attribute to.
            attribute (str): The name to give the switch attribute.
            constraint (str): The name of the constraint with multiple weight target transforms affecting it.
        """
        
        attributes = self.get_weight_names(constraint)
        
        print 'attributes!', attributes
        
        remap = attr.RemapAttributesToAttribute(node, attribute)
        #remap.set_keyable(False)
        remap.create_attributes(constraint, attributes)
        remap.create()

class IkHandle(object):
    """
    Convenience for creating ik handles.
    
    Args
        name (str): The description to give the node. Name = 'ikHandle_(name)'.
    """
    
    solver_rp = 'ikRPsolver'
    solver_sc = 'ikSCsolver'
    solver_spline = 'ikSplineSolver'
    solver_spring = 'ikSpringSolver'
    
    def __init__(self, name):
        
        if not name:
            name = core.inc_name('ikHandle')
        
        if not name.startswith('ikHandle'):
            self.name = 'ikHandle_%s' % name
            
        self.start_joint = None
        self.end_joint = None
        self.solver_type = self.solver_sc
        self.curve = None
        
        self.ik_handle = None
        self.joints = []
            
    
    def _create_regular_ik(self):
        ik_handle, effector = cmds.ikHandle( name = core.inc_name(self.name),
                                       startJoint = self.start_joint,
                                       endEffector = self.end_joint,
                                       sol = self.solver_type )
                           
        cmds.rename(effector, 'effector_%s' % ik_handle)
        self.ik_handle = ik_handle
        
    def _create_spline_ik(self):
        
        if self.curve:
            
            ik_handle = cmds.ikHandle(name = core.inc_name(self.name),
                                           startJoint = self.start_joint,
                                           endEffector = self.end_joint,
                                           sol = self.solver_type,
                                           curve = self.curve, ccv = False, pcv = False)
            
            cmds.rename(ik_handle[1], 'effector_%s' % ik_handle[0])
            self.ik_handle = ik_handle[0]
            
        if not self.curve:
            
            ik_handle = cmds.ikHandle(name = core.inc_name(self.name),
                                           startJoint = self.start_joint,
                                           endEffector = self.end_joint,
                                           sol = self.solver_type,
                                           scv = False,
                                           pcv = False)
            
            cmds.rename(ik_handle[1], 'effector_%s' % ik_handle[0])
            self.ik_handle = ik_handle[0]
            
            self.curve = ik_handle[2]
            self.curve = cmds.rename(self.curve, core.inc_name('curve_%s' % self.name))
            
            self.ik_handle = ik_handle[0]
        

        
    def set_start_joint(self, joint):
        """
        Set start joint for the ik handle.
        
        Args
            joint (str): The name of the start joint.
        """
        self.start_joint = joint
        
    def set_end_joint(self, joint):
        """
        Set end joint for the ik handle.
        
        Args
            joint (str): The name of the end joint.
        """
        self.end_joint = joint
        
    def set_joints(self, joints_list):
        """
        Set the joints for the ik handle.
        start joint becomes the first entry.
        end joint beomces the las entry.
        
        Args
            joints_list (list): A list of joints.
        """
        self.start_joint = joints_list[0]
        self.end_joint = joints_list[-1]
        self.joints = joints_list
        
    def set_curve(self, curve):
        """
        Set the curve for spline ik.
        
        Args
            curve (str): The name of the curve.
        """
        self.curve = curve
        
    def set_solver(self, type_name):
        """
        Set the solver type.
        
        solver types:
        'ikRPsolver'
        'ikSCsolver'
        'ikSplineSolver'
        'ikSpringSolver'
        
        Args
            type_name (str): The name of the solver type.
        """
        self.solver_type = type_name
    
    def set_full_name(self, fullname):
        """
        Set the full name for the ik handle, no prefixing or formatting added.
        """
        self.name = fullname
    
    def create(self):
        """
        Create the ik handle.
        
        Return
            str: The name of the ik handle.
        """
        
        
        if not self.start_joint or not self.end_joint:
            return
        
        if not self.curve and not self.solver_type == self.solver_spline:
            self._create_regular_ik()
        
        if self.curve or self.solver_type == self.solver_spline:
            self._create_spline_ik()

        
        return self.ik_handle

class OrientJoint(object):
    """
    This will orient the joint using the attributes created with OrientJointAttributes.
    """
    
    def __init__(self, joint_name):
        
        self.joint = joint_name
        self.orient_values = None
        self.aim_vector = [1,0,0]
        self.up_vector = [0,1,0]
        self.world_up_vector = [0,1,0]
        
        self.aim_at = 3
        self.aim_up_at = 0
        
        self.child = None
        self.grand_child = None
        self.parent = None
        self.grand_parent = None
        
        self.delete_later =[]
        self.world_up_vector = self._get_vector_from_axis(1)
        self.up_space_type = 'vector'
        
        self._get_relatives()
        
    def _get_relatives(self):
        
        parent = cmds.listRelatives(self.joint, p = True, f = True)
        
        if parent:
            self.parent = parent[0]
            
            grand_parent = cmds.listRelatives(self.parent, p = True, f = True)
            
            if grand_parent:
                self.grand_parent = grand_parent[0]
                
        children = cmds.listRelatives(self.joint, f = True)
        
        if children:
            self.child = children[0]
            
            grand_children = cmds.listRelatives(self.child, f = True)
            
            if grand_children:
                self.grand_child = grand_children[0]
        
    def _get_vector_from_axis(self, index):
        vectors = [[1,0,0],
                   [0,1,0],
                   [0,0,1],
                   [-1,0,0],
                   [0,-1,0],
                   [0,0,-1],
                   [0,0,0]]
        
        return vectors[index]
        
    def _get_aim_at(self, index):
        
        if index < 3:
            world_aim = cmds.group(em = True, n = 'world_aim')
            MatchSpace(self.joint, world_aim).translation()
            
            if index == 0:
                cmds.move(1,0,0, world_aim, r = True)
            if index == 1:
                cmds.move(0,1,0, world_aim, r = True)
            if index == 2:
                cmds.move(0,0,1, world_aim, r = True)
                
            self.delete_later.append( world_aim )
            return world_aim
            
        if index == 3:
            child_aim = self._get_position_group(self.child)
            return child_aim
            
        if index == 4:
            parent_aim = self._get_position_group(self.parent)
            return parent_aim

        if index == 5:
            aim = self._get_local_group(self.parent)
            return aim
        
    def _get_aim_up_at(self, index):
        
        if index == 1:
            self.up_space_type = 'objectrotation'
            
            return self._get_local_group(self.parent)
        
        if index == 2:
            child_group = self._get_position_group(self.child)
            self.up_space_type = 'object'
            return child_group
        
        if index == 3:
            parent_group = self._get_position_group(self.parent)
            self.up_space_type = 'object'
            return parent_group
        
        if index == 4:
            top = self._get_triangle_group(self.orient_values['triangleTop'])
            mid = self._get_triangle_group(self.orient_values['triangleMid'])
            btm = self._get_triangle_group(self.orient_values['triangleBtm'])
            
            if not top or not mid or not btm:
                
                vtool.util.warning('Could not orient %s fully with current triangle plane settings.' % self.joint)
                return
            
            plane_group = get_group_in_plane(top, mid, btm)
            cmds.move(0,10,0, plane_group, r =True, os = True)
            self.delete_later.append(plane_group)
            self.up_space_type = 'object'
            return plane_group
        
        if index == 5:
            self.up_space_type = 'none'
            
    def _get_local_group(self, transform):
        
        local_up_group = cmds.group(em = True, n = 'local_up_%s' % transform)
        
        MatchSpace(transform, local_up_group).rotation()
        MatchSpace(self.joint, local_up_group).translation()
        
        cmds.move(1,0,0, local_up_group, relative = True, objectSpace = True)
        
        self.delete_later.append(local_up_group)
        
        return local_up_group
    
    def _get_position_group(self, transform):
        position_group = cmds.group(em = True, n = 'position_group')
        
        MatchSpace(transform, position_group).translation()
        
        self.delete_later.append(position_group)
        
        return position_group
        
    def _get_triangle_group(self, index):
        transform = None
        
        if index == 0:
            transform = self.grand_parent
        if index == 1:
            transform = self.parent
        if index == 2:
            transform = self.joint
        if index == 3:
            transform = self.child
        if index == 4:
            transform = self.grand_child
            
        if not transform:
            return
                
        return self._get_position_group(transform)
              
    def _create_aim(self):
                
        if not self.aim_up_at:
            aim = cmds.aimConstraint(self.aim_at, 
                                     self.joint, 
                                     aimVector = self.aim_vector, 
                                     upVector = self.up_vector,
                                     worldUpVector = self.world_up_vector,
                                     worldUpType = self.up_space_type)[0]
                                     
        if self.aim_up_at:
            aim = cmds.aimConstraint(self.aim_at, 
                                     self.joint, 
                                     aimVector = self.aim_vector, 
                                     upVector = self.up_vector,
                                     worldUpObject = self.aim_up_at,
                                     worldUpVector = self.world_up_vector,
                                     worldUpType = self.up_space_type)[0] 
        
        self.delete_later.append(aim)
    
    def _get_values(self):
        
        if not cmds.objExists('%s.ORIENT_INFO' % self.joint):
            return
        
        orient_attributes = attr.OrientJointAttributes(self.joint)
        return orient_attributes.get_values()
        
    def _cleanup(self):
        cmds.delete(self.delete_later)

    def _pin(self):
        
        pin = PinXform(self.joint)
        pin.pin()
        
        nodes = pin.get_pin_nodes()
        self.delete_later += nodes
        
    def _freeze(self):
        children = cmds.listRelatives(self.joint, f = True)
        
        if children:
            
            children = cmds.parent(children, w = True)
        
        cmds.makeIdentity(self.joint, apply = True, r = True, s = True)
        
        if children:
            cmds.parent(children, self.joint)
        
      
    def set_aim_vector(self, vector_list):
        """
        Args
            vector_list (list): [0,0,0] vector that defines what axis should aim.  
            If joint should aim with X axis then vector should be [1,0,0].  If joint should aim with Y axis then [0,1,0], etc.
            If up needs to be opposite of X axis then vector should be [-1,0,0].
        """
        self.aim_vector = vector_list
        
    def set_up_vector(self, vector_list):
        """
        Args
            vector_list (list): [0,0,0] vector that defines what axis should aim up.  
            If joint should aim up with X axis then vector should be [1,0,0].  If joint should aim up with Y axis then [0,1,0], etc.
            If up needs to be opposite of X axis then vector should be [-1,0,0].
        """
        self.up_vector = vector_list
        
    def set_world_up_vector(self, vector_list):
        """
        Args
            vector_list (list): [0,0,0] vector that defines what world up axis be.  
            If world should aim up with X axis then vector should be [1,0,0].  If world should aim up with Y axis then [0,1,0], etc.
            If up needs to be opposite of X axis then vector should be [-1,0,0].
        """
        self.world_up_vector = vector_list
        
    def set_aim_at(self, int_value):
        """
        Set how the joint aims.
        
        Args
            int_value (int): 0 aim at world X, 
                                1 aim at world Y, 
                                2 aim at world Z, 
                                3 aim at immediate child. 
                                4 aim at immediate parent. 
                                5 aim at local parent, which is like aiming at the parent and then reversing direction.
        """
        self.aim_at = self._get_aim_at(int_value)
        
    def set_aim_up_at(self, int_value):
        """
        Set how the joint aims up.
        
        Args
            int_value (int):  0 world,
                                1 parent rotate,
                                2 child position,
                                3 parent position,
                                4 triangle plane, which need to be configured to see which joints in the hierarchy it calculates with.
        """
        self.aim_up_at = self._get_aim_up_at(int_value)
        
    def set_aim_up_at_object(self, name):
        self.aim_up_at = self._get_local_group(name)
        
        self.up_space_type = 'objectrotation'
        self.world_up_vector = [0,1,0]
        
    def run(self):
        
        
        self._freeze()
                
        self._get_relatives()
        self._pin()
        
        try:
            cmds.setAttr('%s.rotateAxisX' % self.joint, 0)
            cmds.setAttr('%s.rotateAxisY' % self.joint, 0)
            cmds.setAttr('%s.rotateAxisZ' % self.joint, 0)
        except:
            vtool.util.show('Could not zero out rotateAxis on %s. This may cause rig errors.' % self.joint)
        
        self.orient_values = self._get_values()
        
        if self.orient_values:
        
            self.aim_vector = self._get_vector_from_axis( self.orient_values['aimAxis'] )
            self.up_vector = self._get_vector_from_axis(self.orient_values['upAxis'])
            self.world_up_vector = self._get_vector_from_axis( self.orient_values['worldUpAxis'])
            
            self.aim_at = self._get_aim_at(self.orient_values['aimAt'])
            self.aim_up_at = self._get_aim_up_at(self.orient_values['aimUpAt'])
        
        if not self.orient_values:
                        
            if type(self.aim_at) == int:
                self.aim_at = self._get_aim_at(self.aim_at)
            
            if type(self.aim_up_at) == int: 
                self.aim_up_at = self._get_aim_up_at(self.aim_up_at)
        
        self._create_aim()
        
        self._cleanup()
        
        self._freeze()

class BoundingBox(vtool.util.BoundingBox):
    """
    Convenience for dealing with bounding boxes.
    
    Args
        thing (str): The name of a transform in maya. Bounding box info is automatically loaded from the transform.
    """
    def __init__(self, thing):
        
        self.thing = thing
        
        xmin, ymin, zmin, xmax, ymax, zmax = cmds.exactWorldBoundingBox(self.thing)
        
        super(BoundingBox, self).__init__([xmin, ymin, zmin], 
                                          [xmax, ymax, zmax])

class AttachJoints(object):
    """
    Attach a chain of joints to a matching chain.
    parentConstraint and scaleConstraint are used to make the attachment.
    """
    def __init__(self, source_joints, target_joints):
        self.source_joints = source_joints
        self.target_joints = target_joints
    
    def _hook_scale_constraint(self, node):
        
        constraint_editor = ConstraintEditor()
        scale_constraint = constraint_editor.get_constraint(node, constraint_editor.constraint_scale)
        
        if not scale_constraint:
            return
        
        scale_constraint_to_world(scale_constraint)
        
    def _unhook_scale_constraint(self, scale_constraint):
        
        scale_constraint_to_local(scale_constraint)
        
    def _attach_joint(self, source_joint, target_joint):
        
        
        self._hook_scale_constraint(target_joint)
        
        parent_constraint = cmds.parentConstraint(source_joint, target_joint, mo = True)[0]
        
        scale_constraint = cmds.scaleConstraint(source_joint, target_joint)[0]
        
        constraint_editor = ConstraintEditor()
        constraint_editor.create_switch(self.target_joints[0], 'switch', parent_constraint)
        constraint_editor.create_switch(self.target_joints[0], 'switch', scale_constraint)
        
        self._unhook_scale_constraint(scale_constraint)
        
    def _attach_joints(self, source_chain, target_chain):
        
        for inc in range( 0, len(source_chain) ):
            self._attach_joint(source_chain[inc], target_chain[inc] )
            
    def set_source_and_target_joints(self, source_joints, target_joints):
        """
        Args
            source_joints (list): A list of joint names that should move the target.
            target_joints (list): A list of joints names that should be moved by the source.
        """
        self.source_joints = source_joints
        self.target_joints = target_joints
    
    def create(self):
        """
        Create the attachments.
        """
        self._attach_joints(self.source_joints, self.target_joints)

class DuplicateHierarchy(object):
    """
    Duplicate the hierachy of a transform.
    
    Args
        transform (str): The name of a transform with child hierarchy.
    """
    def __init__(self, transform):
        
        self.top_transform = transform

        self.duplicates = []
        
        self.replace_old = None
        self.replace_new = None
        
        self.stop = False
        self.stop_at_transform = None
        
        self.only_these_transforms = None
        
            
    def _get_children(self, transform):
        return cmds.listRelatives(transform, children = True, type = 'transform')
        
    def _duplicate(self, transform):
        
        new_name = transform
        
        if self.replace_old and self.replace_new:
            new_name = transform.replace(self.replace_old, self.replace_new)
        
        duplicate = cmds.duplicate(transform, po = True)[0]
        
        duplicate = cmds.rename(duplicate, core.inc_name(new_name))
        
        self.duplicates.append( duplicate )

        return duplicate
    
    def _duplicate_hierarchy(self, transform):
            
        if transform == self.stop_at_transform:
            self.stop = True
        
        if self.stop:
            return
        
        top_duplicate = self._duplicate(transform)
        
        children = self._get_children(transform)
        
        if children:
            duplicate = None
            duplicates = []
            
            for child in children:

                if self.only_these_transforms and not child in self.only_these_transforms:
                    continue
                
                duplicate = self._duplicate_hierarchy(child)
                
                if not duplicate:
                    break
                
                duplicates.append(duplicate)
                
                if cmds.nodeType(top_duplicate) == 'joint' and cmds.nodeType(duplicate) == 'joint':
                    
                    if cmds.isConnected('%s.scale' % transform, '%s.inverseScale' % duplicate):
                        cmds.disconnectAttr('%s.scale' % transform, '%s.inverseScale' % duplicate)
                        cmds.connectAttr('%s.scale' % top_duplicate, '%s.inverseScale' % duplicate)
                    
            if duplicates:
                cmds.parent(duplicates, top_duplicate)
        
        return top_duplicate
    
    def only_these(self, list_of_transforms):
        """
        Only duplicate transforms in list_of_transforms.
        
        Args
            list_of_transforms (list): Names of transforms in the hierarchy.
        """
        self.only_these_transforms = list_of_transforms
        
    def stop_at(self, transform):
        """
        The transform at which to stop the duplication.
        
        Args
            transform (str): The name of the transform.
        """
        relative = cmds.listRelatives(transform, type = 'transform')
        
        if relative:
            self.stop_at_transform = relative[0]
        
    def replace(self, old, new):
        """
        Replace the naming in the duplicate.
        
        Args
            old (str): String in the duplicate name to replace.
            new (str): String in the duplicate to replace with.
        """
        self.replace_old = old
        self.replace_new = new
        
    def create(self):
        """
        Create the duplicate hierarchy.
        """
        cmds.refresh()
        
        self._duplicate_hierarchy(self.top_transform)
        
        return self.duplicates

def get_center(transform):
    """
    Get the center of a selection. Selection can be component or transform.
    
    Args
        transform (str): Name of a node in maya.
    
    Return 
        (vector list):  The center vector, eg [0,0,0]
    """
    
    
    components = core.get_components_in_hierarchy(transform)
    
    if components:
        transform = components
        
    bounding_box = BoundingBox(transform)
    return bounding_box.get_center()

def get_btm_center(transform):
    """
    Get the bottom center of a selection. Selection can be component or transform.
    
    Args
        transform (str): Name of a node in maya.
    
    Return 
        (vector list): The btrm center vector, eg [0,0,0]
    """
    
    components = core.get_components_in_hierarchy(transform)
    
    if components:
        transform = components
        
    
    
    bounding_box = BoundingBox(transform)
    return bounding_box.get_ymin_center()

def get_top_center(transform):
    """
    Get the top center of a selection. Selection can be component or transform.
    
    Args
        transform (str): Name of a node in maya.
    
    Return 
        (vector list): The top center vector, eg [0,0,0]
    """
    
    components = core.get_components_in_hierarchy(transform)
    
    if components:
        transform = components
        
    
    
    bounding_box = BoundingBox(transform)
    return bounding_box.get_ymax_center()




def get_closest_transform(source_transform, targets):
    """
    Given the list of target transforms, find the closest to the source transform.
    
    Args
        source_transform (str): The name of the transform to test distance to.
        targets (list): List of targets to test distance against.
        
    Return
        (str): The name of the target in targets that is closest to source_transform.
    """
    
    least_distant = 1000000.0
    closest_target = None
    
    for target in targets:
        
        distance = get_distance(source_transform, target)
        
        if distance < least_distant:
            least_distant = distance
            closest_target = target
            
    return closest_target 

def get_distance(source, target):
    """
    Get the distance between the source transform and the target transform.
    
    Args
        source (str): The name of a transform.
        target (str): The name of a transform.
    
    Return 
        (float): The distance between source and target transform.
    """
    #CBB
    
    vector1 = cmds.xform(source, 
                         query = True, 
                         worldSpace = True, 
                         rp = True)
    
    vector2 = None
    

    if cmds.nodeType(target) == 'mesh':
        vector2 = cmds.xform(target, 
                             query = True, 
                             worldSpace = True, 
                             t = True)
        
    if not vector2:    
        vector2 = cmds.xform(target, 
                             query = True, 
                             worldSpace = True, 
                             rp = True)
    
    return vtool.util.get_distance(vector1, vector2)

def get_midpoint( source, target):
    """
    Get the midpoint between the source transform and the target transform.
    
    Args
        source (str): The name of a transform.
        target (str): The name of a transform.
    
    Return 
        (vector list): The midpoint as [0,0,0] vector between source and target transform.
    """
    vector1 = cmds.xform(source, 
                         query = True, 
                         worldSpace = True, 
                         rp = True)
    
    
    vector2 = cmds.xform(target, 
                            query = True, 
                            worldSpace = True, 
                            rp = True)
    
    return vtool.util.get_midpoint(vector1, vector2)

def get_distances(sources, target):
    """
    Given a list of source transforms, return a list of distances to the target transform
    
    Args
        sources (list): The names of a transforms.
        target (str): The name of a transform.
    
    Return 
        (list): The distances betweeen each source and the target.
    """
    
    distances = []
    
    for source in sources:
        
        distance = get_distance(source, target)
        distances.append(distance)
    
    return distances
        
def get_polevector(transform1, transform2, transform3, offset = 1):
    #CBB
    """
    Given 3 transforms eg. arm, elbow, wrist.  Return a vector of where the pole vector should be located.
        
    Args
        transform1 (str): name of a transform in maya. eg. joint_arm.
        transform2 (str): name of a transform in maya. eg. joint_elbow.
        transform3 (str): name of a transform in maya. eg. joint_wrist.
        
    Return 
        (vector list): The triangle plane vector eg. [0,0,0].  This is good for placing the pole vector.
    """
    
    distance = get_distance(transform1, transform3)
    
    group = get_group_in_plane(transform1, 
                               transform2, 
                               transform3)
    
    cmds.move(0, offset * distance, 0, group, r =True, os = True)
    finalPos = cmds.xform(group, q = True, ws = True, rp = True)

    cmds.delete(group)
    
    return finalPos

def get_group_in_plane(transform1, transform2, transform3):
    """
    Create a group that sits in the triangle plane defined by the 3 transforms.
    
    Args
        transform1 (str): name of a transform in maya. eg. joint_arm.
        transform2 (str): name of a transform in maya. eg. joint_elbow.
        transform3 (str): name of a transform in maya. eg. joint_wrist.
        
    Return 
        (vector list): The triangle plane vector eg. [0,0,0].  This is good for placing the pole vector.
    """
    #CBB
    
    pole_group = cmds.group(em=True)
    match = MatchSpace(transform1, pole_group)
    match.translation_rotation()
    
    cmds.aimConstraint(transform3, pole_group, 
                       offset = [0,0,0], 
                       weight = 1, 
                       aimVector = [1,0,0], 
                       upVector = [0,1,0], 
                       worldUpType = "object", 
                       worldUpObject = transform2)
    
    pole_group2 = cmds.group(em = True, n = 'pole_%s' % transform1)
    match = MatchSpace(transform2, pole_group2)
    match.translation_rotation()
    
    cmds.parent(pole_group2, pole_group)
    cmds.makeIdentity(pole_group2, apply = True, t = True, r = True )
    cmds.parent(pole_group2, w = True)
    cmds.delete(pole_group)
    
    return pole_group2




def get_ordered_distance_and_transform(source_transform, transform_list):
    """
    Returns a list of distances based on how far each transform in transform list is from source_transform.
    Returns a distance dictionary with each distacne key returning the corresponding transform.
    Returns a list with the original distance order has fed in from transform_list.
    
    Args
        source_transform (str)
        
        transform_list (list)
        
    Return
        (dict)
        
    """
    
    
    distance_list = []
    distance_dict = {}
    
    for transform in transform_list:
        distance = get_distance(source_transform, transform)
        
        distance_list.append(distance)
        
        if distance in distance_dict:
            distance_dict[distance].append(transform)
        if not distance in distance_dict:
            distance_dict[distance] = [transform]
        
    
    original_distance_order = list(distance_list)
    
    distance_list.sort()
    
    return distance_list, distance_dict, original_distance_order

def get_transform_list_from_distance(source_transform, transform_list):
    """
    Return a list of distances that corresponds to the transform_list. Each transform's distance from source_transform. 
    """
    
    distance_list, distance_dict, original = get_ordered_distance_and_transform(source_transform, transform_list)
    
    found = []
    
    for distance in distance_list:
        found.append(distance_dict[distance][0])
        
    return found


def create_follow_fade(source_guide, drivers, skip_lower = 0.0001):
    """
    Create a multiply divide for each transform in drivers with a weight value based on the distance from source_guide.
    
    Args
        source_guide (str): Name of a transform in maya to calculate distance.
        drivers (list): List of drivers to apply fade to based on distance from source_guide.
        skip_lower (float): The distance below which multiplyDivide fading stops.
        
    Return
        (list) : The list of multiplyDivide nodes.
    
    """
    distance_list, distance_dict, original_distance_order = get_ordered_distance_and_transform(source_guide, drivers)
    
    multiplies = []
    
    if not distance_list[-1] > 0:
        return multiplies
    
    for distance in original_distance_order:
                
        scaler = 1.0 - (distance/ distance_list[-1]) 
        
        if scaler <= skip_lower:
            continue
        
        multi = attr.MultiplyDivideNode(source_guide)
        
        multi.set_input2(scaler,scaler,scaler)
        
        multi.input1X_in( '%s.translateX' % source_guide )
        multi.input1Y_in( '%s.translateY' % source_guide )
        multi.input1Z_in( '%s.translateZ' % source_guide )
        
        for driver in distance_dict[distance]:
            multi.outputX_out('%s.translateX' % driver)
            multi.outputY_out('%s.translateY' % driver)
            multi.outputZ_out('%s.translateZ' % driver)
            
        multi_dict = {}
        multi_dict['node'] = multi
        multi_dict['source'] = source_guide
        #CBB strange that it passed the last driver...
        multi_dict['target'] = driver
        
        multiplies.append(multi_dict)
        
    return multiplies

def create_match_group(transform, prefix = 'match', use_duplicate = False):
    """
    Create a group that matches a transform.
    Naming = 'match_' + transform
    
    Args
        transform (str): The transform to match.
        prefix (str): The prefix to add to the matching group.
        use_duplicate (bool):  If True, matching happens by duplication instead of changing transform values.
        
    Return
        (str):  The name of the new group.
    """
    parent = cmds.listRelatives(transform, p = True, f = True)
    
    basename = core.get_basename(transform)
    
    name = '%s_%s' % (prefix, basename)
    
    if not use_duplicate:    
        xform_group = cmds.group(em = True, n = core.inc_name( name ))
        match_space = MatchSpace(transform, xform_group)
        match_space.translation_rotation()
        
        if parent:
            cmds.parent(xform_group, parent[0])    
        
    if use_duplicate:
        xform_group = cmds.duplicate(transform, po = True)
        xform_group = cmds.rename(xform_group, core.inc_name(name))
    
    return xform_group    

def create_xform_group(transform, prefix = 'xform', use_duplicate = False):
    """
    Create a group above a transform that matches transformation of the transform. 
    This is good for zeroing out the values of a transform.
    Naming = 'xform_' + transform
    
    Args
        transform (str): The transform to match.
        prefix (str): The prefix to add to the matching group.
        use_duplicate (bool):  If True, matching happens by duplication instead of changing transform values.
        
    Return
        (str):  The name of the new group.
    """
    
    parent = cmds.listRelatives(transform, p = True, f = True)
    
    basename = core.get_basename(transform)
    
    name = '%s_%s' % (prefix, basename)
    
    if not use_duplicate:    
        xform_group = cmds.group(em = True, n = core.inc_name( name ))
        match_space = MatchSpace(transform, xform_group)
        match_space.translation_rotation()
        
        if parent:
            cmds.parent(xform_group, parent[0])    
        
    if use_duplicate:
        xform_group = cmds.duplicate(transform, po = True)
        xform_group = cmds.rename(xform_group, core.inc_name(name))
    
    cmds.parent(transform, xform_group)

    return xform_group

def create_follow_group(source_transform, target_transform, prefix = 'follow', follow_scale = False):
    """
    Create a group above a target_transform that is constrained to the source_transform.
    
    Args
        source_transform (str): The transform to follow.
        target_transform (str): The transform to make follow.
        prefix (str): The prefix to add to the follow group.
        follow_scale (bool): Wether to add a scale constraint or not.
    
    Return
        (str):  The name of the new group.
    """
    
    parent = cmds.listRelatives(target_transform, p = True)
    
    name = '%s_%s' % (prefix, target_transform)
    
    follow_group = cmds.group( em = True, n = core.inc_name(name) )
    
    match = MatchSpace(source_transform, follow_group)
    match.translation_rotation()
    
    cmds.parentConstraint(source_transform, follow_group, mo = True)
    
    cmds.parent(target_transform, follow_group)    
    
    if parent:
        cmds.parent(follow_group, parent)
        
    if follow_scale:
        attr.connect_scale(source_transform, follow_group)
        
    return follow_group

def create_local_follow_group(source_transform, target_transform, prefix = 'followLocal', orient_only = False):
    """
    Create a group above a target_transform that is local constrained to the source_transform.
    This helps when setting up controls that need to be parented but only affect what they constrain when the actual control is moved.  
    
    Args
        source_transform (str): The transform to follow.
        target_transform (str): The transform to make follow.
        prefix (str): The prefix to add to the follow group.
        orient_only (bool): Wether the local constraint should just be an orient constraint.
    
    Return
        (str):  The name of the new group.
    """
    
    parent = cmds.listRelatives(target_transform, p = True)
    
    name = '%s_%s' % (prefix, target_transform)
    
    follow_group = cmds.group( em = True, n = core.inc_name(name) )
    
    #MatchSpace(target_transform, follow_group).translation()
    MatchSpace(source_transform, follow_group).translation_rotation()
    
    xform = create_xform_group(follow_group)
    
    #cmds.parentConstraint(source_transform, follow_group, mo = True)
    
    if not orient_only:
        attr.connect_translate(source_transform, follow_group)
    
    if orient_only:
        attr.connect_rotate(source_transform, follow_group)
    
    #value = cmds.getAttr('%s.rotateOrder' % source_transform)
    #cmds.setAttr('%s.rotateOrder' % follow_group, value)
    
    cmds.parent(target_transform, follow_group)
    
    if parent:
        cmds.parent(xform, parent)
        
    return follow_group    

def create_multi_follow_direct(source_list, target_transform, node, constraint_type = 'parentConstraint', attribute_name = 'follow', value = None):
    """
    Create a group above the target that is constrained to multiple transforms. A switch attribute switches their state on/off.
    Direct in this case means the constraints will be added directly on the target_transform.
    
    Args
        source_list (list): List of transforms that the target should be constrained by.
        target_transform (str): The name of a transform that should follow the transforms in source list.
        node (str): The name of the node to add the switch attribute to.
        constraint_type (str): Corresponds to maya's constraint types. Currently supported: parentConstraint, pointConstraint, orientConstraint.
        attribute_name (str): The name of the switch attribute to add to the node.
        value (float): The value to give the switch attribute on the node.
    
    Return
        (str):  The name of the new group.
    """
    
    if attribute_name == 'follow':
        var = attr.MayaEnumVariable('FOLLOW')
        var.create(node)
            
    locators = []

    for source in source_list:
        
        locator = cmds.spaceLocator(n = core.inc_name('follower_%s' % source))[0]
        
        cmds.hide(locator)
        
        match = MatchSpace(target_transform, locator)
        match.translation_rotation()
        
        cmds.parent(locator, source)
        
        locators.append(locator)
    
    if constraint_type == 'parentConstraint':
        constraint = cmds.parentConstraint(locators,  target_transform, mo = True)[0]
        
    if constraint_type == 'pointConstraint':
        constraint = cmds.pointConstraint(locators,  target_transform, mo = True)[0]
        
    if constraint_type == 'orientConstraint':
        constraint = cmds.orientConstraint(locators,  target_transform, mo = True)[0]
    
    constraint_editor = ConstraintEditor()
    
    constraint_editor.create_switch(node, attribute_name, constraint)

    if value == None:
        value = (len(source_list)-1)
    
    cmds.setAttr('%s.%s' % (node, attribute_name), value)
       

def create_multi_follow(source_list, target_transform, node = None, constraint_type = 'parentConstraint', attribute_name = 'follow', value = None):
    """
    Create a group above the target that is constrained to multiple transforms. A switch attribute switches their state on/off.
    Direct in this case means the constraints will be added directly on the target_transform.
    
    Args
        source_list (list): List of transforms that the target should be constrained by.
        target_transform (str): The name of a transform that should follow the transforms in source list.
        node (str): The name of the node to add the switch attribute to.
        constraint_type (str): Corresponds to maya's constraint types. Currently supported: parentConstraint, pointConstraint, orientConstraint.
        attribute_name (str): The name of the switch attribute to add to the node.
        value (float): The value to give the switch attribute on the node.
    
    Return
        (str):  The name of the new group.
    """
    if node == None:
        node = target_transform
    
    locators = []
    
    if len(source_list) < 2:
        vtool.util.warning('Can not create multi follow with less than 2 source transforms.')
        return
    
    follow_group = create_xform_group(target_transform, 'follow')
    
    if attribute_name == 'follow':
        var = attr.MayaEnumVariable('FOLLOW')
        var.create(node)    

    for source in source_list:
        
        locator = cmds.spaceLocator(n = core.inc_name('follower_%s' % source))[0]
        
        cmds.hide(locator)
        
        match = MatchSpace(target_transform, locator)
        match.translation_rotation()
        
        cmds.parent(locator, source)
        
        locators.append(locator)
    
    if constraint_type == 'parentConstraint':
        constraint = cmds.parentConstraint(locators,  follow_group, mo = True)[0]
    if constraint_type == 'orientConstraint':
        constraint = cmds.orientConstraint(locators,  follow_group)[0]
    if constraint_type == 'pointConstraint':
        constraint = cmds.pointConstraint(locators,  follow_group, mo = True)[0]
    
    constraint_editor = ConstraintEditor()
    
    constraint_editor.create_switch(node, attribute_name, constraint)
    
    if value == None:
        value = (len(source_list)-1)
        
    cmds.setAttr('%s.%s' % (node, attribute_name), value)
    
    return follow_group


def get_hierarchy(node_name):
    """
    Return the name of the node including the hierarchy in the name using "|".
    This is the full path of the node.
    
    Args
        node_name (str): A node name.
        
    Return
        (str): The node name with hierarchy included. The full path to the node.
    """
    
    parent_path = cmds.listRelatives(node_name, f = True)[0]
    
    if parent_path:
        split_path = cmds.split(parent_path, '|')
    
    if split_path:
        return split_path
        
def has_parent(transform, parent):
    """
    Check to see if the transform has parent in its parent hierarchy.
    
    Args
        transform (str): The name of a transform.
        parent (str): The name of a parent transform.
        
    Return
        (bool)
    """
    
    long_transform = cmds.ls(transform, l = True)
    
    if not long_transform:
        return
    
    long_transform = long_transform[0]
    
    split_long = long_transform.split('|')
    
    core.get_basename(parent)
    
    if parent in split_long:
        return True
    
    return False
        
        
def transfer_relatives(source_node, target_node, reparent = False):
    """
    Reparent the children of source_node under target_node.
    If reparent, move the target_node under the parent of the source_node.
    
    Args
        source_node (str): The name of a transform to take relatives from.
        target_node (str): The name of a transform to transfer relatives to.
        reparent (bool): Wether to reparent target_node under source_node after transfering relatives.
    """
    
    parent = None
    
    if reparent:
        parent = cmds.listRelatives(source_node, p = True)
        if parent:
            parent = parent[0]
        
    children = cmds.listRelatives(source_node, c = True, type = 'transform')

    if children:
        cmds.parent(children, target_node)
    
    
    if parent:
        cmds.parent(target_node, parent)


    

def constrain_local(source_transform, target_transform, parent = False, scale_connect = False, constraint = 'parentConstraint'):
    """
    Constrain a target transform to a source transform in a way that allows for setups to remain local to the origin.
    This is good when a control needs to move with the rig, but move something at the origin only when the actually control moves.
    
    Args
        source_transform (str): The name of a transform.
        target_transform (str): The name of a transform.
        parent (bool): The setup uses a local group to constrain the target_transform. If this is true it will parent the target_transform under the local group.
        scale_connect (bool): Wether to also add a scale constraint.
        constraint (str): The type of constraint to use. Currently supported: parentConstraint, pointConstraint, orientConstraint.
        
    Return
        (str, str) : The local group that constrains the target_transform, and the xform group above the local group.
    """
    local_group = cmds.group(em = True, n = core.inc_name('local_%s' % source_transform))
    
    xform_group = create_xform_group(local_group)
    
    parent_world = cmds.listRelatives(source_transform, p = True)
    
    if parent_world:
        parent_world = parent_world[0]
        
        match = MatchSpace(parent_world, xform_group)
        match.translation_rotation()
            
    match = MatchSpace(source_transform, local_group)
    
    match.translation_rotation()
    
    attr.connect_translate(source_transform, local_group)
    attr.connect_rotate(source_transform, local_group)
    
    if scale_connect:
        attr.connect_scale(source_transform, local_group)
            
    if parent:
        cmds.parent(target_transform, local_group)
        
    if not parent:
        if constraint == 'parentConstraint':
            cmds.parentConstraint(local_group, target_transform, mo = True)
        if constraint == 'pointConstraint':
            cmds.pointConstraint(local_group, target_transform, mo = True)
        if constraint == 'orientConstraint':
            cmds.orientConstraint(local_group, target_transform, mo = True)
            
        if scale_connect:
            attr.connect_scale(source_transform, target_transform)
    
    return local_group, xform_group

def subdivide_joint(joint1 = None, joint2 = None, count = 1, prefix = 'joint', name = 'sub_1', duplicate = False):
    """
    Add evenly spaced joints inbetween joint1 and joint2.
    
    Args
        joint1 (str): The first joint. If None given, the first selected joint.
        joint2 (str): The second joint. If None given, the second selected joint.
        count (int): The number of joints to add inbetween joint1 and joint2.
        prefix (str): The prefix to add in front of the new joints.
        name (str): The name to give the new joints after the prefix. Name = prefix + '_' + name
        duplicate (bool): Wether to create a duplicate chain.
        
    Return
        (list): List of the newly created joints.
        
    """
    if not joint1 and not joint2:
        selection = cmds.ls(sl = True)
        
        if cmds.nodeType(selection[0]) == 'joint':
            joint1 = selection[0]
        
        if cmds.nodeType(selection[1]) == 'joint':
            joint2 = selection[1]
            
    if not joint1 or not joint2:
        return
    
    vector1 = cmds.xform(joint1, query = True, worldSpace = True, translation = True)
    vector2 = cmds.xform(joint2, query = True, worldSpace = True, translation = True)
    
    name = '%s_%s' % (prefix, name)
    
    joints = []
    top_joint = joint1
    
    radius = cmds.getAttr('%s.radius' % joint1)
    
    if duplicate:
        cmds.select(cl = True)
        top_joint = cmds.joint(p = vector1, n = core.inc_name(name), r = radius + 1)
        joints.append(top_joint)
        
        match = MatchSpace(joint1, top_joint)
        match.rotation()
        cmds.makeIdentity(top_joint, apply = True, r = True)
    
    offset = 1.00/(count+1)
    value = offset
    
    last_joint = None
        
    for inc in range(0, count):
        
        position = vtool.util.get_inbetween_vector(vector1, vector2, value)
        
        cmds.select(cl = True)
        joint = cmds.joint( p = position, n = core.inc_name(name), r = radius)
        cmds.setAttr('%s.radius' % joint, radius)
        joints.append(joint)

        value += offset
        
            
        if inc == 0:
            cmds.parent(joint, top_joint)
            cmds.makeIdentity(joint, apply = True, jointOrient = True)
            
        if last_joint:
            cmds.parent(joint, last_joint)
            cmds.makeIdentity(joint, apply = True, jointOrient = True)
            
            if not cmds.isConnected('%s.scale' % last_joint, '%s.inverseScale'  % joint):
                cmds.connectAttr('%s.scale' % last_joint, '%s.inverseScale'  % joint)
            
                
        last_joint = joint            
        
            
    btm_joint = joint2
    
    if duplicate:
        cmds.select(cl = True)
        btm_joint = cmds.joint(p = vector2, n = core.inc_name(name), r = radius + 1)
        joints.append(btm_joint)

        match = MatchSpace(joint1, btm_joint)
        match.rotation()
        cmds.makeIdentity(btm_joint, apply = True, r = True)
    
    cmds.parent(btm_joint, joint)
    
    if not cmds.isConnected('%s.scale' % joint, '%s.inverseScale'  % btm_joint):
            cmds.connectAttr('%s.scale' % joint, '%s.inverseScale'  % btm_joint)
            
    return joints


    
@core.undo_chunk
def add_orient_attributes(transform):
    """
    Add orient attributes, used to automatically orient.
    
    Args
        transform (str): The name of the transform.
    """
    if type(transform) != list:
        transform = [transform]
    
    for thing in transform:
        
        orient = attr.OrientJointAttributes(thing)
        orient.set_default_values()
    
def orient_attributes(scope = None):
    """
    Orient all transforms with attributes added by add_orient_attributes.
    If scope is provided, only orient transforms in the scope that have attributes.
    
    Args
        scope (list): List of transforms to orient.
    """
    if not scope:
        scope = get_top_dag_nodes()
    
    for transform in scope:
        relatives = cmds.listRelatives(transform, f = True)
        
        if not cmds.objExists('%s.ORIENT_INFO' % transform):
            if relatives:
                orient_attributes(relatives)
                
            continue
        
        if cmds.nodeType(transform) == 'joint' or cmds.nodeType(transform) == 'transform':
            orient = OrientJoint(transform)
            orient.run()
            
            if relatives:
                orient_attributes(relatives)

def find_transform_right_side(transform):
    """
    Try to find the right side of a transform.
    *_L will be converted to *_R 
    if not 
    l_* will be converted to R_*
    if not 
    *lf_* will be converted to *rt_*
    
    Args
        transform (str): The name of a transform.
        
    Return 
        (str): The name of the right side transform if it exists.
    """
    
    other = ''
    
    if transform.endswith('_L'):
        other = transform.replace('_L', '_R')
        
        if cmds.objExists(other):
            return other
    
    other = ''
        
    if transform.startswith('L_') and not transform.endswith('_R'):
        
        other = transform.replace('L_', 'R_')
        
        if cmds.objExists(other):
            return other 
        
    other = ''
        
    if transform.find('lf_') > -1 and not transform.endswith('_R') and not transform.startswith('L_'):
        other = transform.replace('lf_', 'rt_')
        
        if cmds.objExists(other):
            return other
        
    return ''

def mirror_xform(prefix = None, suffix = None, string_search = None):
    """
    Mirror the positions of all transforms that match the search strings.
    If search strings left at None, search all transforms and joints. 
    
    Args
        prefix (str): The prefix to search for.
        suffix (str): The suffix to search for.
        string_search (str): Search for a name containing string search.
    """
    
    scope_joints = []
    scope_transforms = []
    
    joints = []
    transforms = []
    
    if not prefix and not suffix and not string_search:
        joints = cmds.ls(type ='joint')
        transforms = cmds.ls(type = 'transform')
    
    if prefix:
        joints = cmds.ls('%s*' % prefix, type = 'joint')
        transforms = cmds.ls('%s*' % prefix, type = 'transform')
        
    scope_joints += joints
    scope_transforms += transforms
        
    if suffix:    
        joints = cmds.ls('*%s' % suffix, type = 'joint')
        transforms = cmds.ls('*%s' % suffix, type = 'transform')
    
    scope_joints += joints
    scope_transforms += transforms
        
    if string_search:
        joints = cmds.ls('*%s*' % string_search, type = 'joint')
        transforms = cmds.ls('*%s*' % string_search, type = 'transform')
        
    scope_joints += joints
    scope_transforms += transforms
        
    scope = scope_joints + scope_transforms
    
    if not scope:
        return
    
    for transform in scope:
        
        other = ''
        other = find_transform_right_side(transform)
        
        if attr.is_translate_rotate_connected(other):
            continue
       
        if cmds.objExists(other):
            
            xform = cmds.xform(transform, q = True, ws = True, t = True)
            
            if cmds.nodeType(other) == 'joint':
                
                radius = cmds.getAttr('%s.radius' % transform)
                
                if not core.is_referenced(other):
                    var = attr.MayaNumberVariable('radius')
                    var.set_node(other)
                    var.set_value(radius)
                
                if not cmds.getAttr('%s.radius' % other, l = True):
                    cmds.setAttr('%s.radius' % other, radius)
                    
                cmds.move((xform[0]*-1), xform[1], xform[2], '%s.scalePivot' % other, 
                                                             '%s.rotatePivot' % other, a = True)
            
            if cmds.nodeType(other) == 'transform':
                        
                pos = [ (xform[0]*-1), xform[1],xform[2] ]
                                
                cmds.xform(other, ws = True, t = pos)
                pivot = cmds.xform(transform, q = True, ws = True, rp = True)
                cmds.move((pivot[0]*-1), pivot[1], pivot[2], '%s.scalePivot' % other, 
                                                             '%s.rotatePivot' % other, a = True)
                
                if cmds.objExists('%s.localPosition' % transform):
                    local_position = cmds.getAttr('%s.localPosition' % transform)[0]
                    
                    cmds.setAttr('%s.localPositionX' % transform, (local_position[0] * -1))
                    cmds.setAttr('%s.localPositionY' % transform, local_position[1])
                    cmds.setAttr('%s.localPositionZ' % transform, local_position[2])
    
def match_joint_xform(prefix, other_prefix):
    """
    Match the positions of joints with similar names.
    For example, skin_arm_L could be matched to joint_arm_L, if they exists and prefix = skin and other_prefix = joint.
    Args 
        prefix (str)
        other_prefix (str) 
    """
    scope = cmds.ls('%s*' % other_prefix, type = 'joint')

    for joint in scope:
        other_joint = joint.replace(other_prefix, prefix)

        if cmds.objExists(other_joint):    
            match = MatchSpace(joint, other_joint)
            match.rotate_scale_pivot_to_translation()

def match_orient(prefix, other_prefix):
    """
    Match the orientations of joints with similar names.
    For example, skin_arm_L could be matched to joint_arm_L, if they exists and prefix = skin and other_prefix = joint.
    Args 
        prefix (str)
        other_prefix (str) 
    """
    scope = cmds.ls('%s*' % prefix, type = 'joint')
    
    for joint in scope:
        other_joint = joint.replace(prefix, other_prefix)

        if cmds.objExists(other_joint): 

            pin = PinXform(joint)
            pin.pin()
            cmds.delete( cmds.orientConstraint(other_joint, joint) )
            pin.unpin()
            cmds.makeIdentity(joint, apply = True, r = True)
            
    for joint in scope:
        other_joint = joint.replace(prefix, other_prefix)
        
        if not cmds.objExists(other_joint):
            cmds.makeIdentity(joint, apply = True, jo = True)




    
def get_side(transform, center_tolerance):
    """
    Get the side of a transform based on its position in world space.
    Center tolerance is distance from the center to include as a center transform.
    
    Args
        transform (str): The name of a transform.
        center_tolerance (float): How close to the center the transform must be before it is considered in the center.
        
    Return
        (str): The side that the transform is on, could be 'L','R' or 'C'.
    """
    if type(transform) == list or type(transform) == tuple:
        position = transform
    
    if not type(transform) == list and not type(transform) == tuple:
        position = cmds.xform(transform, q = True, ws = True, rp = True)
        
    if position[0] > 0:
        side = 'L'

    if position[0] < 0:
        side = 'R'
        
    if position[0] < center_tolerance and position[0] > center_tolerance*-1:
        side = 'C'
            
    return side

def create_no_twist_aim(source_transform, target_transform, parent):
    """
    Aim target transform at the source transform, trying to rotate only on one axis.
    Constrains the target_transform.
    
    Args
        source_transform (str): The name of a transform.
        target_transform (str): The name of a transform.
        parent (str): The parent for the setup.
    """
    top_group = cmds.group(em = True, n = core.inc_name('no_twist_%s' % source_transform))
    cmds.parent(top_group, parent)
    cmds.pointConstraint(source_transform, top_group)

    #axis aim
    aim = cmds.group(em = True, n = core.inc_name('aim_%s' % target_transform))
    target = cmds.group(em = True, n = core.inc_name('target_%s' % target_transform))
        
    MatchSpace(source_transform, aim).translation_rotation()
    MatchSpace(source_transform, target).translation_rotation()
    
    xform_target = create_xform_group(target)
    #cmds.setAttr('%s.translateX' % target, 1)
    cmds.move(1,0,0, target, r = True, os = True)
    
    cmds.parentConstraint(source_transform, target, mo = True)
    
    cmds.aimConstraint(target, aim, wuo = parent, wut = 'objectrotation', wu = [0,0,0])
    
    cmds.parent(aim, xform_target, top_group)
    
    #pin up to axis
    pin_aim = cmds.group(em = True, n = core.inc_name('aim_pin_%s' % target_transform))
    pin_target = cmds.group(em = True, n = core.inc_name('target_pin_%s' % target_transform))
    
    MatchSpace(source_transform, pin_aim).translation_rotation()
    MatchSpace(source_transform, pin_target).translation_rotation()
    
    xform_pin_target = create_xform_group(pin_target)
    cmds.move(0,0,1, pin_target, r = True)
    
    cmds.aimConstraint(pin_target, pin_aim, wuo = aim, wut = 'objectrotation')
    
    cmds.parent(xform_pin_target, pin_aim, top_group)
       
    #twist_aim
    #tool_maya.create_follow_group('CNT_SPINE_2_C', 'xform_CNT_TWEAK_ARM_1_%s' % side)
    cmds.pointConstraint(source_transform, target_transform, mo = True)
    
    cmds.parent(pin_aim, aim)
    
    cmds.orientConstraint(pin_aim, target_transform, mo = True)

def create_pole_chain(top_transform, btm_transform, name):
    """
    Create a two joint chain with an ik handle.
    
    Args
        top_transform (str): The name of a transform.
        btm_transform (str): The name of a transform.
        name (str): The name to give the new joints.
        
        Return
            (joint1, joint2, ik_pole)
    """
    
    cmds.select(cl =True)
    
    joint1 = cmds.joint(n = core.inc_name( name ) )
    joint2 = cmds.joint(n = core.inc_name( name ) )

    MatchSpace(top_transform, joint1).translation()
    MatchSpace(btm_transform, joint2).translation()
    
    cmds.joint(joint1, e = True, oj = 'xyz', secondaryAxisOrient = 'xup', zso = True)
    cmds.makeIdentity(joint2, jo = True, apply = True)

    ik_handle = IkHandle( name )
    
    ik_handle.set_start_joint( joint1 )
    ik_handle.set_end_joint( joint2 )
    ik_handle.set_solver(ik_handle.solver_sc)
    ik_pole = ik_handle.create()

    return joint1, joint2, ik_pole

def scale_constraint_to_local(scale_constraint):
    """
    Scale constraint can work wrong when given the parent matrix.
    Disconnect the parent matrix to remove this behavior.
    Reconnect using scale_constraint_to_world if applying multiple constraints.
    
    Args
        scale_constraint (str): The name of the scale constraint to work on.
    """
    
    constraint_editor = ConstraintEditor()
        
    weight_count = constraint_editor.get_weight_count(scale_constraint)
    attr.disconnect_attribute('%s.constraintParentInverseMatrix' % scale_constraint)
    
    
    for inc in range(0, weight_count):
        attr.disconnect_attribute('%s.target[%s].targetParentMatrix' % (scale_constraint, inc))

def scale_constraint_to_world(scale_constraint):
    """
    Works with scale_constraint_to_local.
    
    Args
        scale_constraint (str): The name of the scale constraint affected by scale_constraint_to_local.
    """
    
    constraint_editor = ConstraintEditor()
    
    weight_count = constraint_editor.get_weight_count(scale_constraint)
    
    node = attr.get_attribute_outputs('%s.constraintScaleX' % scale_constraint, node_only = True)
    
    
    if node:
        cmds.connectAttr('%s.parentInverseMatrix' % node[0], '%s.constraintParentInverseMatrix' % scale_constraint)
    
    for inc in range(0, weight_count):
        
        target = attr.get_attribute_input('%s.target[%s].targetScale' % (scale_constraint, inc), True)
        
        cmds.connectAttr('%s.parentInverseMatrix' % target, '%s.target[%s].targetParentMatrix' % (scale_constraint, inc) )
    
def duplicate_joint_section(joint, name = ''):
    """
    Joint chains ususally have a parent and a child along the chain. 
    This will duplicate one of those sections.  You need only supply the parent joint.
    
    Args
        joint (str): The name of the joint to duplicate.
        name (str): The name to give the joint section.
        
    Return
        list: [duplicate, sub duplicate]. If no sub duplicate, then [duplicate, None]
    """
    
    
    rels = cmds.listRelatives(joint, type = 'joint', f = True)
    
    if not rels:
        return
    
    child = rels[0]
    
    if not name:
        name = 'duplicate_%s' % joint
    
    duplicate = cmds.duplicate(joint, po = True, n = name)[0]
    sub_duplicate = None
    
    if child:
        sub_duplicate = cmds.duplicate(child, po = True, n = (name + '_end'))[0] 
        cmds.parent(sub_duplicate, duplicate)
        cmds.makeIdentity(sub_duplicate, jo = True, r = True, apply = True)
        
    if not sub_duplicate:
        return duplicate, None
    if sub_duplicate:
        return duplicate, sub_duplicate   
    
def get_axis_vector(transform, axis_vector):
    """
    Get the vector matrix product.
    If you give it a vector [1,0,0], it will return the transform's x point.
    If you give it a vector [0,1,0], it will return the transform's y point.
    If you give it a vector [0,0,1], it will return the transform's z point.
    
    Args
        transform (str): The name of a transform. Its matrix will be checked.
        axis_vector (list): A vector. X = [1,0,0], Y = [0,1,0], Z = [0,0,1] 
        
    Return
        list: The result of multiplying the vector by the matrix. Good to get an axis in relation to the matrix.
    """
    t_func = api.TransformFunction(transform)
    new_vector = t_func.get_vector_matrix_product(axis_vector)
    
    return new_vector

def transforms_to_joint_chain(transforms, name = ''):
    """
    Given a list of transforms, create a joint chain.
    
    Args
        transforms (list): List of transforms. Their positions will be used to set joint positions.
        name (str): The description to give the joints.
        
    Return
        list: The names of the joints created.
    """
    cmds.select(cl = True)
    
    joints = []
    
    for transform in transforms:
    
        if not name:
            name = transform     
            
        joint = cmds.joint(n = core.inc_name('joint_%s' % name))
        
        MatchSpace(transform, joint).translation_rotation()
        
        joints.append(joint)
        
    return joints

def attach_to_closest_transform(source_transform, target_transforms):
    """
    Attach the source_transform to the closest transform in the list of target_transforms.
    
    Args
        source_transform (str): The name of a transform to check distance to.
        target_transforms (list): List of transforms. The closest to source_transform will be attached to it.
    """
    closest_transform = get_closest_transform(source_transform, target_transforms)
    
    create_follow_group(closest_transform, source_transform)


def create_ghost_chain(transforms):
    """
    A ghost chain has the same hierarchy has the supplied transforms.
    It connects into the an xform group above the transform.  
    This allows for setups that follow a nurbs surface, and then work like an fk hierarchy after.
    
    Args
        transforms (list): A list of transforms.
        
    Return
        list: A list of ghost transforms corresponding to transforms.
    """
    last_ghost = None
    
    ghosts = []
    
    for transform in transforms:
        ghost = cmds.duplicate(transform, po = True, n = 'ghost_%s' % transform)[0]
        cmds.parent(ghost, w = True)
        
        MatchSpace(transform, ghost).translation_rotation()
        
        xform = create_xform_group(ghost)
        
        target_offset = create_xform_group(transform)
        
        attr.connect_translate(ghost, target_offset)
        attr.connect_rotate(ghost, target_offset)
        
        if last_ghost:
            cmds.parent(xform, last_ghost )
        
        last_ghost = ghost
        
        ghosts.append(ghost)

    return ghosts




        