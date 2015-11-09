# Copyright (C) 2014 Louis Vottero louis.vot@gmail.com    All rights reserved.

import traceback

import vtool.util

if vtool.util.is_in_maya():
    import maya.cmds as cmds
    import maya.mel as mel
    
undo_chunk_active = False
current_progress_bar = None
    
MAYA_BINARY = 'mayaBinary'
MAYA_ASCII = 'mayaAscii'

maya_data_mappings = {  
                        'bool' : 'attributeType',
                        'long' : 'attributeType',
                        'long2' : 'attributeType',
                        'long3' : 'attributeType',
                        'short': 'attributeType',
                        'short2' : 'attributeType',
                        'short3' : 'attributeType',
                        'byte' : 'attributeType',
                        'char' : 'attributeType',
                        'enum' : 'attributeType',
                        'float' : 'attributeType',
                        'float2' : 'attributeType',
                        'float3' : 'attributeType',
                        'double' : 'attributeType',
                        'double2' : 'attributeType',
                        'double3' : 'attributeType',
                        'doubleAngle' : 'attributeType',
                        'doubleLinear' : 'attributeType',
                        'doubleArray' : 'dataType',
                        'string' : 'dataType',
                        'stringArray' : 'dataType',
                        'compound' : 'attributeType',
                        'message' : 'attributeType',
                        'time' : 'attributeType',
                        'matrix' : 'dataType',
                        'fltMatrix' : 'attributeType',
                        'reflectanceRGB' : 'dataType',
                        'reflectance' : 'attributeType',
                        'spectrumRGB' : 'dataType',
                        'spectrum' : 'attributeType',
                        'Int32Array' : 'dataType',
                        'vectorArray' : 'dataType',
                        'nurbsCurve' : 'dataType',
                        'nurbsSurface' : 'dataType',
                        'mesh' : 'dataType',
                        'lattice' : 'dataType',
                        'pointArray' : 'dataType'
                        }

class FindUniqueName(vtool.util.FindUniqueString):
    """
    This class is intended to find a name that doesn't clash with other names in the Maya scene.
    It will increment the last number in the name. 
    If no number is found it will append a 1 to the end of the name.
    """
    
    def _get_scope_list(self):

        if cmds.objExists(self.increment_string):
            return [self.increment_string]
        
        if not cmds.objExists(self.increment_string):
            return []
    
    def _format_string(self, number):
        
        if number == 0:
            number = 1
            self.increment_string = '%s_%s' % (self.test_string, number)
        
        if number > 1:
            self.increment_string = vtool.util.increment_last_number(self.increment_string)
    
    def _get_number(self):
        number = vtool.util.get_last_number(self.test_string)
        
        return number

class TrackNodes(object):
    """
    This helps track new nodes that get added to a scene after a function runs.
    
    Usage:
    track_nodes = TrackNodes()
    track_nodes.load()
    my_function()
    new_nodes = track_nodes.get_delta()
    """
    def __init__(self):
        self.nodes = None
        self.node_type = None
        self.delta = None
        
    def load(self, node_type = None):
        """
            node_type corresponds to the maya node type. 
            For example, you can give node_type the string "animCurve" to load only keyframes.
            When after running get_delta(), the delta will only contain keyframes.
            
        Args
            node_type (str): Maya named type, ie animCurve, transform, joint, etc
            
        Return
            None
        """
        self.node_type = node_type
        
        if self.node_type:
            self.nodes = cmds.ls(type = node_type)
        if not self.node_type:
            self.nodes = cmds.ls()
        
    def get_delta(self):
        """
        Get the new nodes in the Maya scene created after load() was executed.
        The load() node_type variable is stored in the class and used when getting the delta.
            
        Return
            (list) : list of new nodes.
        """
        if self.node_type:
            current_nodes = cmds.ls(type = self.node_type)
        if not self.node_type:
            current_nodes = cmds.ls()
            
        new_set = set(current_nodes).difference(self.nodes)
        
        
        return list(new_set)
        
        

            
