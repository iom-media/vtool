# Copyright (C) 2014 Louis Vottero louis.vot@gmail.com    All rights reserved.

from vtool import qt_ui


import ui
import util

import maya.cmds as cmds
import maya.mel as mel
from _ctypes import alignment

if qt_ui.is_pyqt():
    from PyQt4 import QtGui, QtCore, Qt, uic
if qt_ui.is_pyside():
    from PySide import QtCore, QtGui

class PoseManager(ui.MayaWindow):
    
    title = 'Corrective Manager'
    
    def _define_main_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        return layout
        
    def _build_widgets(self):
        
        self.pose_set = PoseSetWidget()
        self.pose_list = PoseListWidget()
        
        self.pose = SculptWidget()
        self.pose.setMaximumHeight(200)
        
        
        self.pose_list.pose_list.itemSelectionChanged.connect(self.select_pose)
        
        self.pose_list.set_pose_widget(self.pose)
        self.pose_list.pose_renamed.connect(self._pose_renamed)
        
        
        
        self.pose_set.pose_reset.connect(self.pose_list.pose_reset)
        """
        self.pose.pose_mirror.connect(self.pose_list.mirror_pose)
        self.pose.pose_mesh.connect(self.pose.mesh_widget.add_mesh)
        #self.pose.pose_mesh_view.connect(self.pose_list.view_mesh)
        self.pose.mesh_change.connect(self.pose_list.change_mesh)
        self.pose.axis_change.connect(self.pose_list.pose_list.axis_change)
        self.pose.value_changed.connect(self.pose_list.value_changed)
        self.pose.parent_changed.connect(self.pose_list.parent_changed)
        self.pose.pose_enable_changed.connect(self.pose_list.pose_enable_changed)
        """
        
        #self.pose.pose_enable_changed.connect(self.pose_list.pose_enable_changed)
        
        self.main_layout.addWidget(self.pose_set)
        self.main_layout.addWidget(self.pose_list)
        self.main_layout.addWidget(self.pose)
        
    def _update_lists(self):
        self.pose_list.refresh()
        
    def _pose_renamed(self, new_name):
        
        new_name = str(new_name)
        self.pose.mesh_widget.set_pose(new_name)
        
    def select_pose(self):
        
        self.pose_list.pose_list.select_pose()
        
        items = self.pose_list.pose_list.selectedItems()
        
        if items:
            pose_name = items[0].text(0)
        
        if not items:
            return    
         
        pose_name = str(pose_name)
        self.pose.set_pose(pose_name)
            
    #def update_meshes(self, meshes, index):
    #    self.pose.mesh_widget.update_meshes(meshes, index) 

class PoseSetWidget(QtGui.QWidget): 
    
    pose_reset = qt_ui.create_signal()
    
    def __init__(self):
        
        super(PoseSetWidget, self).__init__()
        
        self.main_layout = QtGui.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)
            
        self._add_buttons()
        
        self.pose = None
        
    def _add_buttons(self):
        
        name_layout = QtGui.QHBoxLayout()
        
        button_default = QtGui.QPushButton('Set Default Pose')
        button_reset = QtGui.QPushButton('To Default Pose')
        
        button_reset.clicked.connect(self._button_reset)
        button_default.clicked.connect(self._button_default)
        
        
        self.main_layout.addWidget(button_reset)
        self.main_layout.addWidget(button_default)
        
        
    def _button_default(self):
        util.PoseManager().set_default_pose()
    
    def _button_reset(self):
        self.pose_reset.emit()
        util.PoseManager().set_pose_to_default()
        
