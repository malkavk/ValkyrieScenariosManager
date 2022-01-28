from typing import List
from lib.quest import Quest
class ManifestHelper:
    """
    Class to export list of quest to manifest.ini file.
    """

    data = []
    """List of quests."""

    file_name = ""
    """Complet path and name where manifest.ini will be saved."""

    def __init__(self,quests_data: List[Quest], manifest_file: str):
        """
        Initializes the object.

        Parameters
        ----------

        quest_data : List[Quest]
            List of quests to save.

        manifes_file : str
            </path/to/>/manifest.ini
        """
        self.data = quests_data
        self.file_name = manifest_file
    
    def export(self) -> None:
        """
        Exports list of quests to manifest.ini file.
        """
        # Write into manifest.ini
        with open(self.file_name, 'w') as file:
            ## Loop over all quests
            for quest in self.data.keys():
                file.write(self.data[quest].local_version)
                file.write('\n')