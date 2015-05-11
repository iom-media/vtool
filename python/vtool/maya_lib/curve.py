# Copyright (C) 2014 Louis Vottero louis.vot@gmail.com    All rights reserved.

import os

import util
import vtool.util_file
import vtool.util


import maya.cmds as cmds
import maya.mel as mel


current_path = os.path.split(__file__)[0]

class CurveToData(object):
    
    def __init__(self, curve):
        
        curve_shapes = self._get_shapes(curve)
        
        self.curves = []
        self.curve_mobjects = []
        self.curve_functions = []
        
        for curve_shape in curve_shapes:
            
            if not curve_shape:
                vtool.util.warning('%s is not a nurbs curve.' % curve_shape)
                continue 
            
            self.curves.append(curve_shape)
            self.curve_mobjects.append( util.nodename_to_mobject(curve_shape) )
            self.curve_functions.append( util.NurbsCurveFunction( self.curve_mobjects[-1] ))
        
    def _get_shapes(self, curve):
        
        curves = vtool.util.convert_to_sequence(curve)
        
        curve_shapes = []
        
        for curve in curves:
                
            if not cmds.nodeType(curve) == 'nurbsCurve':
                shapes = cmds.listRelatives(curve, s = True)
                
                if shapes:
                    
                    for shape in shapes:
                        if cmds.nodeType(shape) == 'nurbsCurve':
                            curve_shapes.append( shape )
        
        return curve_shapes
    
    def get_degree(self, index = 0):
        return self.curve_functions[index].get_degree()
        
    def get_knots(self, index = 0):
        return self.curve_functions[index].get_knot_values()
        
    def get_cvs(self, index = 0):
        cvs = self.curve_functions[index].get_cv_positions()
        
        returnValue = []
        
        for cv in cvs:
            returnValue.append(cv[0])
            returnValue.append(cv[1])
            returnValue.append(cv[2])
            
        return returnValue
    
    def get_cv_count(self, index = 0):
        return self.curve_functions[index].get_cv_count()
    
    def get_span_count(self, index = 0):
        return self.curve_functions[index].get_span_count()
    
    def get_form(self, index = 0):
        return (self.curve_functions[index].get_form()-1)
    
    def create_curve_list(self):
        
        curve_arrays = []
        
        for inc in range(0, len(self.curves)):
            nurbs_curve_array = []
            
            knots = self.get_knots(inc)
            cvs = self.get_cvs(inc)
            
            nurbs_curve_array.append(self.get_degree(inc))
            nurbs_curve_array.append(self.get_span_count(inc))
            nurbs_curve_array.append(self.get_form(inc))
            nurbs_curve_array.append(0)
            nurbs_curve_array.append(3)
            nurbs_curve_array.append(len(knots))
            nurbs_curve_array += knots
            nurbs_curve_array.append(self.get_cv_count(inc))
            nurbs_curve_array += cvs
            
            curve_arrays.append( nurbs_curve_array )
        
        return curve_arrays
    
    def create_mel_list(self):
        curve_arrays = self.create_curve_list()
        
        mel_curve_data_list = []
        for curve_array in curve_arrays:
            mel_curve_data = ''
            
            for nurbs_data in curve_array:
                mel_curve_data += ' %s' % str(nurbs_data)
                
            mel_curve_data_list.append(mel_curve_data)
            
        return mel_curve_data_list

def set_nurbs_data(curve, curve_data_array):
    #errors at position 7
    cmds.setAttr('%s.cc' % curve, *curve_data_array, type = 'nurbsCurve')
    
def set_nurbs_data_mel(curve, mel_curve_data):
    
    shapes = util.get_shapes(curve)
    
    vtool.util.convert_to_sequence(mel_curve_data)
    
    for inc in range(0, len(shapes)):
        
        if inc < len(mel_curve_data):
            mel.eval('setAttr "%s.cc" -type "nurbsCurve" %s' % (shapes[inc], mel_curve_data[inc]))
        if inc > len(mel_curve_data):
            break
    
        
    