class ProgressBar(object):
    """
    Manipulate the maya progress bar.
    
    Args
        title (str): The name of the progress bar.
        count (int): The number of items to iterate in the progress bar.
    """
    
    def __init__(self, title, count):
        if is_batch():
            return
        
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar');
    
        self.progress_ui = cmds.progressBar( gMainProgressBar,
                                        edit=True,
                                        beginProgress=True,
                                        isInterruptable=True,
                                        status= title,
                                        maxValue= count )
        
        global current_progress_bar 
        current_progress_bar = self
    
    def inc(self, inc = 1):
        """
        Set the current increment.
        """
        if is_batch():
            return
        
        cmds.progressBar(self.progress_ui, edit=True, step=inc)
        
            
    def end(self):
        """
        End the progress bar.
        """
        if is_batch():
            return
        
        cmds.progressBar(self.progress_ui, edit=True, ep = True)
        
    def status(self, status_string):
        """
        Set that status string of the progress bar.
        """
        if is_batch():
            return
        
        cmds.progressBar(self.progress_ui, edit=True, status = status_string)
        
    def break_signaled(self):
        """
        break the progress bar loop so that it stops and disappears.
        """
        if is_batch():
            return True
        
        break_progress = cmds.progressBar(self.progress_ui, query=True, isCancelled=True )

        if break_progress:
            self.end()
            return True
        
        return False
    

def undo_off(function):
    """
    Maya sometimes has operations that generate a huge undo stack and use lots of memory.
    This is meant to handle turning off the undo temporarily for the duration of a function.
    
    Arg
        function: Pass in the instance of the fucntion to wrap.
    """
    
    def wrapper(*args, **kwargs):
        
        global current_progress_bar
        
        if not vtool.util.is_in_maya():
            return
        return_value = None
        
        undo_state = cmds.undoInfo(state = True, q = True)
        
        if undo_state:
            cmds.undoInfo(state = False)
        
        try:
            return_value = function(*args, **kwargs)
        except:
            
            if undo_state:
                cmds.undoInfo( state = True )
                    
                # do not remove
                print traceback.format_exc()
                
            raise(RuntimeError)
        
            if current_progress_bar:
                current_progress_bar.end()
                current_progress_bar = None
        
        if undo_state:          
            cmds.undoInfo( state = True )
        
        return return_value
        
    return wrapper

def undo_chunk(function):
    """
    Maya sometimes has operations that generate a huge undo stack and use lots of memory.
    This is meant to handle creating one undo chunk for a function that has many small operations.
    
    Arg
        function: Pass in the instance of the fucntion to wrap.
    """
    
    def wrapper(*args, **kwargs):
        
        global undo_chunk_active
        global current_progress_bar
        
        if not vtool.util.is_in_maya():
            return
    
        undo_state = cmds.undoInfo(state = True, q = True)
        
        return_value = None
        
        closed = True
        
        if not undo_chunk_active and undo_state:
            cmds.undoInfo(openChunk = True)
                        
            undo_chunk_active = True
            closed = False
        
        try:
            return_value = function(*args, **kwargs)
        except:
            
            if undo_chunk_active:
                cmds.undoInfo(closeChunk = True)
                
                closed = True
                
                undo_chunk_active = False
            
                # do not remove
                print traceback.format_exc()
            
            raise(RuntimeError)

            if current_progress_bar:
                current_progress_bar.end()
                current_progress_bar = None
            
        if not closed:
            if undo_chunk_active:
                cmds.undoInfo(closeChunk = True)
                
                undo_chunk_active = False

        
        return return_value
                     
    return wrapper


def is_batch():
    """
    Return 
        (bool): True if Maya is in batch mode.
    """
    
    return cmds.about(batch = True)

def is_transform(node):
    """
    Is the node a transform.
    
    Args
        node (str): The name of the node to test.
    
    Return
        (bool)
    """
    
    if not cmds.objExists(node):
        return False
    
    if cmds.objectType(node, isAType = 'transform'):
        return True
    
    return False

def is_a_shape(node):
    """
    Test wether the node is a shape.
    
    Args
        node (str): The name of a node.
        
    Return
        bool
    """
    if cmds.objectType(node, isAType = 'shape'):
        return True
    
    return False
    
