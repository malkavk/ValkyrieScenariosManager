import requests
from lib.quest import Quest
import requests
from typing import List, Tuple, Dict
from kivy.properties import Clock


GAME_TYPE = { 
    'mom': "https://drive.google.com/uc?id=13JEtzRQ1LcCAAhKluxii0tgKDW71XODV&export=download", 
    'd2e': "https://drive.google.com/uc?id=1oa6NhKLUFn61RH1niPJzpFT4fG9iQFas&export=download"
}
"""
Constant for online URL of online versions of manifest.ini files fo MoM and D2E.
"""

class LoaderHelper:
    """
    Helper to load data from local manifest.ini file and its online version.
    """


    _remote_manifest = ""
    """
    URL for online version of manifest.ini file do be processed.
    """
    
    _local_manifest = ""
    """
    manifest.ini file (with path) to be processed.
    """

    _local_quests = []
    """
    Quests definitions on local manifest.ini file.
    """
    
    _remote_quests = []
    """
    Quests definitions on online version of manifest.ini file.
    """
    
    def __init__(self, game_type: str, manifest_file_location: str):
        """
        Initializes the object.

        Parameters
        ----------
        game_type : str
            One of two options: "mom" (for Mansions of Madness) or "d2e" (for Descent 2).
        manifest_file_location : str
            Path to Valkyrir manifest.ini file.
        """
        self._remote_manifest = GAME_TYPE[game_type]
        self._local_manifest = manifest_file_location

    def _text_to_list(self, text: List[str]) -> List[str]:
        """
        Converts a string of charcters in a list of string, using "\\n\\n" as deliter.

        Parameters
        ----------
        text : str
            String to be splited.

        Returns
        -------
        List[str] : 
            List of strings.
        """
        list = text.split("\n\n") 
        return list[:-1]

    def _load_remote(self) -> None:
        """
        Loads remote version of manifest.ini file.

        All data are loaded on private properties.
        """
        # Download to a array of bytes.
        r = requests.get(self._remote_manifest) 
        file = bytearray()

        # Conversion of arrays of bytes to string.
        for chunck in r.iter_content():
            for c in chunck:
                file.append(c)
        textFile = file.decode()

        # Conversion of string to list of Quest objects.
        self._remote_quests = [Quest.read_text(item) for item in self._text_to_list(textFile)]
        

    def _load_local(self) -> None:
        """
        Loads local version of manifest.ini file.

        All data are loaded on private properties.
        """
        # Conversion of file of characters to string.
        text_file = ""
        with open(self._local_manifest, "r") as file:
            text_file = file.read()

        # Conversion of string to list of Quest objects.
        self._local_quests = [Quest.read_text(item) for item in self._text_to_list(text_file)]

        
    
    def _fix_url(self, fixer: List[Quest], fixable: List[Quest]) -> Tuple[List[Quest],List[Quest]]:
        """
        Fixes absense of url information on local manifest.ini file with its online version.

        Parameters
        ----------
        Tuple[List[Quest],List]
        fixer : list[Quest]
            List of Quest objects, created from online version of manifest.ini file.
        fixable : list[Quest]
            List of Quest objects, created from online version of manifest.ini file. Each Quest.url will be filled with same information on online version.
        
        Returns
        -------
        Tuple[List[Quest],List[Quest]]
            First list of Quest objects is the original 'fixer'. Second one is the 'fixed'.
        """
        for i in range(0,len(fixer)):
            for j in range(0,len(fixable)):
                if fixable[j].name == fixer[i].name:
                    fixable[j].url = fixer[i].url
        return fixer, fixable
        

    def load(self) -> Tuple[List[Quest],List[Quest]]:
        """
        Public function to call load of local and remote versions of manifest.ini file.

        Returns
        -------
        Tuple[List[Quest],List[Quest]] : 
            First list of Quest objects are loaded from online manifest.ini. Second one is loaded from local manifest.ini. 
            Due online version have more data then local version, local version is 'completed' using online version.
        """
        self._load_local()
        self._load_remote()
        return self._fix_url( self._remote_quests, self._local_quests)
        
    def get_dictionary(self, items: List[Quest], field: str) -> Dict[str, Quest]:
        """
        Converts a list of Quest object in a dictionary, using a specified field as key.

        Parameters
        ----------
        items : List[Quest]
            List of Quest to be converted.
        field: str
            Field name to be used as key.

        Returns
        -------
        Dict [str,Quest] :
            Dictionary of quests, having 'field' as key.
        """
        # Creation of keys
        keys = []
        for item in items:
            keys.append(item.get_field_by_name(field))
        keys.sort() # Keys are sorted

        # Dictionary creation
        dictionary = {}
        for key in keys:
            for item in items:
                if item.get_field_by_name(field)==key:
                    dictionary[key] = item
                    
        return dictionary