class PoseListWidget(qt_ui.BasicWidget):
    
    pose_added = qt_ui.create_signal(object)
    pose_renamed = qt_ui.create_signal(object)
    pose_update = qt_ui.create_signal(object)
 
    def __init__(self):
        super(PoseListWidget, self).__init__()
             
    def _define_main_layout(self):
        layout = QtGui.QHBoxLayout()
        #layout.setAlignment(QtCore.Qt.AlignTop)
        return layout
        
    def _build_widgets(self):
        
        self.pose_list = PoseTreeWidget()
        
        self.pose_list.itemSelectionChanged.connect(self._update_pose_widget)
        
        
        self.pose_widget = PoseWidget()
        self.pose_widget.hide()
        
        #this may need love
        #self.pose_widget.pose_mirror.connect(self.mirror_pose)
        
        #self.pose.pose_mesh.connect(self.pose.mesh_widget.add_mesh)
        #self.pose.pose_mesh_view.connect(self.pose_list.view_mesh)
        
        #self.pose.mesh_change.connect(self.pose_list.change_mesh)
        
        #combo_list = ComboTreeWidget()
        
        #self.pose_list.itemSelectionChanged.connect(self.select_pose)
        
        self.pose_list.pose_renamed.connect(self._pose_renamed)
        
        
        self.main_layout.addWidget(self.pose_list)
        self.main_layout.addWidget(self.pose_widget)
        #self.main_layout.addWidget(combo_list)

    def _update_pose_widget(self):
        current_pose = self.pose_list._current_pose()
        
        items = self.pose_list.selectedItems()
        
        if items:
            self.pose_widget.show()
            
            self.pose_widget.set_pose(current_pose)
            
        if not items:
            self.pose_widget.hide()
            
        self.pose_update.emit(current_pose)

    def _pose_renamed(self, new_name):
        self.pose_renamed.emit(new_name)

        
    def set_pose_widget(self, widget):
        self.pose_list.pose_widget = widget
        
    def create_pose(self):
        self.pose_list.create_pose()
        
    def delete_pose(self):
        self.pose_list.delete_pose()

    def mirror_pose(self):
        self.pose_list.mirror_pose()
        
    def add_mesh(self):
        self.pose_list.add_mesh()
        
    def view_mesh(self):
        self.pose_list.view_mesh()
        
    def change_mesh(self, int):
        self.pose_list.mesh_change(int)
        
    def change_axis(self, string):
        
        self.pose_list.axis_change(string)
        #if self.pose:
        #    self.pose.set_axis(text)
        
    def pose_reset(self):
        item = self.pose_list.currentItem()
        
        item.setSelected(False)
        
    def value_changed(self, max_angle, max_distance, twist_on, twist):
        
        self.pose_list.value_changed(max_angle, max_distance, twist_on, twist)
        
    def parent_changed(self, parent):
        
        self.pose_list.parent_changed(parent)
        
    def pose_enable_changed(self, value):
        self.pose_list.pose_enable_changed(value)
        
    
       
     
class BaseTreeWidget(qt_ui.TreeWidget):
    
    pose_renamed = qt_ui.create_signal(object)
    
    def __init__(self):
        super(BaseTreeWidget, self).__init__()
        self.setSortingEnabled(True)
        self.setSelectionMode(self.ExtendedSelection)
        
        self.text_edit = False
        
        self._populate_list()
        
        self.pose_widget = None

    """
    def _edit_finish(self, item):
        item = super(BaseTreeWidget, self)._edit_finish(item)
        
        if not item:
            return
        
        new_name = str(item.text(0))
        
        new_name = new_name.replace(' ', '_')
        
        if not self.old_name == new_name:
            new_name = self.rename_pose(str(self.old_name), new_name)
        
        if self.old_name == new_name:
            new_name = None
        
        
        if new_name:
            item.setText(0, new_name)
        
        if not new_name and self.old_name:
            item.setText(0, self.old_name ) 
    """
    

    def _populate_list(self):
        pass

    def _current_pose(self):
        item = self.currentItem()
        if item:
            return str(item.text(0))

    def _get_selected_items(self, get_names = False):
        selected = self.selectedIndexes()
        
        items = []
        names = []
        
        for index in selected:
            
            item = self.itemFromIndex(index)
            
            if not get_names:
                items.append(item)
            if get_names:
                name = str( item.text(0) )
                names.append(name)

        if not get_names:
            return items
        if get_names:
            return names

    def _rename_pose(self):
        
        items = self.selectedItems()
        
        item = None
        
        if items:
            item = items[0]
            
        if not items:
            return
        
        self.old_name = item.text(0)
        
        new_name = qt_ui.get_new_name('Please specify a name.', self, old_name = self.old_name)
                
        item.setText(0, new_name)
        
        state = self._item_rename_valid(self.old_name, item)
        
        if state:
            self._item_renamed(item)
        if not state:
            
            item.setText(0, self.old_name)
            
        self.pose_renamed.emit(item.text(0))
        
    def _item_renamed(self, item):    
        
        new_name = item.text(0)
        
        new_name = self.rename_pose(self.old_name, new_name)
        item.setText(0, new_name)
    

    def refresh(self):
        self._populate_list()
        
    #def create_pose(self):
    #    pass


    def rename_pose(self, pose_name, new_name):
        
        self.last_selection = None
        
        return util.PoseManager().rename_pose(str(pose_name), str(new_name))


            
    def view_mesh(self):
        current_str = self.pose_widget.get_current_mesh()
        pose_name = self._current_pose()
        
        if not pose_name:
            return
        
        if not current_str == '- new mesh -':
            util.PoseManager().toggle_visibility(pose_name, True)
            
            
    def mesh_change(self, index):
        
        pose_name = self._current_pose()
        
        if not pose_name:
            return
        
        pose = util.PoseControl()
        pose.set_pose(pose_name)
        pose.set_mesh_index(index)
        
    def delete_pose(self):
        
        permission = qt_ui.get_permission('Delete Pose?', self)
        
        if not permission:
            return
        
        pose = self._current_pose()
        item = self.currentItem()
        
        if not pose:
            return
        
        util.PoseManager().delete_pose(pose)
        
        index = self.indexOfTopLevelItem(item)
        self.takeTopLevelItem(index)
        del(item)
        
        self.last_selection = None
        
    def select_pose(self):
        pass
    
    def parent_changed(self, parent):
        
        pose_name = self._current_pose()
        
        if not pose_name:
            return
        
        pose = util.PoseControl()
        pose.set_pose(pose_name)
        
        pose.set_parent(parent)
        
    def pose_enable_changed(self, value):
        
        pose_name = self._current_pose()
        
        if not pose_name:
            return
        
        cmds.setAttr('%s.enable' % pose_name, value)
        
