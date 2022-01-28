from lib.loader import LoaderHelper
from lib.manifest import ManifestHelper
from lib.downloader import DownloadHelper
from lib.quest import Quest

from typing import List




import os

def _load_data(self, local_manifest:str) -> None:
    """
    Load from local manifest.ini file and its on line version.

    After data is loaded and downloaded, all visual elements are filed as lists of toggle buttons. 

    This data s distributed on 3 categories:
        1. Quests to download
        2. Quests do update
        3. Quests to delete

    Parameters
    ----------
    local_manifest : str
        String with manifest.ini file with path.
    """
    
    # Clear data
    self.delete_checked = 0
    self.delete_total = 0
    self.new_checked = 0
    self.new_total = 0
    self.update_total = 0
    self.update_checked = 0
    
    self._removable_quests = {}
    self._updatable_quests = {} 
    self._new_quests = {} 

    self.max_execution_point = 5

    try:
        # Load manifest.ini local and online version
        self.current_execution_point = 1
        helper = LoaderHelper(self._game_type, local_manifest)
        remote_quests, local_quests = helper.load()

        # Dictionaries using name field for local and remote content
        self.current_execution_point = 2
        local_by_name = helper.get_dictionary(local_quests, 'name')
        remote_by_name = helper.get_dictionary(remote_quests, 'name')

        # Data categorization and interface filling
        self._local_quests = helper.get_dictionary(local_quests, 'title')
        self._remote_quests = helper.get_dictionary(remote_quests, 'title')
        ## Removable quests
        self.current_execution_point = 3
        ### Dictionary creation
        self._removable_quests = helper.get_dictionary(local_quests, 'title')
        ### Data counting
        self.delete_total = len(self._removable_quests.keys())
        ### Interface filling
        self._populate_delete_interface(self._removable_quests, self.ids['DELETE_CONTAINER'])

        ## New quests
        self.current_execution_point = 4
        ### Dictionary creation
        new_quests = []
        self._new_quests = {}
        for new_quest in remote_by_name.keys():
            if not new_quest in local_by_name.keys():
                new_quests.append(remote_by_name[new_quest])
        self._new_quests = helper.get_dictionary(new_quests, 'title')
        ### Data counting
        self.new_total = len(self._new_quests.keys())
        ### Interface filling
        self._populate_new_interface(self._new_quests, self.ids['NEW_CONTAINER'])

        ## Updatable quests
        self.current_execution_point = 5
        ### Dictionary creation
        self._updatable_quests = {}
        updatable_quests = []
        for local_name in local_by_name.keys():
            if (local_name in remote_by_name.keys()) and (local_by_name[local_name].version != remote_by_name[local_name].version):
                updatable_quests.append(remote_by_name[local_name])
        self._updatable_quests = helper.get_dictionary(updatable_quests, 'title')
        ### Data counting
        self.update_total = len(self._updatable_quests.keys())
        ### Interface filling
        self._populate_update_interface(self._updatable_quests, self.ids['UPDATE_CONTAINER'])

    except Exception as e:
        print(e)
        print(e.args)
        print(e.with_traceback)

def _load_ini(self) -> None:
    """
    Loads or create scenariosmanager.ini.
    """
        # Validation if scenariosmanager.ini file exists
    if not os.path.isfile(self.INI_FILE):
        # Missing configuration file
        with open(self.INI_FILE, 'w') as ini_conf:
            ini_conf.write(self.INITIAL_INI_FILE)

    # Load scenariosmanager.ini
    try:
        with open(self.INI_FILE, "r") as ini_conf:
            lines = ini_conf.readlines()
            for line in lines:
                if line.find("valkyrie_config_directory=")==0:
                    self._valkyrie_content_path = line[line.find("=")+1:-1]
            if self._valkyrie_content_pathh=='':
                print("Invalid configuration file.")
    except:
        print("Invalid configuration file.")



def _download_new(self, quest: Quest, destination: str, quests_list: List[Quest], manifest_file: str,) -> None:
    """
    Downloads a new quest and update manifest.ini file.

    Parameters
    ----------

    quest : Quest
        Current quest to download.
    
    destination : str
        Destiantion of downloaded files.

    quests_list : List[Quest]
        List with quest to save to manifest.ini file

    manifest_file : str
        manifest.ini file location.

    """
    downloader = DownloadHelper(quest, destination)
    downloader.download()
    manifest = ManifestHelper(quests_list, manifest_file )
    manifest.export()

def _remove(self, quest: Quest, origin: str, quests_list: List[Quest], manifest_file: str) -> None:
    """
    Remove a quest file and rewrites manifest.ini file.

    Parameters
    ----------

    quest : Quest
        Current quest to download.
    
    origin : str
        Destiantion of downloaded files.

    quests_list : List[Quest]
        List with quest to save to manifest.ini file

    manifest_file : str
        manifest.ini file location.
    """
    file_name = os.path.join(origin, quest.name+'.valkyrie')
    if os.path.exists(file_name):
        os.remove(file_name)
    manifest = ManifestHelper(quests_list, manifest_file )
    manifest.export()