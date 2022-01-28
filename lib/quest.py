from typing import List

class Quest:
    """
    Class to deal with quests data.
    """
    default_language = ""
    """Default quest language."""

    image_name = ""
    """Name of icon file."""

    local_version = []
    """List of string containing data to be saved on local manifest.ini file."""

    name = ""
    """Internal quest name."""

    text = ""
    """String version of original informed data."""

    title = ""
    """Default quest title."""

    url = ""
    """URL from where quest file and its icon may be downloaded. This information exists only in the online version of manifest.ini file."""

    version = ""
    """Quest version."""

    @classmethod
    def read_text(cls, quest_string: List[str]):
        """
        Create a new Quest object from list o characters.

        Parameters
        ----------
        quest_string : List[str]
            List of strings from which data will be extracted. 

        Returns
        -------
        Quest :
            Quest object.
        """
        quest = Quest()
        # Conversion from list of characters do list of lines of text
        quest.text = "".join(quest_string)
        lines = quest.text.split('\n')

        # Title on default language
        default_title = ""

        # Conversion from string to object properties
        for line in lines:
            if line[0]=='#':
                continue
            if line[0]=='[':
                quest.name = line[1:-1]
            else:
                if line.find("version=")==0:
                    quest.version=line[line.find("=")+1:]
                else:
                    if line.find("url=")==0:
                        quest.url=line[line.find("=")+1:]
                    else:
                        if line.find('defaultlanguage=')==0:
                            quest.default_language=line[line.find('=')+1:]
                            default_title="name."+quest.default_language
                        else:
                            if line.find(default_title+"=")==0:
                                quest.title=line[line.find("=")+1:]
                            else:
                                if line.find("image=")==0:
                                    quest.image_name=line[line.find("=")+1:]
        ## Some data are discarded, because they exist only on online version
        local_version = []
        for line in lines:
            if line[0]=="#":
                continue
            if line.find('url=')==0:
                continue
            if line.find('latest_update=')==0:
                continue
            # if line.find('description.')==0:
            #     continue
            # if line.find('authors.')==0:
            #     continue
            local_version.append(line)
            local_version.append('\n')
        quest.local_version = "".join(local_version)
        return quest

    def to_array(self) -> List[str]:
        """
        Converts object in array.

        Returns
        -------
        List[str] :
            Array version of current object. Data sequence is: name (internal name), title (default title), version, default language, url, text, image name.
        """
        return [self.name, self.title, self.version, self.default_language, self.url, self.text, self.image_name]

    def copy(self):
        """
        Make a clone of current object.

        Returns
        -------
        Quest :
            Clone of current object.
        """
        clone = Quest()
        clone.default_language = self.default_language
        clone.image_name = self.image_name
        clone.local_version = self.local_version
        clone.name = self.name
        clone.text = self.text
        clone.title = self.title
        clone.url = self.url
        clone.version = self.version
        return clone

    def get_field_by_name(self, field_name: str) -> str:
        """
        Retrives data of a specific informed property.

        Parameters
        ----------

        filed_name : str
            Property name.

        Returns
        -------
        str :
            Value of desired property.
        """
        if field_name == 'default_language':
            return self.default_language
        elif field_name == 'image_name':
            return self.image_name
        elif field_name == 'name':
            return self.name
        elif field_name == 'text':
            return self.text
        elif field_name == 'title':
            return self.title
        elif field_name == 'url':
            return self.url
        elif field_name == 'version':
            return self.version
        
    def __str__(self) -> str:
        """
        Converts current object data do printable version.
        """
        return f'''[{self.name}]
Title: {self.title}
Default Language: {self.default_language}
Version: {self.version}
URL: {self.url}
Text: {self.text}
'''
        