def is_referenced(node):
    """
    Args
        node (str): Name of a node in maya. Check to see if it is referenced.
        
    Return
        (bool)
    """
    if not cmds.objExists(node):
        return False
    
    is_node_referenced = cmds.referenceQuery(node, isNodeReferenced = True)
    
    return is_node_referenced

def inc_name(name):
    """
    Finds a unique name by adding a number to the end.
    
    Args
        name (str): Name to start from. 
    
    Return
        (str): Modified name, number added if not unique..
    """
    
    unique = FindUniqueName(name)
    return unique.get()

def prefix_name(node, prefix, name, separator = '_'):
    """
    Convenience to quickly rename a Maya node.
    
    Args
        node (str): Name of a node in maya to rename.
        prefix (str)
        name (str)
        separator (str)
        
    Return
        (str): prefix + separator + name
    
    """
    new_name = cmds.rename(node, '%s%s%s' % (prefix,separator, name))
    
    return new_name

def prefix_hierarchy(top_group, prefix):
    """
    Prefix all the names in a hierarchy.
    
    Args
        top_group (str): Name of the top node of a hierarchy.
        prefix (str): Prefix to add in front of top_group and all children.
        
    Return
        (list): The renamed hierarchy including top_group.
    """
    
    relatives = cmds.listRelatives(top_group, ad = True)
     
    relatives.append(top_group)
    
    renamed = []
    
    for relative in relatives:

        new_name = cmds.rename(relative, '%s_%s' % (prefix, relative))
        renamed.append(new_name)
    
    renamed.reverse()
    
    return renamed
    
def pad_number(name):
    """
    Add a number to a name.
    """
    
    number = vtool.util.get_last_number(name)
    
    number_string = str(number)
    
    index = name.rfind(number_string)

    if number < 10:
        number_string = number_string.zfill(2)
        
    new_name =  name[0:index] + number_string + name[index+1:]
    renamed = cmds.rename(name, new_name)
    
    return renamed

        
def get_outliner_sets():
    """
    Get the sets found in the outliner.
    
    Return
        (list): List of sets in the outliner.
    """
    
    sets = cmds.ls(type = 'objectSet')
                
    top_sets = []
        
    for object_set in sets:
        if object_set == 'defaultObjectSet':
            continue
        
        outputs = cmds.listConnections(object_set, 
                                    plugs = False, 
                                    connections = False, 
                                    destination = True, 
                                    source = False,
                                    skipConversionNodes = True)
            
        if not outputs:
            top_sets.append( object_set )
            
            
    return top_sets

def get_top_dag_nodes(exclude_cameras = True):
    """
    Get transforms that sit at the very top of the hierarchy.
    
    Return
        (list)
    """
    
    top_transforms = cmds.ls(assemblies = True)
    
    cameras = ['persp', 'top', 'front', 'side']
    
    for camera in cameras:
        if camera in top_transforms:
            top_transforms.remove(camera)
     
    return top_transforms 

    
def get_shapes(transform):
    """
    Get all the shapes under a transform.
    
    Args
        transform (str): The name of a transform.
        
    Return
        list: The names of shapes under the transform
    """
    if is_a_shape(transform):
        parent = cmds.listRelatives(transform, p = True, f = True)
        return cmds.listRelatives(parent, s = True, f = True)
    
    return cmds.listRelatives(transform, s = True, f = True)
    
def get_node_types(nodes, return_shape_type = True):
    """
    Get the maya node types for the nodes supplied.
    
    Return
        (dict[node_type_name]): node dict of matching nodes
    """
    
    found_type = {}
    
    for node in nodes:
        node_type = cmds.nodeType(node)
        
        if node_type == 'transform':
            
            if return_shape_type:
                shapes = get_shapes(node)
                
                if shapes:
                    node_type = cmds.nodeType(shapes[0])
        
        if not node_type in found_type:
            found_type[node_type] = []
            
        found_type[node_type].append(node)
        
    return found_type
     
def get_basename(name, remove_namespace = True):
    """
    Get the basename in a hierarchy name.
    If top|model|face is supplied, face will be returned.
    """
    
    split_name = name.split('|')
    
    basename = split_name[-1]
    
    if remove_namespace:
        split_basename = basename.split(':')
        return split_basename[-1]
    
    return split_name[-1]

