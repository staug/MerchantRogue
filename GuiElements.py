import Constants
from planes import Plane

__author__ = 'Tangil'

import planes
import planes.gui
import pygame


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

        def __init__(self, number, lineheight, good_quantity = None):
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


    def __init__(self, name, text, goods, callback, quantity=None, width = 300, lineheight = 16, background_color = None, price_modifier = None):
        """Initialise the OptionSelector.
           option_list is a list of strings to be displayed as options.
           callback is a function to be called with the selected Option instance
           as argument once the selection is made.
        """

        # Call base class init
        #
        planes.gui.Container.__init__(self,
                           name,
                           padding = 5,
                           background_color = background_color)

        # TODO: copied from Button.__init__. Maybe inherit from a third class 'Callback'?
        #
        self.callback = callback

        # Add options and OK button
        #
        goodlist = []
        for good in goods:
            goodlist.append(good.name + " " + str(good.regular_value)+ " " + str(price_modifier[good.name]))
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
        ol.rect.left=0
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

    def __init__(self,
                 margin_top=10,
                 margin_left=10,
                 margin_bottom=10,
                 margin_right=10,
                 color=None,
                 background_color=None,
                 single_last_widget=False,
                 padding_v=5,
                 padding_h=5
                 ):
        """
        Basic style for all specific containers
        :param margin_top: the container top margin (impacts sub container placement). Default 10.
        :param margin_left: the container left margin (impacts sub container placement). Default 10.
        :param margin_bottom: the container bottom margin (impacts sub container placement). Default 10.
        :param margin_right: the container right margin (impacts sub container placement). Default 10.
        :param color: the color of teh foreground
        :param background_color: the color of the background. If provided, an included surface will be drawn
        :param single_last_widget: make specific room for the last widget
        :param padding_v: the vertical padding between widgets
        :param padding_h: the horizontal padding between widgets
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
        self.single_last_widget = single_last_widget


# Default container styles
KENNEY_CONTAINER_STYLE_INCLUDED = KenneyContainerStyle(
    color=Constants.KENNEY_COLOR_BEIGE_LIGHT,
    background_color=Constants.KENNEY_COLOR_BEIGE,
    single_last_widget=True)

KENNEY_CONTAINER_STYLE_SCALED = KenneyContainerStyle(
    color=Constants.KENNEY_COLOR_BEIGE_LIGHT)

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

    def __init__(self, name, kenney_style, preferred_size=(0, 0)):
        """Initialise.
           style is an instance of kenney style, which should hold the image name as well as the
           default margins & paddings...
        """
        # Call base
        planes.gui.Container.__init__(self, name, kenney_style.padding_v)
        # save main arguments
        self.style = kenney_style
        self.background = None
        self.preferred_size = preferred_size

        self.draggable = True
        self.grab = False
        self.subplanes_alignment = {}  # tuple (h_align, v_align) to remember the alignment of each.

        return

    def _resize(self):
        # Todo: the plane is stacked vertically by default. Plan for an optional grid arrangement.
        margin_top = self.style.margin_top # this is the height of the top part
        margin_bottom = self.style.margin_bottom # this is the height of the bottom part
        margin_left = self.style.margin_left   # this is the height of the bottom part
        margin_right = self.style.margin_right  # this is the height of the bottom part

        # Mandatory fit new height, observe padding
        max_width = self.preferred_size[0]
        max_height = 0

        for a_plane in self.subplanes.values():
            (h_plane_align, v_plane_align, fix_width, fix_height, stack_horizontal) = self.subplanes_alignment[a_plane.name]
            if fix_width and fix_width > max_width:
                max_width = fix_width
            elif a_plane.rect.width > max_width:
                max_width = a_plane.rect.width
            if a_plane.rect.height > max_height:
                max_height = a_plane.rect.height

        ypos = margin_top

        for name in self.subplanes_list:
            (h_plane_align, v_plane_align, fix_width, fix_height, stack_horizontal) = self.subplanes_alignment[name]
            required_height = max_height
            if fix_height:
                required_height = fix_height
            if v_plane_align == KenneyContainer.V_ALIGN_MIDDLE:
                self.subplanes[name].rect.centery = ypos + int(required_height / 2)
            elif v_plane_align == KenneyContainer.V_ALIGN_TOP:
                self.subplanes[name].rect.top = ypos
            elif v_plane_align == KenneyContainer.V_ALIGN_BOTTOM:
                self.subplanes[name].rect.bottom = ypos + required_height

            ypos += (required_height + self.style.padding_v)

            if h_plane_align == KenneyContainer.H_ALIGN_CENTER:
                self.subplanes[name].rect.centerx = margin_left + int(max_width / 2)
            elif h_plane_align == KenneyContainer.H_ALIGN_LEFT:
                self.subplanes[name].rect.left = margin_left
            elif h_plane_align == KenneyContainer.H_ALIGN_RIGHT:
                self.subplanes[name].rect.right = margin_right

        self.rect.height = max(
            self.preferred_size[1],
            ypos + margin_bottom)
        self.rect.width = max_width + margin_right + margin_left

    def render_background(self):
        if self.style.is_included:
            list_image = [Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_" + self.style.background_color + ".png",
                          Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_" + self.style.color + ".png"]
            if self.style.single_last_widget and len(self.subplanes) > 0:
                last_widget_height = self.subplanes[self.subplanes_list[len(self.subplanes) - 1]].rect.height
                bottom_margin = last_widget_height+ self.style.padding_v + self.style.margin_bottom
                internal_margin = [[10, 10, 10, bottom_margin + 10]]
                self.rect.height += 10
                self.subplanes[self.subplanes_list[len(self.subplanes) - 1]].rect.top += 10
                self.background = IncludedSurface.render(self.rect.size, list_image, list_internal_margin=internal_margin)
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

    def remove(self, plane_identifier, resize_background=True):
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
        self._resize()
        if resize_background:
            self.render_background()

        self.redraw()
        return



class KenneyOKLabel(KenneyContainer, planes.gui.OkBox):
    """
    Container: A box which displays a message and an LMR OK button over a TMB background.
    It is destroyed when OK is clicked.
    The message will be wrapped at newline characters.
    """

    def __init__(self, message, style=None, button_style=None):
        """
        Initialise.
           style is an optional instance of TMBStyle. If no style is given, it
           defaults to KENNEY_CONTAINER_STYLE_INCLUDED
           button_style is an optional instance of WidgetStyle.
        """
        if not style:
            style = KENNEY_CONTAINER_STYLE_INCLUDED

        KenneyContainer.__init__(self, str(id(self)), style, preferred_size=(10, 20))

        # Adapted from planes.gui.OkBox
        lines = message.split("\n")

        for line_no in range(len(lines)):
            self.sub(planes.gui.Label("message_line_{0}".format(line_no),
                                      lines[line_no],
                                      pygame.Rect((0, 0),
                                                  (len(lines[line_no]) * planes.gui.PIX_PER_CHAR, 20)),
                                      background_color=(128, 128, 128, 0)), fix_height=20)

        # Use default style
        self.sub(planes.gui.lmr.LMRButton("OK", 20, self.ok))

        return


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
                 draggable = False,
                 grab = False,
                 highlight = False,
                 left_click_callback = None,
                 right_click_callback = None,
                 up_click_callback = None,
                 down_click_callback = None,
                 dropped_upon_callback = None):

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

    def set_camera(self, camera_size, camera_center=None, camera_top_left=(0,0)):
        self.camera_rect = pygame.Rect(camera_top_left, camera_size)
        self.rendersurface = pygame.Surface(camera_size)
        if camera_center:
            self.camera_rect.center = camera_center

    def move_camera_tile_center(self, new_center):
        self.camera_rect.center = (new_center[0] * self.tile_size[0], new_center[1] * self.tile_size[1])
        self.move_camera() # To adjust to the borders...

    def move_camera(self, x=0, y=0):
        move_x = x * self.tile_size[0]
        move_y = y * self.tile_size[1]

        # print("Width: {} Height: {} Camera: Top {}/ Left {} Bottom {} Right {}".format(
        #     self.image_size[0], self.image_size[1],
        #     self.camera_rect.top, self.camera_rect.left, self.camera_rect.bottom, self.camera_rect.right))

        self.camera_rect.move_ip(move_x, move_y)
        if self.camera_rect.left < 0:
            self.camera_rect.left = 0
        if self.camera_rect.top < 0:
            self.camera_rect.top = 0
        if self.camera_rect.right >= self.image_size[0]:
            self.camera_rect.right = self.image_size[0]
        if self.camera_rect.bottom >= self.image_size[1]:
            self.camera_rect.bottom = self.image_size[1]

    def render(self, displayrect = None):
        if self.camera_rect:
            self.rendersurface.blit(self.image, (0,0), area=self.camera_rect)
        self.last_image_id = id(self.image)

        for subplane in (self.subplanes[name] for name in self.subplanes_list):
            self.rendersurface.blit(subplane.rendersurface, subplane.rect)
        return True

    def clicked(self, button_name, event=None):
        print("click! " + str(event))