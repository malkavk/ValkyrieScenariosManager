from kivy.config import Config
Config.set("graphics", "height", "600")

import asyncio

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.properties import Clock
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics.vertex_instructions import Line, Rectangle
from kivy.graphics.context_instructions import Color

import os


class ScenarioManager(Widget):
    """
    Main widget to deal with interface logics.
    """

    from lib.interface import _populate_delete_interface, _populate_new_interface, _populate_update_interface, _populate_interface, _create_togglebutton, _toggle_image
    from lib.load_data import _load_data, _load_ini, _download_new, _remove

    MANIFEST_FILE = "manifest.ini" 
    """Local file name containing downloaded quests descriptions."""
    DEFAULT_IMAGE = "resources/defaultLogo.png"
    """Default icon for quests."""
    INI_FILE = './scenariosmanager.ini' 
    """Configuration file for Scenarios Manager."""

    INITIAL_INI_FILE = ''''#
# valkyrie_config_directory must be OS path to where Valkyrie stores its downloaded content (MoM and D2N quests)
# For example: on Linux this path is ~/.config/Valkyrie/ 
# "~" is user home directory.
[Scenarios Manager]
valkyrie_config_directory=~/.config/Valkyrie/
'''
    """"Constant with content of initial scenariosmanager.ini file."""
    _executing = False
    """Flag for execution."""
    _updating_data = False
    """Flag if right now is occuring a data manipulation."""

    _valkyrie_content_path = "" 
    """Path to Valkyrie's directory where everything is downloaded."""

    _destination_path = ""
    """Default path used as source and destination. This is the path do manifest.ini file and destination of .valkyrie files"""

    _manifest_file = ""
    """"File name with para to local manifest.ini file."""

    _game_type = ""
    """Game type (mom or d2e)."""

    _removable_quests = {}
    """Quests to delete."""
    _updatable_quests = {} 
    """Quests do update."""
    _new_quests = {} 
    """New quests to download."""
    _local_quest = {}
    """Quests loaded from local manifest.ini file."""
    _remote_quests = {}
    """Quests loaded from remote manifest.ini file."""

    delete_checked = NumericProperty(0)
    """Quests to delete counter."""
    update_checked = NumericProperty(0)
    """Quests to update counter."""
    new_checked = NumericProperty(0)
    """Quests to download counter."""

    delete_total = NumericProperty(0) 
    """Total of quests to delete"""
    update_total = NumericProperty(0) 
    """Total of quests to update"""
    new_total = NumericProperty(0) 
    """Total of new quests"""

    current_execution_point = NumericProperty(0)
    """Current position on execution progress bar"""
    max_execution_point = NumericProperty(0)
    """Max position on execution progress bar"""

    def __init__(self, **kwargs):
        """
        Initializes main objects.
        """
        super().__init__(**kwargs)
        self._load_ini()

    def on_quest_release(self, widget: Widget, value: str) -> None:
        """
        Validates game selection and calls data loading.

        Parameters
        ----------

        widget : Widget
            Cliecked button.
        
        value : str
            Game selected (mom or d2e)
        """
        # Get game type
        self._game_type = value

        # Destination path definition
        self._destination_path = os.path.join(self._valkyrie_content_path, 'Download/')
        if self._destination_path[0]=="~":
            self._destination_path = os.path.expanduser("~")+ self._destination_path[1:-1]

        # manifest.ini file definition
        self._manifest_file = os.path.join(self._destination_path, self.MANIFEST_FILE)

        # Move to second page
        self.ids['MAIN_PAGER'].page = 1
        # Load data and show initial UI

        def show_wait_execute(dt):
            """
            Sub function only for scheduled execution. This takes time to interface redraw
            """
            # Load data
            self._load_data( self._manifest_file )
            
            # Set UI to initial state
            self._clear_pager_state()

        Clock.schedule_once(show_wait_execute, .2)

    def on_toolbar_press(self, index: int) -> None:
        """
        Switch to a different content page, according with indicate index.

        Each of buttons on bottom of window will change to a different content page, passing a different index as parameter.

        Parameters
        ----------

        index : int
            Index of desired page
        """
        self.ids['CONTENT_PAGER'].page = index

    def on_toggle_delete(self, widget: Widget) -> None:
        """
        Deals with state of ToggleButton, selecting or unselecting a quest for deletion.

        Parameters
        ----------

        widget : Widget
            ToggleButton that triggered the event.
        """

        # Nothing must be done if quests are under operation
        if self._executing:
            return

        # Validation of button state and update of deletion selection
        if widget.state == 'down':
            self.delete_checked +=1
        else:
            self.delete_checked -=1

        # Update of button on upper right corner of the list
        self._toggle_image(self.ids['DELETE_CHECK'], self.delete_checked, self.delete_total)

    def on_toggle_new(self, widget: Widget) -> None:
        """
        Deals with state of ToggleButton, selecting or unselecting a new quest for download.

        Parameters
        ----------

        widget : Widget
            ToggleButton that triggered the event.
        """

        # Nothing must be done if quests are under operation
        if self._executing:
            return

        # Validation of button state and update of new downloads selection
        if widget.state == 'down':
            self.new_checked +=1
        else:
            self.new_checked -=1

        # Update of button on upper right corner of the list
        self._toggle_image(self.ids['NEW_CHECK'], self.new_checked, self.new_total)

    def on_toggle_update(self, widget: Widget) -> None:
        """
        Deals with state of ToggleButton, selecting or unselecting a quest for update.

        Parameters
        ----------

        widget : Widget
            ToggleButton that triggered the event.
        """

        # Nothing must be done if quests are under operation
        if self._executing:
            return

        # Validation of button state and update of updates selection
        if widget.state == 'down':
            self.update_checked +=1
        else:
            self.update_checked -=1

        # Update of button on upper right corner of the list
        self._toggle_image(self.ids['UPDATE_CHECK'], self.update_checked, self.update_total)

    def on_delete_check_pressed(self, widget: Widget) -> None:
        """
        Check or uncheck all ToggleButton concerned with quests to delete.

        Parameters
        ----------

        widget: Widget
            Corner button clicked.
        """
        # Nothing must be done if quests are under operation
        if self._executing:
            return

        # State validation
        if self.delete_checked == 0:
            ## Check all items
            self._change_states(self.ids['DELETE_CONTAINER'], 'down')
            self.delete_checked = self.delete_total
            widget.source = "resources/check.png"
        else:
            ## Uncheck all items
            self._change_states(self.ids['DELETE_CONTAINER'], 'normal')
            self.delete_checked = 0
            widget.source = "resources/none.png"

    def on_new_check_pressed(self, widget: Widget) -> None:
        """
        Check or uncheck all ToggleButton concerned with new quests to download.

        Parameters
        ----------

        widget: Widget
            Corner button clicked.
        """
        # Nothing must be done if quests are under operation
        if self._executing:
            return

        # State validation     
        if self.new_checked == 0:
            ## Check all items
            self._change_states(self.ids['NEW_CONTAINER'], 'down')
            self.new_checked = self.new_total
            widget.source = "resources/check.png"
        else:
            ## Uncheck all items
            self._change_states(self.ids['NEW_CONTAINER'], 'normal')
            self.new_checked = 0
            widget.source = "resources/none.png"

    def on_update_check_pressed(self, widget: Widget) -> None:
        """
        Check or uncheck all ToggleButton concerned with quests to update.

        Parameters
        ----------

        widget: Widget
            Corner button clicked.
        """
        # Nothing must be done if quests are under operation
        if self._executing:
            return

        # State validation
        if self.update_checked == 0:
            ## Check all items
            self._change_states(self.ids['UPDATE_CONTAINER'], 'down')
            self.update_checked = self.update_total
            widget.source = "resources/check.png"
        else:
            ## Uncheck all items
            self._change_states(self.ids['UPDATE_CONTAINER'], 'normal')
            self.update_checked = 0
            widget.source = "resources/none.png"

    def _change_states(self, container: Widget, state: str) -> None:
        """
        Change state of each ToggleButton into a Widget.

        Parameters
        ----------

        container : Widget
            Widget that contains ToggleButtons to change state.

        state : str
            New state.
        """
        # Loop over all items into container
        for item in container.children:
            # ToggleButton is one of children into a item, into the container
            item.children[0].state = state
    
    def on_execute_release(self) -> None:
        """
        Execute all modifications marked.
        """
        # Nothing must be done if quests are under operation
        if self._executing:
            return

        # Clear execution point
        self.current_execution_point = 0

        # Max operations definition
        self.max_execution_point = self.new_checked + self.update_checked + self.delete_checked


        Clock.schedule_interval(self.update_data, 0.5)
            
    
    def update_data(self, dt: float) -> None:
        """
        Execute all operations defined by items selection on interface.

        Parameters
        ----------

        dt : float
            Elapsed time
        """
        if self._updating_data:
            return
        # Prevents that other updating data operation be executed
        self._updating_data = True
        # Change flag to prevent others UI elements to change current states
        self._executing = True
        
        # Title of current quest
        title = ""
        try:
            updatable_quests = {}
            ## Increment current execution point
            self.current_execution_point += 1
            if self.current_execution_point <= self.max_execution_point:
                print("Executing operation... ("+str(self.current_execution_point)+"/"+str(self.max_execution_point)+")")
            if self.current_execution_point <= self.new_checked:
                # Download new quests
                ## List of items selection
                container = self.ids['NEW_CONTAINER']
                ## ToggleButton identifier
                button = None
                ## ToggleButon identification
                item = -1
                while not button:
                    item +=1
                    if container.children[item].children[0].state == 'down':
                        button = container.children[item].children[0]
                title = button.text
                ## Add selected quest to local list of quest
                self._local_quests[title] = self._new_quests[title]
                ## Download of quest and manifest.ini update
                self._download_new(self._local_quests[title], self._destination_path, self._local_quests, self._manifest_file)    
                ## Unselect quest
                button.state = 'normal'
            elif self.current_execution_point <= self.new_checked + self.update_checked:
                # Update existing quests
                ## List of items selection
                container = self.ids['UPDATE_CONTAINER']
                ## ToggleButton identifier
                button = None
                ## ToggleButon identification
                item = -1
                while not button:
                    item +=1
                    if container.children[item].children[0].state == 'down':
                        button = container.children[item].children[0]
                ## Identification of selected quest
                title = button.text
                ## Identification of updatable quests
                updatable_quests[title] = self._local_quest[title]
                ## Download of quest and manifest.ini update
                self._download_new(self._local_quests[title], self._destination_path, self._local_quests, self._manifest_file)
                ## Unselect quest
                button.state = 'normal'
            elif self.current_execution_point <= self.max_execution_point:
                # Delete existing quests
                ## List of items selection
                container = self.ids['DELETE_CONTAINER']
                ## ToggleButton identifier
                button = None
                ## ToggleButon identification
                item = -1
                while not button:
                    item +=1
                    if container.children[item].children[0].state == 'down':
                        button = container.children[item].children[0]
                ## Quest identification
                title = button.text
                ## Quests must be delete only if they weren´t updated
                if not title in updatable_quests.keys():
                    ## Quest copy
                    quest = self._local_quests[title].copy()
                    ## Removal of quest from local quests list
                    del self._local_quests[title]
                    ## Quest file removal and manifest.ini update
                    self._remove(quest, self._destination_path, self._local_quests, self._manifest_file)
                ## Unselect quest
                button.state = 'normal'
            else:
                # Finishing execution
                Clock.unschedule(self.update_data)
                self.ids['MAIN_PAGER'].page=1

                def show_wait_execute(dt):
                    """
                    Sub function only for scheduled execution. This takes time to interface redraw
                    """
                    # Load data
                    self._load_data( self._manifest_file )
                    
                    # Set UI to initial state
                    self._clear_pager_state()

                Clock.schedule_once(show_wait_execute, .2)
                self._executing = False
        except Exception as e:
            print("Current quest: {title}")
            print(e)
            print(e.with_traceback)
            print(e.args)
        finally:
            # Releases to next operation be done
            self._updating_data = False

    def _clear_pager_state(self) -> None:
        """
        Redefines UI elements to initial state.
        """
        self.ids['MAIN_PAGER'].page=2
        self.on_toolbar_press(0)
        self.ids['NEW_PAGER_BUTTON'].state='down'
        self.ids['UPDATE_PAGER_BUTTON'].state='normal'
        self.ids['DELETE_PAGER_BUTTON'].state='normal'
        self.ids['EXECUTE_PAGER_BUTTON'].state='normal'
        self.ids['NEW_CHECK'].source="resources/none.png"
        self.ids['UPDATE_CHECK'].source="resources/none.png"
        self.ids['DELETE_CHECK'].source="resources/none.png"
        
class CustomButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)

class ScenarioManagerApp(App):
    title = ".valkyrie Manager "

if __name__=="__main__":
    ScenarioManagerApp().run()