from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image, AsyncImage
from kivy.uix.widget import Widget
from kivy.metrics import dp

from typing import Callable, Dict

from lib.quest import Quest

import urllib

def _create_togglebutton(self, text: str, url: str, image: str, event: Callable[[Widget], None]) -> GridLayout:
    """
    Create an item the displays an image and a toogle button. This toggle button will deal with selection of quest.
    
    This item is composed by: a GridLayout; an Image or an AsyncImage (depending on if is defined image porperty in quest object); a ToggleButton with quest title.

    Parameters
    ----------

    text : str
        Quest title.

    url : str
        URL used to download online image to be displayed.

    image : str
        Name of online icon file.

    event : Callable[[Widget], None]->None
        Function to bind to TobbleButton on_release.
    
    Returns
    -------

    Gridlayout :
        Griglayout containing an Image or Asyncimage and a ToggleButton.

    """
    # Creation of the item
    layout = GridLayout(cols=2, size_hint_y=None, height=dp(50))
    ## Creation of ToggleButton and bind to on_release.
    item = ToggleButton( text=text, size_hint=(1, None), height=dp(50))
    item.bind(on_release=event)
    ## Icon creation
    image_widget = None
    if image!="":
        image_widget = AsyncImage(source=url+urllib.parse.quote(image), size=(dp(48),dp(48)), size_hint=(None,1))
    else:
        image_widget = Image(source=self.DEFAULT_IMAGE, size=(dp(48),dp(48)), size_hint=(None,1))
    ## Add widgets to item
    layout.add_widget(image_widget)
    layout.add_widget(item)

    return layout

def _populate_interface(self, data: Dict[str, Quest], interface: Widget, event: Callable[[Widget], None]) -> None:
    """
    Fills a widget with 0 or more items (Grilayout with an Image or AsyncImage and a ToggleButton).

    Parameters
    ----------

    data : Dict[str,Quest]
        Dictionary having quests title and Quest object.
    
    interface : Widget
        Widget to be populated with items.

    event : Callable[[Widget], None]
        Function to bind to TobbleButton on_release.
    """
    # Widget must be cleared before be filled
    interface.clear_widgets()

    # Items will be created in title sorted order
    quests_keys = list(data.keys())
    quests_keys.sort()
    for quest_key in quests_keys:
        url = data[quest_key].url
        image_name = data[quest_key].image_name
        ## Item creation
        item = self._create_togglebutton(quest_key, url, image_name, event)
        ## Add item to widget
        interface.add_widget(item)

def _populate_delete_interface(self, data: Dict[str,Quest], interface: Widget) -> None:
    """
    Fills a widget with 0 or more items (Grilayout with an Image or AsyncImage and a ToggleButton).

    Nem items acts over quests to be deleted.

    Parameters
    ----------
    data : Dict[str,Quest]
        Dictionary having quests title and Quest object.
    
    interface : Widget
        Widget to be populated with items.
    """
    self._populate_interface(data, interface, self.on_toggle_delete)

def _populate_new_interface(self, data: Dict[str,Quest], interface: Widget) -> None:
    """
    Fills a widget with 0 or more items (Grilayout with an Image or AsyncImage and a ToggleButton).

    Nem items acts over new quests to be downloaded.

    Parameters
    ----------
    data : Dict[str,Quest]
        Dictionary having quests title and Quest object.
    
    interface : Widget
        Widget to be populated with items.
    """
    self._populate_interface(data, interface, self.on_toggle_new)

def _populate_update_interface(self, data: Dict[str,Quest], interface: Widget) -> None:
    """
    Fills a widget with 0 or more items (Grilayout with an Image or AsyncImage and a ToggleButton).

    Nem items acts over quests to be updated.

    Parameters
    ----------
    data : Dict[str,Quest]
        Dictionary having quests title and Quest object.
    
    interface : Widget
        Widget to be populated with items.
    """
    self._populate_interface(data, interface, self.on_toggle_update)

def _toggle_image(self, widget: Image, checked: int, total: int) -> None:
    """
    Switchs Image image, according with items counting.

    Parameters
    ----------
    widget : Image
        Image object to be changed.

    checked : int
        Items counting.

    total : int
        Total of items to compare.

    """    

    # Constants definition with image files names 
    ALL_IMAGE = "resources/check.png"
    NONE_IMAGE = "resources/none.png"
    SOME_IMAGE = "resources/some.png"

    # Validation of data and image selection
    if checked == total:
        widget.source = ALL_IMAGE
    elif checked == 0:
        widget.source = NONE_IMAGE
    else:
        widget.source = SOME_IMAGE