class PoseTreeWidget(BaseTreeWidget):

    def __init__(self):
        
        self.item_context = []
        
        super(PoseTreeWidget, self).__init__()
        self.setHeaderLabels(['pose'])
        
        self.last_selection = []
    
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._item_menu)
        
        self._create_context_menu()
        
    def mousePressEvent(self, event):
        
        model_index =  self.indexAt(event.pos())
        
        """
        if model_index.column() > 0:
            self.clearSelection()
        
        if model_index is None:
            self.clearSelection()
        """
        
        item = self.itemAt(event.pos())
        
        if not item or model_index.column() == 1:
            self.clearSelection()
            
        
        if event.button() == QtCore.Qt.RightButton:
            return
        
        if model_index.column() == 0 and item:
            super(PoseTreeWidget, self).mousePressEvent(event)
        
    def _item_menu(self, position):
                
        item = self.itemAt(position)
            
        if item:
            for item in self.item_context:
                item.setVisible(True)
            
        if not item:
            for item in self.item_context:
                item.setVisible(False)
        
        
        self.context_menu.exec_(self.viewport().mapToGlobal(position))
        
    def _create_context_menu(self):
        
        self.context_menu = QtGui.QMenu()
        
        pose_menu = self.context_menu.addMenu('New Pose')
        
        self.create_no_reader = pose_menu.addAction('No Reader')
        self.create_cone = pose_menu.addAction('Cone')
        self.create_rbf = pose_menu.addAction('RBF')
        self.context_menu.addSeparator()
        self.rename_action = self.context_menu.addAction('Rename')
        self.delete_action = self.context_menu.addAction('Delete')
        self.context_menu.addSeparator()
        self.select_pose_action = self.context_menu.addAction('Select Pose')
        self.select_joint_action = self.context_menu.addAction('Select Joint')
        self.select_blend_action = self.context_menu.addAction('Select Blendshape')
        self.context_menu.addSeparator()
        self.set_pose_action = self.context_menu.addAction('Update Pose')
        self.reset_sculpts_action = self.context_menu.addAction('Reset Sculpt')
        self.context_menu.addSeparator()
        self.refresh_action = self.context_menu.addAction('Refresh')
        
        self.item_context = [self.rename_action, 
                        self.delete_action,
                        self.reset_sculpts_action,
                        self.set_pose_action,
                        self.select_joint_action,
                        self.select_pose_action,
                        self.select_blend_action]
        
        self.create_cone.triggered.connect(self.create_cone_pose)
        self.create_no_reader.triggered.connect(self.create_no_reader_pose)
        self.rename_action.triggered.connect(self._rename_pose)
        self.delete_action.triggered.connect(self.delete_pose)
        
        self.select_joint_action.triggered.connect(self._select_joint)
        self.select_pose_action.triggered.connect(self._select_pose)
        self.set_pose_action.triggered.connect(self._set_pose_data)
        self.reset_sculpts_action.triggered.connect(self._reset_sculpts)
        
        self.select_blend_action.triggered.connect(self._select_blend)
        
        
        self.refresh_action.triggered.connect(self._populate_list)
    
    def _populate_list(self):
        
        self.clear()
        
        poses = util.PoseManager().get_poses()
        
        if not poses:
            return
        
        for pose in poses:
            
            pose_type = cmds.getAttr('%s.type' % pose)
            if pose_type == 'cone':
                self.create_cone_pose(pose, select = False)
            if pose_type == 'no reader':
                self.create_no_reader_pose(pose, select = False)
            
            
    def _select_joint(self):
        name = self._current_pose()
        transform = util.PoseManager().get_transform(name)
        
        util.show_channel_box()
        
        cmds.select(transform)
        
    def _select_pose(self):
        
        name = self._current_pose()
        
        control = util.PoseManager().get_pose_control(name)
        
        util.show_channel_box()
        
        cmds.select(control)

    def _set_pose_data(self):
        
        name = self._current_pose()
        control = util.PoseManager().get_pose_control(name)
        util.PoseManager().set_pose_data(control)

    def _reset_sculpts(self):
        
        name = self._current_pose()
        util.PoseManager().reset_pose(name)
        
    def _select_blend(self):
        
        name = self._current_pose()
        
        if not name:
            return
        
        pose_inst = util.PoseControl()
        pose_inst.set_pose(name)
        
        blend = pose_inst.get_blendshape()
        
        util.show_channel_box()
           
        cmds.select(blend, r = True)
        
    """
    def _get_pose_values(self, pose):
                
        max_angle = cmds.getAttr('%s.maxAngle' % pose)
        max_distance = cmds.getAttr('%s.maxDistance' % pose)
        twist_on = cmds.getAttr('%s.twistOffOn' % pose)
        twist = cmds.getAttr('%s.maxTwist' % pose)
        
        return max_angle, max_distance, twist_on, twist
    """ 
    def create_cone_pose(self, name = None, select = True):
        
        pose_names = self._get_selected_items(True)
        
        pose = None
        
        if name:
            pose = name
        
        if not pose:
            pose = util.PoseManager().create_cone_pose()
        
        if not pose:
            return
        
        
        item = QtGui.QTreeWidgetItem()
        item.setText(0, pose)
        self.addTopLevelItem(item)
        
        if select:
            item.setSelected(True)
            self.setCurrentItem(item)

    def create_no_reader_pose(self, name = None, select = True):

        pose_names = self._get_selected_items(True)
        
        pose = None
        
        if name:
            pose = name
        
        if not pose:
            pose = util.PoseManager().create_no_reader_pose()
        
        if not pose:
            return
        
        
        item = QtGui.QTreeWidgetItem()
        item.setText(0, pose)
        self.addTopLevelItem(item)
        
        if select:
            item.setSelected(True)
            self.setCurrentItem(item)


    def mirror_pose(self):
        
        pose = self._current_pose()
        item = self.currentItem()
        
        if not pose:
            return
        
        mirror = util.PoseManager().mirror_pose(pose)
        
        self.refresh()
        self.select_pose(mirror)
        
        #items = self.findItems(mirror, Qt.QMatchFlags(0), 0)
        
        #self.setItemSelected(item, True)
        

        
    def select_pose(self, pose_name = None):
        
        items = self.selectedItems()
        if not items:
            return
        
        if self.last_selection: 
            
            util.PoseManager().visibility_off(self.last_selection[0])
        
        pose_names = self._get_selected_items(get_names = True)
        
        if len( pose_names ) > 1:
            
            util.PoseManager().set_poses(pose_names)
            
            values = self._get_pose_values(pose_names[0])
            
            self.pose_widget.set_values(values[0], values[1], values[2], values[3])
            
            value = cmds.getAttr('%s.enable' % pose_names[0])
            self.pose_widget.set_pose_enable(value)    
            
            return
        
        if len( pose_names ) == 1:
            pose = pose_names[0]
            
            #cmds.select(pose)
            
            pose = str(pose)
            
            util.PoseManager().set_pose(pose)
            #self.update_meshes(pose)
            
            #values = self._get_pose_values(pose)
            
            #this needs to be added back in
            #self.pose_widget.set_values(values[0], values[1], values[2], values[3])
                        
            pose_inst = util.PoseControl()
            pose_inst.set_pose(pose)
            #parent = pose_inst.get_parent()
            
            #this needs to be added back in
            #self.pose_widget.set_pose_parent_name(parent)
            
            
        value = cmds.getAttr('%s.enable' % pose_names[0])
        #this needs to be added back in
        #self.pose_widget.set_pose_enable(value)
            
        self.last_selection = pose_names
            
    def value_changed(self, max_angle, max_distance, twist_on, twist):
        poses = self._get_selected_items(True)
        
        if not poses:
            return
        
        cmds.setAttr('%s.maxAngle' % poses[-1], max_angle)
        cmds.setAttr('%s.maxDistance' % poses[-1], max_distance)
        cmds.setAttr('%s.maxTwist' % poses[-1], twist)
        cmds.setAttr('%s.twistOffOn' % poses[-1], twist_on)
        