def delete_unknown_nodes():
    """
    This will find all unknown nodes. Unlock and delete them.
    """
    
    unknown = cmds.ls(type = 'unknown')

    for node in unknown:
        if cmds.objExists(node):
            cmds.lockNode(node, lock = False)
            cmds.delete(node)

def rename_shapes(transform):
    """
    Rename all the shapes under a transform. 
    Renames them to match the name of the transform.
    
    Args
        transform (str): The name of a transform.
    """
    
    shapes = get_shapes(transform)
    
    if shapes:
        cmds.rename(shapes[0], '%sShape' % transform)
        
    if len(shapes) == 1:
        return
    
    if not shapes:
        return
    
    inc = 1
    for shape in shapes[1:]:
        
        cmds.rename(shape, '%sShape%s' % (transform, inc))
        inc += 1

def get_shapes_in_hierarchy(transform):
    """
    Get all the shapes in the child hierarchy excluding intermediates.
    This is good when calculating bounding box of a group.
    
    Args
        transform (str): The name of a transform.
        
    Return
        list: The list of shape nodes.
    """
    hierarchy = [transform]
    
    relatives = cmds.listRelatives(transform, ad = True, type = 'transform', f = True)
    
    if relatives:
        hierarchy += relatives
    
    shapes = []
    
    for child in hierarchy:
        
        found_shapes = get_shapes(child)
        sifted_shapes = []
        
        if not found_shapes:
            continue
        
        for found_shape in found_shapes:
            
            if cmds.getAttr('%s.intermediateObject' % found_shape):
                continue
            
            sifted_shapes.append( found_shape )
            
        if sifted_shapes:
            shapes += sifted_shapes
    
    return shapes

def has_shape_of_type(node, maya_type):
    """
    Test wether the node has a shape of the supplied type.
    
    Args
        node (str): The name of a node.
        maya_type (str): Can be a mesh, nurbsCurve, or any maya shape type. 
        
    Return
        bool
    """
    test = None
    
    if cmds.objectType(node, isAType = 'shape'):
        test = node
        
    if not cmds.objectType(node, isAType = 'shape'):
        shapes = get_shapes(node)
        
        if shapes:
            test = shapes[0]
        
    if test:
        if maya_type == cmds.nodeType(test):
            return True

def get_component_count(transform):
    """
    Get the number of components under a transform. 
    This does not include hierarchy.
    
    Args
        transform (str): The name of a transform.
    
    Return
        int: The number of components under transform, eg. verts, cvs, etc.
    """
    
    components = get_components(transform)
    
    return len( cmds.ls(components[0], flatten = True) )

def get_components(transform):
    """
    Get the name of the components under a transform.  
    This does not include hierarchy.
    
    Args
        transform (str): The name of a transform.
        
    Return
        list: The name of all components under transform, eg verts, cvs, etc.
    """
    
    shapes = get_shapes(transform)
    
    return get_components_from_shapes(shapes)

def get_components_in_hierarchy(transform):
    """
    Get the components in the hierarchy.
    This includes all transforms with shapes parented under the transform.
    
    Args
        transform (str): The name of a transform.
        
    Return
        list: The name of all components under transform, eg verts, cvs, etc.
    """
    
    shapes = get_shapes_in_hierarchy(transform)
    
    return get_components_from_shapes(shapes)

def get_components_from_shapes(shapes = None):
    """
    Get the components from the a list of shapes.  Curntly supports cv and vtx components
    
    Args
        shapes (list): List of shape names.
        
    Return
        list: The components of the supplied shapes.
    """
    components = []
    if shapes:
        for shape in shapes:
            
            found_components = None
            
            if cmds.nodeType(shape) == 'nurbsSurface':
                found_components = '%s.cv[*]' % shape
            
            if cmds.nodeType(shape) == 'nurbsCurve':
                found_components = '%s.cv[*]' % shape
            
            if cmds.nodeType(shape) == 'mesh':
                found_components = '%s.vtx[*]' % shape
            
            if found_components:
                components.append( found_components )
            
    return components

