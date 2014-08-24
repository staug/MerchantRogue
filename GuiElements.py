import Constants
from planes import Plane

__author__ = 'Tangil'

import planes
import planes.gui
import pygame
import GameData


class TradePlane(planes.gui.Container):
    """
    A BuyPlane wraps an OptionList, a list of PlusMinus and an OK button,
    calling a callback when a selection is confirmed.
    """

    class PlusMinusList(planes.gui.Container):
        """A list of options to select from.

           Options are subplanes of OptionList, named option0, option1, ..., optionN

           Please note that it is not possible to confirm a selection here. Use a
           wrapper like OptionSelector to accomplish that.

           Additional attributes:

           OptionList.selected
               The selected Option
        """

        def __init__(self, number, lineheight, good_quantity=None):
            """Initialise the OptionList.
               option_list is a list of strings to be displayed as options.
            """

            # Call base class init
            #
            planes.gui.Container.__init__(self, "plusminuslist")

            # Add options
            #
            for num in range(number):
                a_value = None
                if good_quantity:
                    plusminus = planes.gui.PlusMinusBox(str(num), 2, value=good_quantity[num])
                else:
                    plusminus = planes.gui.PlusMinusBox(str(num), 2)
                self.sub(plusminus)

            return


    def __init__(self, name, text, goods, callback, quantity=None, width=300, lineheight=16, background_color=None,
                 price_modifier=None):
        """Initialise the OptionSelector.
           option_list is a list of strings to be displayed as options.
           callback is a function to be called with the selected Option instance
           as argument once the selection is made.
        """

        # Call base class init
        #
        planes.gui.Container.__init__(self,
                                      name,
                                      padding=5,
                                      background_color=background_color)

        # TODO: copied from Button.__init__. Maybe inherit from a third class 'Callback'?
        #
        self.callback = callback

        # Add options and OK button
        #
        goodlist = []
        for good in goods:
            goodlist.append(good.name + " " + str(good.regular_value) + " " + str(price_modifier[good.name]))
        ol = planes.gui.OptionList("option_list",
                                   goodlist,
                                   width - 150,
                                   lineheight)

        self.sub(ol)
        o2 = TradePlane.PlusMinusList(len(goods), 30, good_quantity=quantity)
        self.sub(o2)

        button = planes.gui.Button(text,
                                   pygame.Rect((0, 0), (o2.rect.width + ol.rect.width, lineheight)),
                                   self.selection_made)

        self.sub(button)
        ol.rect.left = 0
        o2.rect.topleft = ol.rect.topright
        button.rect.top = o2.rect.bottom
        self.rect.height = button.rect.bottom
        self.rect.width = o2.rect.right
        self.goods = goods

        return

    def selection_made(self, plane):
        """Button callback called when the user confirmed an option from the list.
           Calls OptionSelector.callback(ugly) with ugly list of tuple (good, qty).
        """
        # UGLY
        ugly = []

        for x in range(len(self.subplanes["plusminuslist"].subplanes)):
            value = self.subplanes["plusminuslist"].subplanes[str(x)].subplanes["textbox"].text
            if int(value) != 0:
                ugly.append((self.goods[x], int(value)))
        self.callback(ugly)
        return


class KenneyContainerStyle:
    def __init__(self, margin_top=10, margin_left=10, margin_bottom=10, margin_right=10, color=None,
                 background_color=None, single_last_widget_group=False, padding_v=5, padding_h=5):
        """
        Basic style for all specific containers
        :param margin_top: the container top margin (impacts sub container placement). Default 10.
        :param margin_left: the container left margin (impacts sub container placement). Default 10.
        :param margin_bottom: the container bottom margin (impacts sub container placement). Default 10.
        :param margin_right: the container right margin (impacts sub container placement). Default 10.
        :param color: the color of teh foreground
        :param background_color: the color of the background. If provided, an included surface will be drawn
        :param single_last_widget_group: make specific room for the last widget
        :param padding_v: the vertical padding between widgets
        :param padding_h: the horizontal padding between widgets
        :param font: filename of the font. It will be taken from the font folder.
        :return: a fully built container style
        """
        assert color, "At least one color needs to be provided"
        # Save the properties
        self.margin_top = margin_top
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.margin_bottom = margin_bottom
        self.padding_v = padding_v
        self.padding_h = padding_h
        self.color = color
        self.is_included = False
        if background_color:
            self.background_color = background_color
            self.is_included = True
        self.single_last_widget = single_last_widget_group