class ComboTreeWidget(BaseTreeWidget):
    def __init__(self):
        super(ComboTreeWidget, self).__init__()
        self.setHeaderLabels(['combo'])
        
class PoseTreeItem(QtGui.QTreeWidgetItem):
    def __init__(self, name):
        super(PoseTreeItem, self).__init__()
        
        self.pose = None
        
        self.setText(0, name)
        
    def _rename(self, new_name):
        
        if self.pose.rename(new_name):
            return self.pose.pose_control
        
    def load_pose(self, pose):
        if not util.PoseControl().is_a_pose(pose):
            return
    
        #self.pose = util.PoseControl()
        #self.pose.set_pose(pose)
        #self.pose.select()
       
class PoseWidget(qt_ui.BasicWidget):

    pose_mirror = qt_ui.create_signal() 
    pose_mesh = qt_ui.create_signal()
    mesh_change = qt_ui.create_signal(object)
    pose_enable_changed = qt_ui.create_signal(object)
    
    def __init__(self):
        super(PoseWidget, self).__init__()
        
        self.pose_name = None
        self.pose_control_widget = None
    
    def _define_main_layout(self):
        layout = QtGui.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        return layout
    
    def _build_widgets(self):
        
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
        #self.setMaximumHeight(200)
        self.setMaximumWidth(200)
        
        
        #self.mesh_widget = MeshWidget()
        """
        self.pose_control_widget.pose_mirror.connect(self._pose_mirror)
        self.pose_control_widget.pose_mesh.connect(self._pose_mesh)
        self.pose_control_widget.axis_change.connect(self._axis_change)
        self.pose_control_widget.value_changed.connect(self._value_changed)
        self.pose_control_widget.parent_change.connect(self._parent_changed)
        self.pose_control_widget.pose_enable_change.connect(self._pose_enable_changed)
        """
        
        
        #self.main_layout.addWidget(self.mesh_widget) 

    def _button_mesh(self):
        self.pose_mesh.emit()

    def _pose_mirror(self):
        self.pose_mirror.emit()
        
    def _pose_mesh(self):
        self.pose_mesh.emit()
        
    def _axis_change(self, value):
        self.axis_change.emit(value)
        
    def _mesh_change(self, value):
        self.mesh_change.emit(value)
        
    def _value_changed(self, value1, value2, value3, value4):
        self.value_changed.emit(value1, value2, value3, value4)
        
    def _parent_changed(self, parent):
        self.parent_changed.emit(parent)
        
    def _pose_enable_changed(self, value):
        self.pose_enable_changed.emit(value)

    def update_meshes(self, meshes, index):
        self.mesh_widget.update_meshes(meshes, index)
        
    def set_pose(self, pose_name):
        self.pose_name = pose_name
        
        pose_type = cmds.getAttr('%s.type' % pose_name)
        
        
        
        if self.pose_control_widget:
            self.deleteLater(self.pose_control_widget)
            self.pose_control_widget = None
        
        if pose_type == 'no reader':
            self.pose_control_widget = PoseNoReaderWidget()
            
        if pose_type == 'cone':
            self.pose_control_widget = PoseConeWidget()
        
        self.pose_control_widget.set_pose(pose_name)
        
        self.main_layout.addWidget(self.pose_control_widget)
        
    def set_values(self, angle, distance, twist_on, twist):
        self.pose_control_widget.set_values(angle, distance, twist_on, twist)
        
    def set_pose_parent_name(self, parent_name):

        if not parent_name:
            parent_name = ''
        
        self.pose_control_widget.set_parent_name(parent_name)
        
    def set_pose_enable(self, value):
        self.pose_control_widget.set_pose_enable(value)
        
    def get_current_mesh(self):
        return self.mesh_widget.get_current_mesh()


