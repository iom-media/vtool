# Copyright (C) 2016 Louis Vottero louis.vot@gmail.com    All rights reserved.

from vtool import qt_ui, qt
from vtool import util
from vtool.process_manager import process
from vtool import util_file

from vtool import logger
log = logger.get_logger(__name__)

class ProcessSettings(qt_ui.BasicWidget):
    
    def __init__(self):
        
        self.directory = None
        
        super(ProcessSettings, self).__init__()
        
        self.setContentsMargins(1,1,1,1)
        
    def set_directory(self, directory):
        
        log.debug('Set process setting widget directory %s' % self.directory)
        
        self.directory = directory
        self.name_widget.set_directory(self.directory)
        self.management_widget.set_directory(self.directory)
    
    def set_active(self, bool_value):
        
        self.name_widget.set_active(bool_value)
    
    def _build_widgets(self):
        
        self.management_widget = ManagementWidget()
        
        self.name_widget = qt_ui.DefineControlNameWidget(self.directory)
        
        self.management_widget.collapse_group()
        self.name_widget.collapse_group()
        
        self.main_layout.addWidget(self.management_widget)
        self.main_layout.addWidget(self.name_widget)
        
        self.main_layout.setAlignment(qt.QtCore.Qt.AlignTop)
        
        
class ManagementWidget(qt_ui.Group):
    
    def __init__(self, name = 'Management'):
        super(ManagementWidget, self).__init__(name)
        
        self.directory = None
        
        
    def _build_widgets(self):
        
        
        #backup = qt.QPushButton('Backup This Process')
        prune_version = qt.QPushButton('Prune Old Versions')
        
        #backup.clicked.connect(self._backup_process)
        prune_version.clicked.connect(self._prune_versions)
        
        self.backup_history = BackupProcessFileWidget()
        
        #self.main_layout.addWidget(backup)
        self.main_layout.addWidget(prune_version)
        
        self.backup_dir = qt.QLabel('Backup Directory:')
        
        self.main_layout.addWidget(self.backup_dir)
        self.main_layout.addWidget(self.backup_history)
        


    def _prune_versions(self):
        
        print 'prune!'
    
    def set_directory(self, directory):
        
        if not directory:
            return
        
        self.directory = directory
        backup = self.backup_history.set_directory(directory)
        
        self.backup_dir.setText('Backup Directory: %s' % backup)
        
        
class BackupProcessFileWidget(qt_ui.BackupWidget):
    def _define_save_widget(self):
        return BackupProcessWidget()
    
    def _define_history_widget(self):
        return BackupProcessHistoryWidget()
    
    def set_directory(self, directory):
        super(BackupProcessFileWidget, self).set_directory(directory)
        
        if not directory:
            return
        
        log.debug('Backup history widget process path: %s' % directory)
        
        process_inst = process.Process()
        process_inst.set_directory(directory)
        
        backup_directory = process_inst.get_backup_path()
        
        log.debug('Backup history widget path: %s' % backup_directory)
        
        self.set_history_directory(backup_directory)
        
        if backup_directory == ( directory + '/.backup' ):
            backup_directory = 'local'
        
        return backup_directory
        
class BackupProcessWidget(qt_ui.DirectoryWidget):    
    
    file_changed = qt.create_signal()
    
    def _build_widgets(self):
        
        self.save_button = qt.QPushButton('Backup Process')
        
        self.save_button.setMaximumWidth(125)
        self.save_button.setMinimumWidth(qt_ui._save_button_minimum)
        
        self.save_button.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Fixed)
        
        self.save_button.clicked.connect(self._save)
        
        self.main_layout.addWidget(self.save_button)
        
        self.main_layout.setAlignment(qt.QtCore.Qt.AlignTop)
        
    def _save(self):
        
        process.backup_process(self.directory)
        self.file_changed.emit()
        
class BackupProcessHistoryWidget(qt_ui.HistoryFileWidget):
    
    def _build_widgets(self):
        super(BackupProcessHistoryWidget, self)._build_widgets()
        
        self.open_button.hide()
        
        
        
        
    