class KenneyContainer(planes.gui.Container):
    """A planes.gui.Container with variable width and height and a Kenney background.

       Additional attributes:

       TMBContainer.style
           An instance of TMBStyle.

       TMBContainer.background
           A Pygame Surface, holding the rendered background.
           Initially None, repainted in TMBContainer.sub().
    """

    V_ALIGN_MIDDLE = "middle"
    V_ALIGN_TOP = "top"
    V_ALIGN_BOTTOM = "bottom"
    H_ALIGN_CENTER = "center"
    H_ALIGN_LEFT = "left"
    H_ALIGN_RIGHT = "right"

    def __init__(self,
                 name=None,
                 style=None,
                 preferred_size=(10, 10),
                 normalize_size=True,
                 ignore_last_group_dimensions=False,
                 pos=(0, 0)):
        """Initialise.
           style is an instance of kenney style, which should hold the image name as well as the
           default margins & paddings...
        """
        # Call base
        if not name:
            name = str(id(self))
        self.name = name
        planes.gui.Container.__init__(self, name, style.padding_v)
        # save main arguments
        self.style = style
        self.background = None
        if not (preferred_size and preferred_size[0] and preferred_size[1]):
            preferred_size = (10, 10)
        self.preferred_size = preferred_size

        self.draggable = True
        self.grab = False
        self.subplanes_alignment = {}  # tuple (h_align, v_align) to remember the alignment of each.

        self.normalize_size = normalize_size  # indicate if we should normalize all widget size to the biggest
        self.ignore_last_group_height = ignore_last_group_dimensions
        self.rect.topleft = pos
        return

    def _resize(self):
        margin_top = self.style.margin_top  # this is the height of the top part
        margin_bottom = self.style.margin_bottom  # this is the height of the bottom part
        margin_left = self.style.margin_left  # this is the height of the bottom part
        margin_right = self.style.margin_right  # this is the height of the bottom part

        group_horizontal = []
        # First step: organize the widgets by horizontal group
        for name in self.subplanes_list:
            (h_plane_align, v_plane_align, fix_width, fix_height, stack_horizontal) = self.subplanes_alignment[name]
            required_height = self.subplanes[name].rect.height
            if fix_height:
                required_height = fix_height
            required_width = self.subplanes[name].rect.width
            if fix_width:
                required_width = fix_width
            if not stack_horizontal:
                group_horizontal.append([[name, required_height, required_width]])
            else:
                group_horizontal[-1].append([name, required_height, required_width])

        line_width = []
        line_height = []
        for index, widget_group in enumerate(group_horizontal):
            widget_group_width = 0
            widget_group_max_height = 0
            for widget in widget_group:
                # Is this widget higher than the other in the group? If yes, this is the new reference for this line.
                if widget_group_max_height < widget[1]:
                    widget_group_max_height = widget[1]
                # Width: we simply add the width
                widget_group_width += widget[2]
            line_width.append(widget_group_width + (len(widget_group) - 1) * self.style.padding_h)
            line_height.append(widget_group_max_height)

        max_line_width = max(line_width)
        max_line_height_except_last = max_line_height = max(line_height)

        total_width = margin_left + max_line_width + margin_right

        if self.ignore_last_group_height and len(group_horizontal) > 1:
            max_line_height_except_last = max(line_height[0:len(group_horizontal) - 1])

        y_pos = margin_top

        for index_group, widget_group in enumerate(group_horizontal):

            x_pos = margin_left
            required_height = 0

            for index, widget in enumerate(widget_group):
                name = widget[0]
                (h_plane_align,
                 v_plane_align,
                 fix_width,
                 fix_height,
                 stack_horizontal) = self.subplanes_alignment[name]

                required_height = line_height[index_group]
                if self.normalize_size:
                    required_height = max_line_height
                    if self.ignore_last_group_height and index_group != len(group_horizontal):
                        required_height = max_line_height_except_last

                required_width = widget[2]
                if index == 0:
                    if h_plane_align == KenneyContainer.H_ALIGN_CENTER:
                        x_pos += (max_line_width - line_width[index_group]) // 2
                    if h_plane_align == KenneyContainer.H_ALIGN_RIGHT:
                        x_pos += max_line_width - line_width[index_group]

                if v_plane_align == KenneyContainer.V_ALIGN_MIDDLE:
                    self.subplanes[name].rect.centery = y_pos + int(required_height / 2)
                elif v_plane_align == KenneyContainer.V_ALIGN_TOP:
                    self.subplanes[name].rect.top = y_pos
                elif v_plane_align == KenneyContainer.V_ALIGN_BOTTOM:
                    self.subplanes[name].rect.bottom = y_pos + required_height

                self.subplanes[name].rect.left = x_pos
                x_pos += (required_width + self.style.padding_h)

            y_pos += (required_height + self.style.padding_v)

        self.rect.height = max(self.preferred_size[1], y_pos + margin_bottom - self.style.padding_v)
        self.rect.width = max(self.preferred_size[0], total_width)

    def render_background(self):
        if self.style.is_included:
            list_image = [Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_" + self.style.background_color + ".png",
                          Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panelInset_" + self.style.color + ".png"]
            if self.style.single_last_widget and len(self.subplanes) > 0:
                # Not: this adds an extra 10 margin all around!
                for name in self.subplanes_list:
                    self.subplanes[name].rect.left += 10
                    self.subplanes[name].rect.top += 5
                self.rect.width += 20
                self.rect.height += 20

                group_horizontal = []
                # First step: organize the widgets by horizontal group
                for name in self.subplanes_list:
                    (h_plane_align, v_plane_align, fix_width, fix_height, stack_horizontal) = self.subplanes_alignment[
                        name]
                    required_height = self.subplanes[name].rect.height
                    if fix_height:
                        required_height = fix_height
                    if not stack_horizontal:
                        group_horizontal.append([[name, required_height]])
                    else:
                        group_horizontal[-1].append([name, required_height])

                last_widget_height = 0
                for widget in group_horizontal[-1]:
                    # Is this widget higher than the other in the group? If yes, this is the new reference for this line.
                    if last_widget_height < widget[1]:
                        last_widget_height = widget[1]

                bottom_margin = last_widget_height + 20
                internal_margin = [[10, 10, 10, bottom_margin]]

                # and we need to move the last widget group by an additional 5
                for widget_data in group_horizontal[-1]:
                    self.subplanes[widget_data[0]].rect.bottom = (self.rect.height - 10)

                self.background = IncludedSurface.render(self.rect.size, list_image,
                                                         list_internal_margin=internal_margin)
            else:
                self.background = IncludedSurface.render(self.rect.size, list_image)
        else:
            self.background = ScaledSurface.render(self.rect.size,
                                                   Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_" + self.style.color + ".png")

    def sub(self,
            plane,
            h_align=H_ALIGN_CENTER,
            v_align=V_ALIGN_MIDDLE,
            fix_width=None,
            fix_height=None,
            stack_horizontal=False):
        """
        Resize the container, update the position of plane and add it as a subplane.
        This will also repaint TMBContainer.background.
        """

        # Adapted from gui.Container method

        # First add the subplane by calling the base class method.
        # This also cares for re-adding an already existing subplane.
        planes.Plane.sub(self, plane)
        self.subplanes_alignment[plane.name] = (h_align, v_align, fix_width, fix_height, stack_horizontal)

        # Resize and recreate background
        self._resize()
        self.render_background()
        self.redraw()

        return

    def redraw(self):
        """
        Redraw the container image using the background.
        This also creates a new rendersurface.
        """
        self.image = self.background.copy()
        self.rendersurface = self.image.copy()
        return

    def remove(self, plane_identifier, resize_background=False):
        """
        Remove the subplane, then reposition remaining subplanes and resize the container.
        """
        # Adapted from gui.Container method
        # Accept Plane name as well as Plane instance
        if isinstance(plane_identifier, planes.Plane):
            name = plane_identifier.name
        else:
            name = plane_identifier
        planes.Plane.remove(self, name)

        # Now shrink and adapt background
        if resize_background:
            self._resize()
            self.render_background()

        self.redraw()
        return


class KenneyMultiColumnContainer(planes.gui.Container):
    """A Kenney Container that can hold multiple column.
    """

    V_ALIGN_MIDDLE = "middle"
    V_ALIGN_TOP = "top"
    V_ALIGN_BOTTOM = "bottom"
    H_ALIGN_CENTER = "center"
    H_ALIGN_LEFT = "left"
    H_ALIGN_RIGHT = "right"

    def __init__(self,
                 name=None,
                 style=None,
                 preferred_size=(10, 10),
                 normalize_size=True,
                 ignore_last_group_dimensions=False,
                 pos=(0, 0)):
        """Initialise.
           style is an instance of kenney style, which should hold the image name as well as the
           default margins & paddings...
        """
        # Call base
        if not name:
            name = str(id(self))
        self.name = name
        planes.gui.Container.__init__(self, name, style.padding_v)
        # save main arguments
        self.style = style
        self.background = None
        if not (preferred_size and preferred_size[0] and preferred_size[1]):
            preferred_size = (10, 10)
        self.preferred_size = preferred_size

        self.draggable = True
        self.grab = False
        self.rect.topleft = pos

        # the column is one of the most important part here.
        # It is a list of plan name (in order, top to down!).
        self.columns = [[]]
        # the subplane characteristics contain the data passed in the "sub" function. It is a dictionary with
        # plan_name -> (h_plane_align, v_plane_align, fix_width, fix_height, stack_horizontal, column_id)
        self.subplanes_characteristics = {}

        self.normalize_size = normalize_size  # indicate if we should normalize all widget size to the biggest
        # the last group of widgets (OK/Cancel) will always be in column 0. Here we highlight if we have such group
        # present. If yes, this group will be centered cross all columns.
        self.ignore_last_group_dimensions = ignore_last_group_dimensions

        return

    def _resize(self):
        margin_top = self.style.margin_top  # this is the height of the top part
        margin_bottom = self.style.margin_bottom  # this is the height of the bottom part
        margin_left = self.style.margin_left  # this is the height of the bottom part
        margin_right = self.style.margin_right  # this is the height of the bottom part

        list_of_group_horizontal = []
        # First step: organize the widgets by horizontal groups. Each group is a column.
        for index_column, column in enumerate(self.columns):
            list_of_group_horizontal.append([])
            for name in column:
                (h_plane_align,
                 v_plane_align,
                 fix_width,
                 fix_height,
                 stack_horizontal) = self.subplanes_characteristics[name]
                required_height = self.subplanes[name].rect.height
                if fix_height:
                    required_height = fix_height
                required_width = self.subplanes[name].rect.width
                if fix_width:
                    required_width = fix_width
                if not stack_horizontal:
                    list_of_group_horizontal[index_column].append([[name, required_height, required_width]])
                else:
                    list_of_group_horizontal[index_column][-1].append([name, required_height, required_width])

        list_of_line_width = []
        list_of_line_height = []
        for index_column, column in enumerate(self.columns):
            list_of_line_width.append([])
            list_of_line_height.append([])
            for index, widget_group in enumerate(list_of_group_horizontal[index_column]):
                widget_group_width = 0
                widget_group_max_height = 0
                for widget in widget_group:
                    # Is this widget higher than the other in the group? If yes, this is the new reference for this line.
                    if widget_group_max_height < widget[1]:
                        widget_group_max_height = widget[1]
                    # Width: we simply add the width
                    widget_group_width += widget[2]
                list_of_line_width[index_column].append(
                    widget_group_width + (len(widget_group) - 1) * self.style.padding_h)
                list_of_line_height[index_column].append(widget_group_max_height)

        max_line_width_list = []
        for list_line_width in list_of_line_width:
            max_line_width_list.append(max(list_line_width))

        total_width = margin_left + sum(max_line_width_list) + 2 * self.style.padding_h * (
        len(max_line_width_list) - 1) + margin_right

        max_line_height_list = []
        for list_line_height in list_of_line_height:
            max_line_height_list.append(max(list_line_height))

        max_line_height_except_last = 20
        if self.ignore_last_group_dimensions and len(list_of_line_height[0]) > 1:
            max_line_height_except_last = max(list_of_line_height[0][0:len(list_of_line_height[0]) - 1])

        y_pos_list = []
        x_column_pos = margin_left

        for index_column, column in enumerate(self.columns):
            y_pos = margin_top

            for index_group, widget_group in enumerate(list_of_group_horizontal[index_column]):

                required_height = 0
                x_pos = x_column_pos

                for index, widget in enumerate(widget_group):
                    name = widget[0]
                    (h_plane_align,
                     v_plane_align,
                     fix_width,
                     fix_height,
                     stack_horizontal) = self.subplanes_characteristics[name]

                    required_height = list_of_line_height[index_column][index_group]
                    if self.normalize_size:
                        required_height = max_line_height_list[index_column]
                        if index_column == 0 and self.ignore_last_group_dimensions and index_group != len(
                                list_of_group_horizontal):
                            required_height = max_line_height_except_last

                    required_width = widget[2]
                    if index == 0:
                        if h_plane_align == KenneyContainer.H_ALIGN_CENTER:
                            x_pos += (max_line_width_list[index_column] - list_of_line_width[index_column][
                                index_group]) // 2
                        if h_plane_align == KenneyContainer.H_ALIGN_RIGHT:
                            x_pos += max_line_width_list[index_column] - list_of_line_width[index_column][index_group]

                    if v_plane_align == KenneyContainer.V_ALIGN_MIDDLE:
                        self.subplanes[name].rect.centery = y_pos + int(required_height / 2)
                    elif v_plane_align == KenneyContainer.V_ALIGN_TOP:
                        self.subplanes[name].rect.top = y_pos
                    elif v_plane_align == KenneyContainer.V_ALIGN_BOTTOM:
                        self.subplanes[name].rect.bottom = y_pos + required_height

                    self.subplanes[name].rect.left = x_pos
                    x_pos += (required_width + self.style.padding_h)

                y_pos += (required_height + self.style.padding_v)

            y_pos_list.append(y_pos)
            x_column_pos += (max_line_width_list[index_column] + 2 * self.style.padding_h)

            # TODO; the last group of column 0 (OK/Cancel) needs to be shifted down AND centered if ignore last widget height!!
            # Note: the y pos of the last widget group needs to be changed only if the ypos of teh others is < than y in pos 0

        self.rect.height = max(self.preferred_size[1], max(y_pos_list) + margin_bottom - self.style.padding_v)
        self.rect.width = max(self.preferred_size[0], total_width)

    def render_background(self):
        if self.style.is_included:
            list_image = [Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_" + self.style.background_color + ".png",
                          Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panelInset_" + self.style.color + ".png"]
            if self.style.single_last_widget and len(self.subplanes) > 0:
                # Not: this adds an extra 10 margin all around!
                for name in self.subplanes_list:
                    self.subplanes[name].rect.left += 10
                    self.subplanes[name].rect.top += 5
                self.rect.width += 20
                self.rect.height += 20

                group_horizontal = []
                # First step: organize the widgets by horizontal group
                for name in self.subplanes_list:
                    (h_plane_align, v_plane_align, fix_width, fix_height, stack_horizontal, column_index) = \
                        self.subplanes_characteristics[
                        name]
                    required_height = self.subplanes[name].rect.height
                    if fix_height:
                        required_height = fix_height
                    if not stack_horizontal:
                        group_horizontal.append([[name, required_height]])
                    else:
                        group_horizontal[-1].append([name, required_height])

                last_widget_height = 0
                for widget in group_horizontal[-1]:
                    # Is this widget higher than the other in the group? If yes, this is the new reference for this line.
                    if last_widget_height < widget[1]:
                        last_widget_height = widget[1]

                bottom_margin = last_widget_height + 20
                internal_margin = [[10, 10, 10, bottom_margin]]

                # and we need to move the last widget group by an additional 5
                for widget_data in group_horizontal[-1]:
                    self.subplanes[widget_data[0]].rect.bottom = (self.rect.height - 10)

                self.background = IncludedSurface.render(self.rect.size, list_image,
                                                         list_internal_margin=internal_margin)
            else:
                self.background = IncludedSurface.render(self.rect.size, list_image)
        else:
            self.background = ScaledSurface.render(self.rect.size,
                                                   Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_" + self.style.color + ".png")

    def sub(self,
            plane,
            column_index=0,
            h_align=H_ALIGN_CENTER,
            v_align=V_ALIGN_MIDDLE,
            fix_width=None,
            fix_height=None,
            stack_horizontal=False):
        """
        Resize the container, update the position of plane and add it as a subplane.
        This will also repaint TMBContainer.background.
        """

        # Adapted from gui.Container method

        # First add the subplane by calling the base class method.
        # This also cares for re-adding an already existing subplane.
        planes.Plane.sub(self, plane)
        # Now, takes care of putting the container in the correct column.
        while len(self.columns) <= column_index:
            self.columns.append([])
        self.columns[column_index].append(plane.name)
        self.subplanes_characteristics[plane.name] = (h_align,
                                                      v_align,
                                                      fix_width,
                                                      fix_height,
                                                      stack_horizontal)

        # Resize and recreate background
        self._resize()
        self.render_background()
        self.redraw()

        return

    def redraw(self):
        """
        Redraw the container image using the background.
        This also creates a new rendersurface.
        """
        self.image = self.background.copy()
        self.rendersurface = self.image.copy()
        return

    def remove(self, plane_identifier, resize_background=False):
        """
        Remove the subplane, then reposition remaining subplanes and resize the container.
        """
        # Adapted from gui.Container method
        # Accept Plane name as well as Plane instance
        if isinstance(plane_identifier, planes.Plane):
            name = plane_identifier.name
        else:
            name = plane_identifier
        planes.Plane.remove(self, name)

        # Now shrink and adapt background
        if resize_background:
            self._resize()
            self.render_background()

        self.redraw()
        return


class KenneyPopupLabel(KenneyContainer):
    """
    A popup that displays a message (wrapped) with a OK button.
    It is destroyed when OK is clicked, and an optional callback is called.
    The message will be wrapped at newline characters.
    """

    def __init__(self,
                 message,
                 style=None,
                 button_style=None,
                 message_h_align=KenneyContainer.H_ALIGN_CENTER,
                 callback=None,
                 pos=(0, 0)):
        """
        Initialize the popup
        :param message: the message to be displayed, will be splitted at "\n"
        :param style: the style for the container
        :param button_style: the style for the button
        :param message_h_align: alignment of the message (default: center)
        :param callback: optional callback that will be called when the button is pressed.
        :return:
        """
        if not style:
            style = Constants.DEFAULT_CONTAINER_STYLE
        self.callback = callback

        KenneyContainer.__init__(self, style=style, preferred_size=(10, 20), ignore_last_group_dimensions=True, pos=pos)

        lines = message.split("\n")
        for line_no in range(len(lines)):
            self.sub(KenneyWidgetLabel(lines[line_no]), h_align=message_h_align)
        self.sub(KenneyWidgetButton(self.ok, label="OK", style=button_style))

        return

    def ok(self, plane, event=None):
        """
        Button clicked callback which destroys the OkBox.
        """
        if self.callback:
            self.callback(source=self, event=event)
        self.destroy()
        return


class KenneyPopupLabelCancel(KenneyContainer):
    """
    A popup that displays a message (wrapped) with a OK and cancel button.
    It is destroyed when OK or Cancel is clicked, and an optional callback is called.
    The message will be wrapped at newline characters.
    """

    def __init__(self,
                 message,
                 style=None,
                 button_style=None,
                 message_h_align=KenneyContainer.H_ALIGN_CENTER,
                 callback_ok=None,
                 callback_cancel=None,
                 pos=(0, 0)):
        """
        Initialize the popup
        :param message: the message to be displayed, will be splitted at "\n"
        :param style: the style for the container
        :param button_style: the style for the button
        :param message_h_align: alignment of the message (default: center)
        :param callback: optional callback that will be called when the button is pressed.
        :return:
        """
        if not style:
            style = Constants.DEFAULT_CONTAINER_STYLE
        self.callback_ok = callback_ok
        self.callback_cancel = callback_cancel

        KenneyContainer.__init__(self, style=style, preferred_size=(10, 20), ignore_last_group_dimensions=True, pos=pos)

        lines = message.split("\n")
        for line_no in range(len(lines)):
            self.sub(KenneyWidgetLabel(lines[line_no]), h_align=message_h_align)
        self.sub(KenneyWidgetButton(self.ok, label="OK", style=button_style))
        self.sub(KenneyWidgetButton(self.cancel, label="Cancel", style=button_style), stack_horizontal=True)

        return

    def ok(self, plane, event=None):
        if self.callback_ok:
            self.callback_ok(source=self, event=event)
        self.destroy()
        return

    def cancel(self, plane, event=None):
        if self.callback_cancel:
            self.callback_cancel(source=self, event=event)
        self.destroy()
        return


class KenneyPopupOption(KenneyContainer):
    """
    Display a list of choice that are selectable
    It is destroyed when OK or Cancel is clicked, and the callback is called with the selected object(s).
    """

    class ButtonGroup():
        """
        The button group governs group of selection, like a RadioGroup would do.
        """

        def __init__(self, multi_allowed=False):
            self.object_of_group = []
            self.button_of_group = []
            self.multi_allowed = multi_allowed
            return

        def add_button(self, button, object_controlled):
            self.object_of_group.append(object_controlled)
            self.button_of_group.append(button)
            return

        def notify(self, button_notifier):
            """
            This function is used when one button is changed, takes care of the multi selection.
            """
            if not self.multi_allowed:
                for button in self.button_of_group:
                    if button.is_selected and button.name != button_notifier.name:
                        button.is_selected = False
                        button.redraw(force=True)
            return

        def get_selected_objects(self):
            """
            :return all the object which button has the status selected
            """
            objects = []
            for index, button in enumerate(self.button_of_group):
                if button.is_selected:
                    objects.append(self.object_of_group[index])
            return objects


    def __init__(self,
                 group_of_options,
                 selected_option_indexes=None,
                 multiple_selection_allowed=None,
                 use_image=False,
                 width=None,
                 height=None,
                 style=None,
                 button_style=None,
                 callback_ok=None,
                 callback_cancel=None,
                 pos=(0, 0)):
        """
        Initialize the popup
        :param message: the message to be displayed, will be splitted at "\n"
        :param style: the style for the container
        :param button_style: the style for the button
        :param message_h_align: alignment of the message (default: center)
        :param callback: optional callback that will be called when the button is pressed.
        :return:
        """
        if not style:
            style = Constants.DEFAULT_CONTAINER_STYLE
        if not button_style:
            button_style = Constants.DEFAULT_WIDGET_STYLE
        self.callback_ok = callback_ok
        self.callback_cancel = callback_cancel

        KenneyContainer.__init__(self,
                                 style=style,
                                 preferred_size=(width, height),
                                 ignore_last_group_dimensions=True,
                                 normalize_size=False,
                                 pos=pos)
        # the options are a list of list
        self.button_groups = []
        for group_index, options in enumerate(group_of_options):
            group = KenneyPopupOption.ButtonGroup()
            if multiple_selection_allowed and multiple_selection_allowed[group_index]:
                group.multi_allowed = True
            self.button_groups.append(group)
            for option_index, option in enumerate(options):
                selected = False
                if selected_option_indexes and selected_option_indexes[group_index] == option_index:
                    selected = True
                button = KenneyWidgetOptionButton(group=group, use_image=use_image,
                                                  style=button_style, selected=selected)
                self.button_groups[-1].add_button(button, option)
                self.sub(button)
                self.sub(KenneyWidgetLabel(str(option)), stack_horizontal=True)
        width = button_style.get_font_size_for("Cancel")[0]
        self.sub(KenneyWidgetButton(self.ok, label="OK", style=button_style, width=width))
        self.sub(KenneyWidgetButton(self.cancel, label="Cancel", style=button_style, width=width),
                 stack_horizontal=True)

        return

    def ok(self, plane, event=None):
        if self.callback_ok:
            object_list = []
            for group in self.button_groups:
                for object_selected in group.get_selected_objects():
                    object_list.append(object_selected)
            self.callback_ok(source=self, event=event, object_selected=object_list)
        self.destroy()
        return

    def cancel(self, plane, event=None):
        if self.callback_cancel:
            object_list = []
            for group in self.button_groups:
                for object_selected in group.get_selected_objects():
                    object_list.append(object_selected)
            self.callback_cancel(source=self, event=event, object_selected=object_list)
        self.destroy()
        return


class KenneyPopupOptionMultiColumns(KenneyMultiColumnContainer):
    """
    Display a list of choice that are selectable
    It is destroyed when OK or Cancel is clicked, and the callback is called with the selected object(s).
    """

    class ButtonGroup():
        """
        The button group governs group of selection, like a RadioGroup would do.
        """

        def __init__(self, multi_allowed=False):
            self.object_of_group = []
            self.button_of_group = []
            self.multi_allowed = multi_allowed
            return

        def add_button(self, button, object_controlled):
            self.object_of_group.append(object_controlled)
            self.button_of_group.append(button)
            return

        def notify(self, button_notifier):
            """
            This function is used when one button is changed, takes care of the multi selection.
            """
            if not self.multi_allowed:
                for button in self.button_of_group:
                    if button.is_selected and button.name != button_notifier.name:
                        button.is_selected = False
                        button.redraw(force=True)
            return

        def get_selected_objects(self):
            """
            :return all the object which button has the status selected
            """
            objects = []
            for index, button in enumerate(self.button_of_group):
                if button.is_selected:
                    objects.append(self.object_of_group[index])
            return objects


    def __init__(self,
                 group_of_options,
                 selected_option_indexes=None,
                 multiple_selection_allowed=None,
                 use_image=False,
                 width=None,
                 height=None,
                 style=None,
                 button_style=None,
                 callback_ok=None,
                 callback_cancel=None,
                 pos=(0, 0)):
        """
        Initialize the popup
        :param message: the message to be displayed, will be splitted at "\n"
        :param style: the style for the container
        :param button_style: the style for the button
        :param message_h_align: alignment of the message (default: center)
        :param callback: optional callback that will be called when the button is pressed.
        :return:
        """
        if not style:
            style = Constants.DEFAULT_CONTAINER_STYLE
        if not button_style:
            button_style = Constants.DEFAULT_WIDGET_STYLE
        self.callback_ok = callback_ok
        self.callback_cancel = callback_cancel

        KenneyMultiColumnContainer.__init__(self,
                                            style=style,
                                            preferred_size=(width, height),
                                            ignore_last_group_dimensions=True,
                                            normalize_size=False,
                                            pos=pos)
        # the options are a list of list
        self.button_groups = []
        for group_index, options in enumerate(group_of_options):
            group = KenneyPopupOption.ButtonGroup()
            if multiple_selection_allowed and multiple_selection_allowed[group_index]:
                group.multi_allowed = True
            self.button_groups.append(group)
            for option_index, option in enumerate(options):
                selected = False
                if selected_option_indexes and selected_option_indexes[group_index] == option_index:
                    selected = True
                button = KenneyWidgetOptionButton(group=group, use_image=use_image,
                                                  style=button_style, selected=selected)
                self.button_groups[-1].add_button(button, option)
                self.sub(button, column_index=group_index)
                self.sub(KenneyWidgetLabel(str(option)), stack_horizontal=True, column_index=group_index)
        width = button_style.get_font_size_for("Cancel")[0]
        self.sub(KenneyWidgetButton(self.ok, label="OK", style=button_style, width=width))
        self.sub(KenneyWidgetButton(self.cancel, label="Cancel", style=button_style, width=width),
                 stack_horizontal=True)

        return

    def ok(self, plane, event=None):
        if self.callback_ok:
            object_list = []
            for group in self.button_groups:
                for object_selected in group.get_selected_objects():
                    object_list.append(object_selected)
            self.callback_ok(source=self, event=event, object_selected=object_list)
        self.destroy()
        return

    def cancel(self, plane, event=None):
        if self.callback_cancel:
            object_list = []
            for group in self.button_groups:
                for object_selected in group.get_selected_objects():
                    object_list.append(object_selected)
            self.callback_cancel(source=self, event=event, object_selected=object_list)
        self.destroy()
        return


class KenneyGetStringDialog(KenneyContainer):
    """A combination of KenneyContainer, Label, TextBox and Button that asks the user for a string.
    """

    def __init__(self, prompt, callback, numberline=1, width=None, style=None, button_style=None, pos=(0, 0)):

        if not style:
            style = Constants.DEFAULT_CONTAINER_STYLE
        if not button_style:
            button_style = Constants.DEFAULT_WIDGET_STYLE
        # Base class __init__()
        KenneyContainer.__init__(self, style=style, ignore_last_group_dimensions=True, pos=pos)

        self.draggable = False

        # Adapted from planes.gui.GetStringDialog
        self.callback = callback
        self.sub(KenneyWidgetLabel(prompt))
        # text box - compute the argument.
        rect = button_style.font.render(prompt, True, button_style.text_color).get_rect()
        if width:
            rect.width = width
        rect.height = numberline * rect.height + style.padding_v * (numberline - 1)
        self.textbox = planes.gui.TextBox("textbox", pygame.Rect((0, 0), rect.size), return_callback=self.return_key)
        self.sub(self.textbox, stack_horizontal=True)
        self.sub(KenneyWidgetButton(self.ok, label="OK", style=button_style))
        GameData.display.key_sensitive(self.textbox)

        return

    def ok(self, plane, event=None):
        """Button callback to destroy the GetStringDialog and call GetStringDialog.callback(string).
        """

        # Deactivate to lose the cursor
        self.textbox.deactivate()

        callback = self.callback
        string = self.textbox.text
        self.destroy()
        callback(text=string)

        return

    def return_key(self, text, event=None):
        """Return key callback to destroy the GetStringDialog and call GetStringDialog.callback(string).
        """

        callback = self.callback
        self.destroy()
        callback(text=text)
        return


class KenneyWidgetStyle:
    V_ALIGN_MIDDLE = "middle"
    V_ALIGN_TOP = "top"
    V_ALIGN_BOTTOM = "bottom"
    H_ALIGN_CENTER = "center"
    H_ALIGN_LEFT = "left"
    H_ALIGN_RIGHT = "right"

    IMAGE_DICT = {}

    def __init__(self,
                 color=None,
                 background_image_filename=None,
                 h_align=H_ALIGN_CENTER,
                 v_align=V_ALIGN_MIDDLE,
                 h_margin=0,
                 v_margin=0,
                 text_color=(0, 0, 0),
                 font=None,
                 default_height=30,
                 default_width=100,
                 font_size=14
    ):
        """
        Basic style for all widgets
        :param color: the color of the foreground. Must be present if background image is not there
        :param background_image_filename: a reference to the background image (note: it will be saved). Must be present if color is not there.
        :param h_align: the horizontal text alignment (if this widget has a text) - center, left or right.
        :param v_align: the vertical text alignment (if this widget has a text) - top, middle or center.
        :param h_margin: in case of left/right alignment, the horizontal margin
        :param v_margin: in case of top/bottom alignment, the vertical margin
        :param text_color: the text color (if any)
        :param default_height: if no height is provided, this will be the default
        :param default_width: if no width is provided, this will be the default
        :return: a fully built container style
        """
        assert color or background_image_filename, "Either a color or a background image needs to be provided"
        # Save the properties
        self.color = color
        self.background_image_filename = background_image_filename
        if background_image_filename and background_image_filename not in KenneyWidgetStyle.IMAGE_DICT.keys():
            KenneyWidgetStyle.IMAGE_DICT[background_image_filename] = \
                pygame.image.load(background_image_filename).convert_alpha()
        self.h_align = h_align
        self.v_align = v_align
        self.h_margin = h_margin
        self.v_margin = v_margin
        self.default_height = default_height
        self.default_width = default_width
        self.text_color = text_color
        a_font = None
        if font:
            a_font = Constants.FONT_FOLDER + font + ".ttf"
        self.font = pygame.font.Font(a_font, font_size)

        return

    def get_font_size_for(self, text):
        """
        Compute the space occupied by the text. If no font exists, the default is return
        :param text: the text which space we want to evaluate
        :return: a size tuple.
        """
        if self.font:
            return self.font.size(text)
        else:
            dimensions = (self.default_width, self.default_height)
            return dimensions


class KenneyWidget:
    """
    Base class for fixed-height, flexible-width widgets with a background.
    """

    def __init__(self, style, width, height=None):
        """
        Initialise LMRWidget.background from width and style given.
        width is the total widget width in pixels.
        style is an instance of KenneyWidgetStyle.
        If height is not given it is taken from the style.default_height.
        """
        self.style = style
        # Compute dimensions
        if not height:
            height = style.default_height
        # Dimensions
        if style.color:
            self.background = ScaledSurface.render(
                (width, height), Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_" + self.style.color + ".png")
        else:
            self.background = pygame.Surface((width, height), flags=pygame.SRCALPHA).convert_alpha()
            self.background.blit(
                pygame.transform.smoothscale(KenneyWidgetStyle[style.background_image_filename].copy, (width, height)))


class KenneyWidgetLabel(planes.Plane):
    """
    A specific label object, able to follow n object with/without an attribute
    """

    def __init__(self, text=None, width=None, height=None, style=None, follow_object=None, follow_attribute=None,
                 pos=(0, 0)):
        """Initialise the Label.
           text is the text to be written on the Label. If text is None, it is
           replaced by an empty string.
        """
        # Call base class init
        if not style:
            style = Constants.DEFAULT_WIDGET_STYLE
        self.style = style

        required_width = style.default_width
        required_height = style.default_height

        if width:
            required_width = width
        if height:
            required_height = height

        self.follow_object = follow_object
        self.follow_attribute = follow_attribute

        test_attribute = self._get_text()
        if test_attribute:
            # if we follow an object or an attribute, then we overwrite the text
            text = test_attribute

        if text is not None:
            self.text = text
            (required_width, required_height) = self.style.font.size(self.text)
        else:
            self.text = ""

        if width:
            required_width = max(width, required_width)
        if height:
            required_height = max(height, required_height)

        planes.Plane.__init__(self, str(id(self)),
                              pygame.Rect(pos, (required_width, required_height)), draggable=False, grab=False)

        self.cached_text = None
        self.background_color = self.cached_color = self.current_color = (0, 0, 0, 0)
        self.image = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)

        self.redraw()
        return

    def update(self):
        """
        Renew the text on the label, then call the base class method.
        """
        test_attribute = self._get_text()
        if test_attribute:
            # if we follow an object or an attribute, then we overwrite the text
            self.text = test_attribute
        self.redraw()
        planes.Plane.update(self)
        return

    def redraw(self):
        """
        Redraw the Label if necessary.
        """

        if self.text != self.cached_text or self.current_color != self.cached_color:
            self.image.fill(self.current_color)

            # Text is centered on rect.
            fontsurf = self.style.font.render(self.text, True, self.style.text_color)
            centered_rect = fontsurf.get_rect()

            # Get a neutral center of self.rect
            centered_rect.center = pygame.Rect((0, 0), self.rect.size).center
            self.image.blit(fontsurf, centered_rect)

            # Force redraw in render()
            self.last_rect = None

            self.cached_text = self.text
            self.cached_color = self.current_color

        return

    def _get_text(self):
        if self.follow_attribute:
            assert self.follow_object, "An attribute was set without object??"
            return str(getattr(self.follow_object, self.follow_attribute))
        elif self.follow_object:
            return str(self.object_followed)
        else:
            return None


class KenneyWidgetButton(KenneyWidget, KenneyWidgetLabel):
    """
    A planes.gui.Button enhanced with Kenney, showing a scaled surface as background.
    """

    def __init__(self, callback, width=None, height=None, style=None, label=None, pos=(0, 0)):
        """Initialise the Button.

           label is the Text to be written on the button.

           callback is the function to be called with callback(Button) when the
           Button is clicked with the left mouse button.

           style is an instance of LMRStyle. If omitted, GREY_BUTTON_STYLE will be
           used.
        """
        if not style:
            style = Constants.DEFAULT_WIDGET_STYLE
        if not width:
            width = style.default_width
        if not height:
            height = style.default_height

        if label is not None:
            size = style.font.size(label)
            width = max(size[0] + 20, width)
            height = max(size[1] + 10, height)

        # Initialise self.background
        KenneyWidget.__init__(self, style, width, height=height)
        # Now call base class.
        KenneyWidgetLabel.__init__(self, text=label, width=width, height=height, style=style, pos=pos)

        # Overwrite Plane base class attributes
        self.left_click_callback = callback
        self.highlight = True
        self.clicked_counter = 0
        self.redraw()
        return

    def redraw(self):
        """Conditionally redraw the Button.
        """

        # Partly copied from Label.redraw()
        if self.text != self.cached_text:
            # Copy, don't blit, taking care for transparency
            self.image = self.background.copy()
            # Text is centered on rect.
            fontsurf = self.style.font.render(self.text, True, self.style.text_color)
            centered_rect = fontsurf.get_rect()

            # Get a neutral center of self.rect
            centered_rect.center = pygame.Rect((0, 0), self.rect.size).center

            # Anticipate a drop shadow: move the text up a bit
            centered_rect.move_ip(0, -1)
            self.image.blit(fontsurf, centered_rect)

            # Force redraw in render()
            self.last_rect = None
            self.cached_text = self.text
        return

    def update(self):
        """
        Change color if clicked, then call the base class method.
        """
        if self.clicked_counter:
            self.clicked_counter = self.clicked_counter - 1
            if not self.clicked_counter:
                # Just turned zero, restore original background
                self.current_color = self.background_color
        KenneyWidgetLabel.update(self)

        return

    def clicked(self, button_name, event=None):
        """Plane standard method, called when there is a MOUSEDOWN event on this plane.
           Changes the Button color for some frames and calls the base class implementation.
        """
        if button_name == "left":
            self.clicked_counter = 4
            # Half-bright
            self.current_color = list(map(lambda i: int(i * 0.5), self.current_color))
            self.redraw()

        # Call base class implementation which will call the callback
        KenneyWidgetLabel.clicked(self, button_name, event=event)
        return


class KenneyWidgetIconButton(KenneyWidget, KenneyWidgetLabel):
    """
    A planes.gui.Button enhanced diplaying a single image and no text.
    If width/height are not passed, the image dimensions are used, else the image is resized.
    """
    IMAGE_DICT = {}

    def __init__(self, callback, image_source_filename, width=None, height=None, pos=(0, 0)):
        """
        Initialise the Button.
        """

        dimension = (width, height)
        if not width:
            dimension = None
        self.icon_image = ScaledImage.render(image_source_filename, target_dimension=dimension)
        (width, height) = self.icon_image.get_rect().size

        # Initialise self.background
        KenneyWidget.__init__(self, Constants.DEFAULT_WIDGET_STYLE, width, height=height)
        # Now call base class.
        KenneyWidgetLabel.__init__(self, width=width, height=height, pos=pos)

        # Overwrite Plane base class attributes
        self.text = " "
        self.background = self.icon_image
        self.left_click_callback = callback
        self.highlight = True
        self.clicked_counter = 0
        self.redraw()
        return

    def redraw(self):
        """Conditionally redraw the Button.
        """
        # Partly copied from Label.redraw()
        if self.text != self.cached_text:
            # Copy, don't blit, taking care for transparency
            self.image = self.background.copy()
            self.last_rect = None
            self.cached_text = self.text
        return

    def update(self):
        # """
        # Change color if clicked, then call the base class method.
        # """
        # if self.clicked_counter:
        # self.clicked_counter = self.clicked_counter - 1
        # if not self.clicked_counter:
        # # Just turned zero, restore original background
        #         self.current_color = self.background_color
        KenneyWidgetLabel.update(self)

        return

    def clicked(self, button_name, event=None):
        """Plane standard method, called when there is a MOUSEDOWN event on this plane.
           Changes the Button color for some frames and calls the base class implementation.
        """
        if button_name == "left":
            self.clicked_counter = 4
            # Half-bright
            self.current_color = list(map(lambda i: int(i * 0.5), self.current_color))
            self.redraw()

        # Call base class implementation which will call the callback
        KenneyWidgetLabel.clicked(self, button_name, event=event)
        return


class KenneyWidgetOptionButton(KenneyWidget, KenneyWidgetLabel):
    """
    A specific button to be used for a list of selection, which keeps in memory a state.
    Change color when selected when it is selected.
    """

    def __init__(self, group=None, use_image=False, width=None, height=None, style=None, pos=(0, 0), selected=False):
        """
        Initialize the button
        :param use_image: if set to True, one of the Kenney icon check will be used, otherwise a pannel will be used
        :param width: the width, if not set the image size will be used, else the default style
        :param height: the height, if not set the image size will be used, else the default style
        :param style: the style - used for color (front and background).
        :param pos: the position for the image
        :param group: the group for the button. The group is notified when the button is clicked
        :param selected: the starting value for this button

        :return:
        """

        if not style:
            style = Constants.DEFAULT_WIDGET_STYLE
        if use_image:
            dimensions = None
            image_name = Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "iconCheck_" + style.color + ".png"
            if width and height:
                dimensions = (width, height)
            self.icon_image = ScaledImage.render(image_name, dimensions)
            width = self.icon_image.get_rect().width
            height = self.icon_image.get_rect().height
        else:
            self.icon_image = None
            if not width:
                width = style.default_width
            if not height:
                height = style.default_height

        self.is_selected = selected
        self.group = group
        # Initialise self.background
        KenneyWidget.__init__(self, style, width, height=height)
        # Now call base class.
        KenneyWidgetLabel.__init__(self, width=width, height=height, style=style, pos=pos)
        # Overwrite Plane base class attributes
        if self.icon_image:
            self.background = self.icon_image
        alternate_style = KENNEY_WIDGET_STYLE_BLUE
        if style == KENNEY_WIDGET_STYLE_BLUE:
            alternate_style = KENNEY_WIDGET_STYLE_BROWN
        if self.icon_image:
            alternate_image = Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "iconCheck_" + alternate_style.color + ".png"
            dimensions = (width, height)
            self.alternate_background = ScaledImage.render(alternate_image, dimensions)
        else:
            self.alternate_background = KenneyWidget(alternate_style, width, height=height).background

        self.highlight = True
        self.redraw(force=True)
        return

    def redraw(self, force=False):
        """Conditionally redraw the Button.
        """
        # Partly copied from Label.redraw()
        if force:
            # Copy, don't blit, taking care for transparency
            if self.is_selected:
                self.image = self.alternate_background.copy()
            else:
                self.image = self.background.copy()

            # Force redraw in render()
            self.last_rect = None
            self.cached_text = self.text
        return

    def clicked(self, button_name, event=None):
        """Plane standard method, called when there is a MOUSEDOWN event on this plane.
           Changes the Button color for some frames and calls the base class implementation.
        """
        self.is_selected = not self.is_selected
        if self.group:
            self.group.notify(self)

        if button_name == "left":
            self.redraw(force=True)
        return


class ScaledImage:
    IMAGE_DICT = {}

    @staticmethod
    def render(image_source_filename, target_dimension=None):
        """
        load and possibly resize (if target dimension is given) an image
        :param image_source_filename: the complete path and filename (including folder) for the source image
        :param target_dimension: a tuple (width, height) for the target image
        :return: a copy of the surface with the correct background
        """
        if image_source_filename not in ScaledImage.IMAGE_DICT.keys():
            ScaledImage.IMAGE_DICT[image_source_filename] = pygame.image.load(image_source_filename).convert_alpha()

        image_source = ScaledImage.IMAGE_DICT[image_source_filename].copy()
        if target_dimension:
            return pygame.transform.smoothscale(image_source, target_dimension)
        return image_source


class ScaledSurface:
    IMAGE_DICT = {}

    @staticmethod
    def render(target_dimension, image_source_filename, image_corner_dimension=(10, 10), top=10, bottom=10, left=10,
               right=10, use_max_width=True, use_max_height=True):
        """
        Auto adjust a rectangular image (like a button) to a given dimension by cutting its to pieces.
        :param target_dimension: a tuple (width, height) for the target image
        :param image_source_filename: the complete path and filename (including folder) for the source image
        :param image_corner_dimension: a tuple describing the corner size of the image - default (10, 10)
        :param top: which part of the image is copied over, starting top left corner.
        :param bottom: which part of the image is copied over, starting bottom left corner.
        :param left: which left part of the image is copied over, starting top left corner.
        :param right: which right part of the image is copied over, starting top right corner.
        :return: a surface with the correct background
        """

        (width, height) = target_dimension
        (image_source_corner_size_width, image_source_corner_size_height) = image_corner_dimension

        if image_source_filename not in ScaledSurface.IMAGE_DICT.keys():
            ScaledSurface.IMAGE_DICT[image_source_filename] = pygame.image.load(image_source_filename).convert_alpha()

        image_source = ScaledSurface.IMAGE_DICT[image_source_filename]
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        if use_max_width:
            top = bottom = image_source.get_rect().width - 2 * image_source_corner_size_width
        if use_max_height:
            right = left = image_source.get_rect().height - 2 * image_source_corner_size_height

        # Fill the surface
        surface.fill(image_source.get_at(image_source.get_rect().center),
                     rect=pygame.Rect(image_source_corner_size_width,
                                      image_source_corner_size_height,
                                      width - 2 * image_source_corner_size_width,
                                      height - 2 * image_source_corner_size_height))
        # Fill the corners
        surface.blit(image_source, (0, 0, 1, 1),
                     area=((0, 0),
                           (image_source_corner_size_width, image_source_corner_size_height)))
        surface.blit(image_source, (0, height - image_source_corner_size_height, 1, 1),
                     area=((0, image_source.get_rect().height - image_source_corner_size_height),
                           (image_source_corner_size_width, image_source_corner_size_height)))
        surface.blit(image_source, (width - image_source_corner_size_width, 0, 1, 1),
                     area=((image_source.get_rect().width - image_source_corner_size_width, 0),
                           (image_source_corner_size_width, image_source_corner_size_height)))
        surface.blit(image_source, (width - image_source_corner_size_width,
                                    height - image_source_corner_size_height, 1, 1),
                     area=((image_source.get_rect().width - image_source_corner_size_width,
                            image_source.get_rect().height - image_source_corner_size_height),
                           (image_source_corner_size_width, image_source_corner_size_height)))

        # Finish with the border
        top_extract = image_source.subsurface(image_source_corner_size_width, 0,
                                              top, image_source_corner_size_height)
        number_fill_top = int((width - image_source_corner_size_width * 2) / top)
        rest_fill_top = (width - image_source_corner_size_width * 2) % top
        for x_index in range(number_fill_top):
            surface.blit(top_extract, (x_index * top + image_source_corner_size_width, 0, 1, 1))
        rest_extract = image_source.subsurface(image_source_corner_size_width, 0,
                                               rest_fill_top, image_source_corner_size_height)
        surface.blit(rest_extract, (width - image_source_corner_size_width - rest_fill_top, 0, 1, 1))

        bottom_extract = image_source.subsurface(image_source_corner_size_width,
                                                 image_source.get_rect().height -
                                                 image_source_corner_size_height,
                                                 bottom, image_source_corner_size_height)
        number_fill_bottom = int((width - image_source_corner_size_width * 2) / bottom)
        rest_fill_bottom = (width - image_source_corner_size_width * 2) % bottom
        for x_index in range(number_fill_bottom):
            surface.blit(bottom_extract, (x_index * bottom + image_source_corner_size_width,
                                          height - image_source_corner_size_height, 1, 1))
        rest_extract = image_source.subsurface(image_source_corner_size_width,
                                               image_source.get_rect().height - image_source_corner_size_height,
                                               rest_fill_bottom, image_source_corner_size_height)
        surface.blit(rest_extract, (width - image_source_corner_size_width - rest_fill_bottom,
                                    height - image_source_corner_size_height, 1, 1))

        left_extract = image_source.subsurface(0, image_source_corner_size_height,
                                               image_source_corner_size_width, left)
        number_fill_left = int((height - image_source_corner_size_height * 2) / left)
        rest_fill_left = (height - image_source_corner_size_height * 2) % left
        for y_index in range(number_fill_left):
            surface.blit(left_extract, (0, y_index * left + image_source_corner_size_height, 1, 1))
        rest_extract = image_source.subsurface(0, image_source_corner_size_height,
                                               image_source_corner_size_width, rest_fill_left)
        surface.blit(rest_extract, (0, height - image_source_corner_size_height - rest_fill_left, 1, 1))

        right_extract = image_source.subsurface(image_source.get_rect().width -
                                                image_source_corner_size_width,
                                                image_source_corner_size_height,
                                                image_source_corner_size_width,
                                                right)
        number_fill_right = int((height - image_source_corner_size_height * 2) / right)
        rest_fill_right = (height - image_source_corner_size_height * 2) % right
        for y_index in range(number_fill_right):
            surface.blit(right_extract,
                         (width - image_source_corner_size_width,
                          y_index * right + image_source_corner_size_height, 1, 1))
        rest_extract = image_source.subsurface(image_source.get_rect().width - image_source_corner_size_width,
                                               image_source_corner_size_height,
                                               image_source_corner_size_width,
                                               rest_fill_right)
        surface.blit(rest_extract, (width - image_source_corner_size_width,
                                    height - image_source_corner_size_height - rest_fill_right, 1, 1))
        return surface


class IncludedSurface:
    """
    Utility class to create a border effect by putting several images one into another.
    """

    @staticmethod
    def render(target_dimension, list_image, list_corner_tuples=None, list_internal_margin=None):
        """

        :param target_dimension: a tuple (width, height) for the target image
        :param list_image: list of filenames (including folder) for the image
        :param list_corner_tuples: list of tuples describing the corner size of the image - default (10, 10)
        :param list_internal_margin: list of tuples (left, top, right, bottom) describing which part of the image
        is copied over.
        :return: a surface with the correct background
        """
        (width, height) = target_dimension

        if list_corner_tuples:
            surface = ScaledSurface.render((width, height), list_image[0], list_corner_tuples[0])
        else:
            surface = ScaledSurface.render((width, height), list_image[0])

        current_top_pos = (0, 0)
        current_size = (width, height)
        new_surface = None

        for x in range(1, len(list_image)):
            if list_internal_margin:
                current_size = (current_size[0] - list_internal_margin[x - 1][0] - list_internal_margin[x - 1][2],
                                current_size[1] - list_internal_margin[x - 1][1] - list_internal_margin[x - 1][3])
                current_top_pos = (current_top_pos[0] + list_internal_margin[x - 1][0],
                                   current_top_pos[0] + list_internal_margin[x - 1][1])
            else:
                # assume internal_margin of 10
                current_size = (current_size[0] - 20, current_size[1] - 20)
                current_top_pos = (current_top_pos[0] + 10, current_top_pos[0] + 10)
            if list_corner_tuples:
                new_surface = ScaledSurface.render(current_size, list_image[x], list_corner_tuples[x])
            else:
                new_surface = ScaledSurface.render(current_size, list_image[x])
            surface.blit(new_surface, (current_top_pos[0], current_top_pos[1]))
        return surface


class ImagePlane(Plane):
    def __init__(self,
                 name,
                 rect,
                 tile_size,
                 image_size=None,
                 draggable=False,
                 grab=False,
                 highlight=False,
                 left_click_callback=None,
                 right_click_callback=None,
                 up_click_callback=None,
                 down_click_callback=None,
                 dropped_upon_callback=None):

        if not image_size:
            image_size = rect.size
            self.image_size = rect.size
        else:
            rect.size = image_size
        super().__init__(name, rect, draggable=draggable, grab=grab,
                         highlight=highlight, left_click_callback=left_click_callback,
                         right_click_callback=right_click_callback, up_click_callback=up_click_callback,
                         down_click_callback=down_click_callback, dropped_upon_callback=dropped_upon_callback)
        self.camera_rect = None
        self.image_size = image_size
        self.tile_size = tile_size

    def set_camera(self, camera_size, camera_center=None, camera_top_left=(0, 0)):
        self.camera_rect = pygame.Rect(camera_top_left, camera_size)
        self.rendersurface = pygame.Surface(camera_size)
        if camera_center:
            self.camera_rect.center = camera_center

    def move_camera_tile_center(self, new_center):
        self.camera_rect.center = (new_center[0] * self.tile_size[0], new_center[1] * self.tile_size[1])
        self.move_camera()  # To adjust to the borders...

    def move_camera(self, x=0, y=0):
        move_x = x * self.tile_size[0]
        move_y = y * self.tile_size[1]

        # print("Width: {} Height: {} Camera: Top {}/ Left {} Bottom {} Right {}".format(
        # self.image_size[0], self.image_size[1],
        # self.camera_rect.top, self.camera_rect.left, self.camera_rect.bottom, self.camera_rect.right))

        self.camera_rect.move_ip(move_x, move_y)
        if self.camera_rect.left < 0:
            self.camera_rect.left = 0
        if self.camera_rect.top < 0:
            self.camera_rect.top = 0
        if self.camera_rect.right >= self.image_size[0]:
            self.camera_rect.right = self.image_size[0]
        if self.camera_rect.bottom >= self.image_size[1]:
            self.camera_rect.bottom = self.image_size[1]

    def render(self, displayrect=None):
        if self.camera_rect:
            self.rendersurface.blit(self.image, (0, 0), area=self.camera_rect)
        self.last_image_id = id(self.image)

        for subplane in (self.subplanes[name] for name in self.subplanes_list):
            self.rendersurface.blit(subplane.rendersurface, subplane.rect)
        return True

    def clicked(self, button_name, event=None):
        (camera_top_x, camera_top_y) = self.camera_rect.topleft
        camera_top_x = camera_top_x // Constants.TILE_SIZE[0]
        camera_top_y = camera_top_y // Constants.TILE_SIZE[1]
        (pos_x, pos_y) = event.pos
        pos_x = pos_x // Constants.TILE_SIZE[0] + camera_top_x
        pos_y = pos_y // Constants.TILE_SIZE[1] + camera_top_y
        # print("click at {}x{}! ".format(pos_x, pos_y))
        print(GameData.current_town.tile_map.map[(pos_x, pos_y)])


# Some container styles
KENNEY_CONTAINER_STYLE_INCLUDED = KenneyContainerStyle(color=Constants.KENNEY_COLOR_GREY,
                                                       background_color=Constants.KENNEY_COLOR_BEIGE,
                                                       single_last_widget_group=True,
                                                       margin_left=15,
                                                       margin_top=15,
                                                       margin_bottom=15,
                                                       margin_right=15)

KENNEY_CONTAINER_STYLE_SCALED = KenneyContainerStyle(color=Constants.KENNEY_COLOR_GREY)

# Some widget styles
KENNEY_WIDGET_STYLE_BLUE = KenneyWidgetStyle(color=Constants.KENNEY_COLOR_BLUE, font="dolphin")
KENNEY_WIDGET_STYLE_BROWN = KenneyWidgetStyle(color=Constants.KENNEY_COLOR_BROWN, font="dolphin")

# Default
Constants.DEFAULT_WIDGET_STYLE = KENNEY_WIDGET_STYLE_BLUE
Constants.DEFAULT_CONTAINER_STYLE = KENNEY_CONTAINER_STYLE_INCLUDED