class MeshWidget(qt_ui.BasicWidget):
    
    mesh_change = qt_ui.create_signal(object)
    
    def __init__(self):
        super(MeshWidget, self).__init__()
        
        self.pose_name = None
        
        self.mesh_list.setSelectionMode(self.mesh_list.ExtendedSelection)
    
    def sizeHint(self):    
        return QtCore.QSize(200,100)
        
    
    def _build_widgets(self):
        #self.mesh_label = QtGui.QLabel('Sculpts')
        self.mesh_list = QtGui.QListWidget()
        
        self.mesh_list.itemSelectionChanged.connect(self._item_selected)
        
        #self.main_layout.addWidget(self.mesh_label, alignment = QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.mesh_list)
        
        

    def _mesh_change(self, int_value):    
        self.mesh_change.emit(int_value)

    def get_current_meshes(self):
        items = self.mesh_list.selectedItems()
        
        found = []
        
        for item in items:
            found.append( str( item.text() ) )
        
        return found

    def _update_meshes(self, pose_name):
        
        pose = util.BasePoseControl()
        pose.set_pose(pose_name)
        
        
        
        meshes =  pose.get_target_meshes()
        
        self.update_meshes(meshes,pose.mesh_index)
        
    @util.undo_chunk
    def add_mesh(self):
                          
        print 'adding mesh'
                          
        current_meshes = self.get_current_meshes()
              
        pose_name = self.pose_name
            
        if not pose_name:
            return
        
        new_meshes = []
        meshes = []
        
        selection = cmds.ls(sl = True, l = True)
        
        if selection:
        
            mesh_count = self.mesh_list.count()
            
            for thing in selection:
                
                if util.has_shape_of_type(thing, 'mesh'):
                    
                    pass_mesh = thing
                    
                    for inc in range(0, mesh_count):
                        
                        test_item = self.mesh_list.item(inc)
                        
                        if str( test_item.text() ) == thing:
                            pass_mesh = None
                            
                            meshes.append(thing)
                            
                        
                    if pass_mesh:    
                        new_meshes.append(pass_mesh)
        
        if new_meshes or not current_meshes:
                    
            if new_meshes:
                
                util.PoseManager().add_mesh_to_pose(pose_name, new_meshes)
                
                
        
            if not current_meshes:
            
                util.PoseManager().add_mesh_to_pose(pose_name)
                            
        
            self._update_meshes(pose_name)
                 
        if meshes:
            
            self.mesh_list.clearSelection()
            
            for mesh in meshes:
                
                if not mesh:
                    continue
                
                index = util.PoseManager().get_mesh_index(pose_name, mesh)
                
                
                item = self.mesh_list.item(index)
                if item:
                    
                    item.setSelected(True)
                    
                
                util.PoseManager().toggle_visibility(pose_name, mesh_index = index)
            
            return
         
            
        if current_meshes:
            
            indices = self.mesh_list.selectedIndexes()
            if indices:
                for index in indices:
                    
                    index = index.row()
                
                    util.PoseManager().toggle_visibility(pose_name, mesh_index= index)
        
    def _item_selected(self):
        pass
        """
        indices = self.mesh_list.selectedIndexes()
        
        if indices:
            index = indices[0]
            index = index.row()
        
            util.PoseManager().toggle_visibility(self.pose_name, mesh_index = index)
        """
        
    def update_meshes(self, meshes = [], index = 0):
        self.mesh_list.clear()    
        
        for mesh in meshes:
        
            item = QtGui.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(0,30))
            item.setText(mesh)
            self.mesh_list.addItem(item)
           
            
        item = self.mesh_list.item(index)
        if item:
            item.setSelected(True)
            
    def set_pose(self, pose_name):
        
        self.pose_name = pose_name

        self._update_meshes(pose_name)
            
        


        

