import requests
import shutil,os,os.path
import pathlib


class DownloadHelper:
    """
    Helps to download quest file.
    """

    _quest = None
    """Quest object used to locate some data"""

    _destination = ""
    """Where quest file will be saved."""

    def __init__(self, quest, destination):
        """
        Initialization.

        Parameters
        ----------
        quest : Quest
            Quest object that will be downloaded.
        
        destination : str
            Location on computer where quest file will be saved.
        """
        self._quest = quest
        self._destination = destination
    
    def download(self):
        """
        Downloads the quest file.
        """
        # Downloads of quest file and saves it on current directory
        request = requests.get(self._quest.url+self._quest.name+'.valkyrie')
        file = bytearray()

        current_directory = pathlib.Path().resolve()

        with open(self._quest.name+".valkyrie", "wb") as file:
            for chunck in request.iter_content():
                file.write(chunck)

        # Moves quest file on current directory to its final destination        
        origin = os.path.join(current_directory, self._quest.name+".valkyrie")
        ## If destination file exists it is delete
        destination = os.path.join(self._destination, self._quest.name+".valkyrie")
        if os.path.exists(destination):
            os.remove(destination)
        shutil.move(origin,self._destination)