def create_display_layer(name, nodes):
    """
    Create a display layer containing the supplied nodes.
    
    Args
        name (str): The name to give the display layer.
        nodes (str): The nodes that should be in the display layer.
        
    """
    layer = cmds.createDisplayLayer( name = name )
    cmds.editDisplayLayerMembers( layer, nodes, noRecurse = True)
    cmds.setAttr( '%s.displayType' % layer, 2 )

def delete_display_layers():
    """
    Deletes all display layers.
        
    
    """
    layers = cmds.ls('displayLayer')
    
    for layer in layers:
        cmds.delete(layer)

#--- ui

def get_visible_hud_displays():
    """
    Get viewport hud displays.
    
    Return
        (list):  List of names of heads up displays.
    """    
    
    found = []
        
    displays = cmds.headsUpDisplay(q = True, lh = True)
        
    for display in displays:
        visible = cmds.headsUpDisplay(display, q = True, vis = True)
        
        if visible:
            found.append(display)
        
    return found

def set_hud_visibility(bool_value, displays = None):
    """
    Set the viewport hud display visibility.
    
    Args
        bool_value (bool): True turns visiliblity on, False turns it off.
        displays (list): List of heads up displays by name.
    """
    
    if not displays:
        displays = cmds.headsUpDisplay(q = True, lh = True) 
    
    for display in displays:
        cmds.headsUpDisplay(display, e = True, vis = bool_value)

def set_hud_lines(lines, name):
    """
    Set the viewport hud text for the named hud.
    
    Args
        lines (list): Each entry in the list is a new text line in the display.
        name (str): The name of the heads up display to work on.
    
    """
    
    inc = 0
    for line in lines:

        hud_name = '%s%s' % (name, inc)
    
        if cmds.headsUpDisplay(hud_name, ex = True):
            cmds.headsUpDisplay(hud_name, remove = True)
        
            
        cmds.headsUpDisplay( hud_name, section = 1, block = inc, blockSize = 'large', labelFontSize = "large", dataFontSize = 'large')
        cmds.headsUpDisplay( hud_name, edit = True, label = line)
        
        inc += 1

    
def show_channel_box():
    """
    Makes the channel box visible.
    """
    
    docks = mel.eval('global string $gUIComponentDockControlArray[]; string $goo[] = $gUIComponentDockControlArray;')
    
    if 'Channel Box / Layer Editor' in docks:
        index = docks.index('Channel Box / Layer Editor')
        dock = docks[index + 1]
        
        if cmds.dockControl(dock, q = True, visible = True):
            cmds.dockControl(dock, edit = True, visible = False)
            cmds.dockControl(dock, edit = True, visible = True)
        
        index = docks.index('Channel Box')
        dock = docks[index + 1]
            
        if cmds.dockControl(dock, q = True, visible = True):
            cmds.dockControl(dock, edit = True, visible = False)
            cmds.dockControl(dock, edit = True, visible = True)

def add_to_isolate_select(nodes):
    """
    Add the specified nodes into every viewport's isolate select. 
    This will only work on viewports that have isolate select turned on.
    Use when nodes are not being evaluated because isolate select causes them to be invisible.
    
    Args
        nodes (list): The nodes to add to isolate select.
    """
    
    if is_batch():
        return
    
    nodes = vtool.util.convert_to_sequence(nodes)
    
    model_panels = get_model_panels()
    
    for panel in model_panels:
        if cmds.isolateSelect(panel, q = True, state = True):
            for node in nodes: 
                cmds.isolateSelect(panel, addDagObject = node)
                
            #cmds.isolateSelect(panel, update = True)
            
def get_model_panels():
    """
    Good to use when editing viewports. 
    """
    return cmds.getPanel(type = 'modelPanel')


def get_current_audio_node():
    """
    Get the current audio node. Important when getting sound in a playblast.
    
    Return
        (str): Name of the audio node.
    """
    
    play_slider = mel.eval('global string $gPlayBackSlider; string $goo = $gPlayBackSlider')
    
    return cmds.timeControl(play_slider, q = True, s = True)