class SculptWidget(qt_ui.BasicWidget):
    
    def __init__(self):
        super(SculptWidget, self).__init__()
        
        self.pose = None
    
    def sizeHint(self):
        
        return QtCore.QSize(200,200)
        
    def _define_main_layout(self):
        return QtGui.QVBoxLayout()
    
    def _button_mesh(self):
        print self.pose
        self.mesh_widget.add_mesh()
        #self.pose_mesh.emit()

    def _button_mirror(self):
        self.pose_mirror.emit()
    
    def _build_widgets(self):
        
        self.slider = QtGui.QSlider()
        
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMaximumHeight(30)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setTickPosition(self.slider.TicksBothSides)
        
        
        self.slider.valueChanged.connect(self._pose_enable)
        
        button_mesh = QtGui.QPushButton('Sculpt')
        button_mesh.setMinimumHeight(50)
        button_mesh.setMinimumWidth(50)
        
        v_layout = QtGui.QHBoxLayout()
        v_layout.addWidget(button_mesh)
        v_layout.addSpacing(20)
        v_layout.addWidget(self.slider)
        v_layout.addSpacing(20)
        
        button_view = QtGui.QPushButton('View')

        button_mesh.clicked.connect(self._button_mesh)
        
        button_mirror = QtGui.QPushButton('Mirror')
        
        button_mirror.clicked.connect(self._button_mirror)

        self.mesh_widget = MeshWidget()

        #self.main_layout.addWidget(button_mesh)
        #self.main_layout.addWidget(self.slider)
        self.main_layout.addLayout(v_layout)
        #self.main_layout.addWidget(self.slider)
        self.main_layout.addWidget(self.mesh_widget)
        #self.main_layout.addWidget(button_mirror)

    def _pose_enable(self, value):
        
        value = value/100.00
        
        if not self.pose:
            return
        
        cmds.setAttr('%s.enable' % self.pose, value)
      
    def set_pose(self, pose_name):
        
        if not pose_name:
            self.pose = None
            return
        
        self.pose = pose_name
        
        self.mesh_widget.set_pose(pose_name)
        
        self.set_pose_enable()
        
    def set_pose_enable(self):
        
        value = cmds.getAttr('%s.enable' % self.pose)
        
        value = value*100
        self.slider.setValue(value)
        