class CurveDataInfo():
    
    curve_data_path = vtool.util_file.join_path(current_path, 'curve_data')
        
    def __init__(self):
        
        self.libraries = {}
        self._load_libraries()
        
        self.library_curves = {}
        self._initialize_library_curve()
        
        self.active_library = None
        
        
    def _load_libraries(self):
        files = os.listdir(self.curve_data_path)
        
        for file in files:
            if file.endswith('.data'):
                split_file = file.split('.')
                
                self.libraries[split_file[0]] = file
                
    def _initialize_library_curve(self):
        names = self.get_library_names()
        for name in names:
            self.library_curves[name] = {}       
    
    def _get_curve_data(self, curve_name, curve_library):
        
        curve_dict = self.library_curves[curve_library]
        
        if not curve_dict.has_key(curve_name):
            vtool.util.warning('%s is not in the curve library %s.' % (curve_name, curve_library))
            
            return None, None
        
        return curve_dict[curve_name]
    
    def _get_curve_parent(self, curve):
        
        parent = None
        
        if cmds.nodeType(curve) == 'nurbsCurve':
            parent = cmds.listRelatives(curve, parent = True)[0]
        if not cmds.nodeType(curve) == 'nurbsCurve':
            parent = curve
            
        return parent
    
    def _get_mel_data_list(self, curve):
        curveData = CurveToData(curve)
        mel_data_list = curveData.create_mel_list()
        
        return mel_data_list
    
    def set_directory(self, directorypath):
        self.curve_data_path = directorypath
        self.libraries = {}
        self._load_libraries()
        self.library_curves = {}
        self._initialize_library_curve()
    
    def set_active_library(self, library_name):
        
        vtool.util_file.create_file('%s.data' % library_name, self.curve_data_path)
        self.active_library = library_name
        self.library_curves[library_name] = {}
        self.load_data_file()
     
    def load_data_file(self, path = None):
        
        if not self.active_library:
            vtool.util.warning('Must set active library before running this function.')
            return
        
        if not path:
            path = vtool.util_file.join_path(self.curve_data_path, '%s.data' % self.active_library)
        
        last_line_curve = False
        curve_name = ''
        curve_data = ''
        curve_type = ''
        
        readfile = vtool.util_file.ReadFile(path)
        data_lines = readfile.read()
        
        curve_data_lines = []
        
        for line in data_lines:
            
            if line.startswith('->'):
                
                if curve_data_lines:
                    
                    self.library_curves[self.active_library][curve_name] = [curve_data_lines, curve_type]
                    
                line_split = line.split()
                curve_name = line_split[1]
                
                if len(line_split) > 3:
                    
                    if curve_type != curve_name:
                        curve_type = line_split[2]
                        
                    if not curve_type:
                        curve_type = ''
                        
                curve_name = curve_name.strip()
                last_line_curve = True
                curve_data_lines = []
                                
            if not line.startswith('->') and last_line_curve:
                
                line = line.strip()
                if line:
                    curve_data = line
                    curve_data = curve_data.strip()
                    curve_data_lines.append(curve_data) 
                    
        if curve_data_lines:

            self.library_curves[self.active_library][curve_name] = [curve_data_lines, curve_type] 
                
    def write_data_to_file(self):
        if not self.active_library:
            vtool.util.warning('Must set active library before running this function.')
            return
        
        path = vtool.util_file.join_path(self.curve_data_path, '%s.data' % self.active_library)
        
        writefile = vtool.util_file.WriteFile(path)
        
        current_library = self.library_curves[self.active_library]
        
        lines = []
        
        for curve in current_library:
            
            curve_data_lines, curve_type = current_library[curve]
            
            if not curve_type:
                if cmds.objExists('%s.curveType' % curve):
                    curve_type = cmds.getAttr('%s.curveType' % curve)
            
            if curve != curve_type:
                lines.append('-> %s %s' % (curve, curve_type))
            if curve == curve_type:
                lines.append('-> %s' % curve)
            
            for curve_data in curve_data_lines:
                lines.append('%s' % curve_data)
          
        writefile.write(lines)
        
        return path
        
    def get_library_names(self):
        return self.libraries.keys()
    
    def get_curve_names(self):
        if not self.active_library:
            vtool.util.warning('Must set active library before running this function.')
            return
        
        return self.library_curves[self.active_library].keys()
        
    def set_shape_to_curve(self, curve, curve_in_library, check_curve = False):
        if not self.active_library:
            vtool.util.warning('Must set active library before running this function.')
            return
        
        mel_data_list, original_curve_type = self._get_curve_data(curve_in_library, self.active_library)

        if not mel_data_list:
            return
        
        
        curve_data = CurveToData(curve)
        original_mel_list =  curve_data.create_mel_list()
        
        curve_type_value = None
        
        curve_attr = '%s.curveType' % curve
        print curve_attr
        
        if cmds.objExists(curve_attr):
            curve_type_value = cmds.getAttr('%s.curveType' % curve)
        
        check_curve = False
        if check_curve:
            
            if curve_type_value == None or curve_type_value != original_curve_type:
            
                mel_count = len(mel_data_list)
                original_count = len(original_mel_list)
                
                if mel_count != original_count:
                    vtool.util.warning('Curve data does not match stored data. Skipping %s' % curve)
                    return
                
                for inc in range(0, mel_count):
                    
                    split_mel_data = mel_data_list[inc].strip()
                    split_orig_data = original_mel_list[inc].strip()
                    
                    split_mel_data = split_mel_data.split()
                    split_orig_data = split_orig_data.split()
                    
                    if len(split_mel_data) != len(split_orig_data):
                    
                        vtool.util.warning('Curve data does not match stored data. Skipping %s' % curve)
                        return
                    

        
        data_list_count = len(mel_data_list)
        
        shapes = util.get_shapes(curve)
        
        if not shapes:
            return
        
        shapes_count = len(shapes)
        
        if shapes_count != data_list_count:
            if check_curve:
                return
            if not check_curve and shapes_count > 1:
                cmds.delete(shapes[1:])
        
        if len(shapes) < mel_data_list:
            
            current_index = len(shapes)
            
            for inc in range(current_index, len(mel_data_list)):
                
                curve_shape = cmds.createNode('nurbsCurve')
        
                parent = cmds.listRelatives(curve_shape, parent = True)[0]
                
                cmds.parent(curve_shape, curve, r = True, s = True)
                
                cmds.delete(parent)
     
        if mel_data_list:
            
            set_nurbs_data_mel(curve, mel_data_list)
            
        util.rename_shapes(curve)
        
        if curve_type_value:
            attribute_value = curve_type_value
        
            curve_type = util.MayaStringVariable('curveType')
            curve_type.set_node(curve)
            curve_type.set_value(curve_type_value)
            curve_type.create()
        
    def add_curve(self, curve, library_name = None):
        
        if not curve:
            
            return
        
        if not library_name:
            
            library_name = self.active_library
            
            if not self.active_library:
                vtool.util.warning('Must set active library before running this function.')
                return
        
        mel_data_list = self._get_mel_data_list(curve)
        
        curve_type = curve
        
        if cmds.objExists('%s.curveType' % curve):  
            curve_type = cmds.getAttr('%s.curveType' % curve)
            
        transform = self._get_curve_parent(curve)
               
        if library_name:
            self.library_curves[library_name][transform] = [mel_data_list, curve_type]
        
    def create_curve(self, curve_name):
        if not self.active_library:
            vtool.util.warning('Must set active library before running this function.')
            return
        
        curve_shape = cmds.createNode('nurbsCurve')
        
        parent = cmds.listRelatives(curve_shape, parent = True)[0]
        parent = cmds.rename( parent, curve_name )
        
        self.set_shape_to_curve(parent, curve_name)

        return parent
        
    def create_curves(self):
        if not self.active_library:
            vtool.util.warning('Must set active library before running this function.')
            return
        
        curves_dict = self.library_curves[self.active_library]
        
        for curve in curves_dict:
            self.create_curve(curve)    