#--- pose widgets

class PoseBaseWidget(qt_ui.BasicWidget):
    
    def __init__(self):
        
        super(PoseBaseWidget, self).__init__()
        self.pose = None
    
    def set_pose(self, pose_name):
        
        if not pose_name:
            self.pose = None
            return
        
        self.pose = pose_name

class PoseNoReaderWidget(PoseBaseWidget):
    pass

class PoseConeWidget(PoseBaseWidget):
    
    pose_mirror = qt_ui.create_signal() 
    pose_mesh = qt_ui.create_signal()
    pose_mesh_view = qt_ui.create_signal()
    axis_change = qt_ui.create_signal(object)
    mesh_change = qt_ui.create_signal(object)
    #parent_change = qt_ui.create_signal(object)
    pose_enable_change = qt_ui.create_signal(object)
    
    value_changed = qt_ui.create_signal(object, object, object, object)
    
    
    
    def __init__(self):
        
        super(PoseConeWidget, self).__init__()
        
        self.emit_parent = True
        
    def _define_main_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        return QtGui.QVBoxLayout()
        
    def sizeHint(self):
        
        return QtCore.QSize(150,400)
        
        
    def _build_widgets(self):
        
        self.layout_pose = QtGui.QVBoxLayout()
        
        self.combo_label = QtGui.QLabel('Alignment')
        
        self.combo_axis = QtGui.QComboBox()
        self.combo_axis.addItems(['X','Y','Z'])
        
        layout_combo = QtGui.QHBoxLayout()
        
        layout_combo.addWidget(self.combo_label, alignment = QtCore.Qt.AlignRight)
        layout_combo.addWidget(self.combo_axis)
        
        layout_slide = QtGui.QVBoxLayout()
        
        layout_angle, self.max_angle = self._add_spin_widget('Max Angle')
        layout_distance, self.max_distance = self._add_spin_widget('Max Distance')
        layout_twist, self.twist = self._add_spin_widget('Max twist')
        layout_twist_on, self.twist_on = self._add_spin_widget('Twist')
                        
        self.max_angle.setRange(0, 180)
        
        self.twist.setRange(0, 180)
        self.twist_on.setRange(0,1)
        self.max_distance.setMinimum(0)
        self.max_distance.setMaximum(10000000)
        
        parent_combo = QtGui.QHBoxLayout()
        
        parent_label = QtGui.QLabel('Parent')
        self.parent_text = QtGui.QLineEdit()
        
        self.parent_text.textChanged.connect(self._parent_name_change)
        
        parent_combo.addWidget(parent_label, alignment = QtCore.Qt.AlignRight)
        parent_combo.addWidget(self.parent_text)
        
        
        self.slider = QtGui.QSlider()
        #self.slider.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setTickPosition(self.slider.TicksBothSides)
        
        
        self.max_angle.valueChanged.connect(self._value_changed)
        self.max_distance.valueChanged.connect(self._value_changed)
        self.twist_on.valueChanged.connect(self._value_changed)
        self.twist.valueChanged.connect(self._value_changed)
        self.combo_axis.currentIndexChanged.connect(self._axis_change)
        self.slider.valueChanged.connect(self._pose_enable)
        
        
        #layout_slide.addWidget(self.slider)
        layout_slide.addLayout(parent_combo)
        layout_slide.addLayout(layout_combo)
        layout_slide.addLayout(layout_angle)
        layout_slide.addLayout(layout_twist)
        layout_slide.addLayout(layout_distance)
        layout_slide.addLayout(layout_twist_on)
        
        
        #button_mesh = QtGui.QPushButton('Sculpt')
        
        #button_view = QtGui.QPushButton('View')

        #button_mesh.clicked.connect(self._button_mesh)
        
        #button_mirror = QtGui.QPushButton('Mirror')
        
        #button_mirror.clicked.connect(self._button_mirror)

        #self.main_layout.addWidget(button_mesh)
        self.main_layout.addLayout(layout_slide)
        #self.main_layout.addWidget(button_mirror)
        
    def _add_spin_widget(self, name):
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        
        label = QtGui.QLabel(name)
        label.setAlignment(QtCore.Qt.AlignRight)
        
        widget = QtGui.QDoubleSpinBox()
        
        widget.setCorrectionMode(widget.CorrectToNearestValue)
        widget.setWrapping(False)
        layout.addWidget(label)
        layout.addWidget(widget)
        
        return layout, widget      


    def _button_mirror(self):
        self.pose_mirror.emit()

    def _button_mesh(self):
        self.pose_mesh.emit()

        
    def _axis_change(self):
        
        text = str( self.combo_axis.currentText() )
        self.axis_change(text)
        #self.axis_change.emit(text)
        
    def _parent_name_change(self):
        
        self.parent_text.setStyleSheet('QLineEdit{background:red}')
        
        text = str( self.parent_text.text() )
        
        if not text:
            #self.parent_text.setStyleSheet('QLineEdit{background:default}')
            style = self.styleSheet()
            self.parent_text.setStyleSheet(style)
            
            if self.emit_parent:
                self.parent_change.emit(None)
            return
        
        if cmds.objExists(text) and util.is_a_transform(text):
            #self.parent_text.setStyleSheet('QLineEdit{background:default}')
            
            style = self.styleSheet()
            self.parent_text.setStyleSheet(style)
            
            self.set_parent_name(text)
            
            
        
    
    def _value_changed(self):
        max_angle = self.max_angle.value()
        max_distance = self.max_distance.value()
        twist_on = self.twist_on.value()
        twist = self.twist.value()
        
        print twist, '!!!'
        
        self.set_values(max_angle, max_distance, twist_on, twist)
        #self.value_changed.emit(max_angle, max_distance, twist_on, twist)

    def _pose_enable(self, value):
        
        value = value/100.00
        
        self.pose_enable_change.emit(value)

    def _get_pose_values(self):
        
        pose = self.pose
               
        max_angle = cmds.getAttr('%s.maxAngle' % pose)
        max_distance = cmds.getAttr('%s.maxDistance' % pose)
        twist_on = cmds.getAttr('%s.twistOffOn' % pose)
        twist = cmds.getAttr('%s.maxTwist' % pose)
        
        print twist, '!!!'
        
        self.set_values(max_angle, max_distance, twist_on, twist)
        
        return max_angle, max_distance, twist_on, twist

    def _get_parent(self):
        
        pose_inst = util.PoseControl()
        pose_inst.set_pose(self.pose)
        parent = pose_inst.get_parent()
        
        self.set_parent_name(parent)
        
        return parent

    def set_pose(self, pose_name):
        super(PoseConeWidget, self).set_pose(pose_name)
        
        if not pose_name:
            self.pose = None
            return
        
        self.pose = pose_name
        self._get_pose_values()
        self._get_parent()

    def set_values(self, angle, distance, twist_on, twist):
        
        if not self.pose:
            return
        
        self.max_angle.setValue(angle)
        self.max_distance.setValue(distance)
        self.twist_on.setValue(twist_on)
        self.twist.setValue(twist)
        
        
        cmds.setAttr('%s.maxAngle' % self.pose, angle)
        cmds.setAttr('%s.maxDistance' % self.pose, distance)
        cmds.setAttr('%s.maxTwist' % self.pose, twist)
        cmds.setAttr('%s.twistOffOn' % self.pose, twist_on)
        
    def axis_change(self, string):
        
        if not self.pose:
            return
        
        pose_name = str(self.pose)
        
        pose = util.PoseControl()
        pose.set_pose(pose_name)
        pose.set_axis(string)
        
    def set_parent_name(self, parent_name):
        
        self.parent_text.setText(parent_name)
        
        if not self.pose:
            return
        
        pose = util.PoseControl()
        pose.set_pose(self.pose)
        
        pose.set_parent(parent_name)
        
    def set_pose_enable(self, value):
        value = value*100
        self.slider.setValue(value)
    
        