"""planes
   A Hierarchical Surface Framework for PyGame
   Copyright 2010-2013 by Florian Berger <fberger@florian-berger.de>
"""

# This file is part of planes.
#
# planes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# planes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with planes.  If not, see <http://www.gnu.org/licenses/>.

# Planned in mind at the Mosel valley in late July 2010
# Actual work started on 01. Oct 2010

# TODO: add Plane.offset(x, y) to offset all subplanes - without touching their rect -> only while rendering
# TODO: Surface.get_flags has all sorts of interesting information to optimise performance.
# TODO: Planes *so* needs live performance reporting. Maybe not via log file, but as some sort of a live display via TTY or socket.
# TODO: replace Plane.subplanes and Planes.subplanes_list with collections.OrderedDict and OrderedDict.keys()?

import time
import random

import pygame


VERSION = "0.6.1a"

class Plane:
    """A Plane is a surface in a hierarchy of surfaces.
       Concept-wise it bears some similarities to pygame.sprite.Sprite.

       Planes are currently not thread safe! Accessing a Plane from several
       threads may produce unexpected results and errors.

       Attributes:

       Plane.name
           Name of the plane.

       Plane.image
           The pygame.Surface for this Plane.

       Plane.rendersurface
           A pygame.Surface displaying the composite of this plane and all
           subplanes.

       Plane.rect
           The render position of this Plane on the parent Plane.

       Plane.parent
           The parent plane. Initially None.

       Plane.subplanes
           Dict of subplanes, identified by their name.

       Plane.subplanes_list
           A list of subplane names, in order of their addition

       Plane.draggable
           Boolean flag. If True, this Plane can be dragged and dropped.

       Plane.grab
           Boolean flag. If True, this Plane will remove dropped Planes from
           their parent Plane and make it a subplane of this one.
           Handled in Plane.dropped_upon()

       Plane.highlight
           Boolean flag. If True, the Plane be highlighted when the mouse cursor
           moves over it.

       Plane.last_image_id
           Caches object id of the image at last rendering for efficiency.

       Plane.last_rect
           Caches rect at last rendering for efficiency.

       Plane.left_click_callback
           Callback function when this plane has been clicked with the left
           mouse button.

       Plane.right_click_callback
           Callback function when this plane has been clicked with the right
           mouse button.

       Plane.up_click_callback
           Callback function when the mouse wheel has been moved up above this
           Plane.

       Plane.down_click_callback
           Callback function when the mouse wheel has been moved down above this
           Plane.

       Plane.dropped_upon_callback
           Callback function when a plane has been dropped upon this plane.

       Plane.mouseover_callback
           Callback function when the mouse cursor moves over this plane.

       Plane.mouseout_callback
           Callback function when the mouse cursor has left this plane.

       Plane.mouseover
           Flag indicating whether the mouse cursor is over this Plane.
           Initially False.

       Plane.sync_master_plane
          A Plane that this Plane's position will sync to. Initally None.

       Plane.offset
          A tuple (x, y) describing the offset to the sync master plane.
          Initially None.
    """

    # TODO: it should be possible to initialise a Plane with a Pygame Surface, for convenvience.
    #
    def __init__(self,
                 name,
                 rect,
                 draggable = False,
                 grab = False,
                 highlight = False,
                 left_click_callback = None,
                 right_click_callback = None,
                 up_click_callback = None,
                 down_click_callback = None,
                 dropped_upon_callback = None):
        """Initialize the Plane.
           name is the name of the plane which can also be used
           as an attribute.
           rect is an instance of pygame.Rect giving width, height
           and render position.
           draggable is a flag indicating whether this plane can be dragged.
           grab is a flag indicating whether other planes can be dropped
           on this one.
           clicked_callback and dropped_upon_callback, if given, must be
           functions.
           Planes are filled with solid black color by default.
        """

        self.name = name

        # We do not use the SRCALPHA flag because it considerably slows down the
        # rendering. If an application needs per-pixel alpha, it can always
        # substitute Plane.image with an RGBA Surface.
        #
        self.image = pygame.Surface(rect.size, flags = pygame.HWSURFACE)

        # Transparent by default, so let's paint it black
        #
        self.image.fill((0, 0, 0, 255))

        # Plane.image is the image of this very plane.
        # Plane.rendersurface is the composite of this
        # plane and all subplanes.
        # To save space, it is initalized to Plane.image.
        # A surface is only created when there are subsurfaces.
        #
        self.rendersurface = self.image

        # Rect is relative to the parent plane, not to the display!
        #
        self.rect = rect

        self.draggable = draggable
        self.grab = grab

        self.highlight = highlight
        self.mouseover = False

        # Parent stores the parent plane.
        # Upon creation, there is none.
        #
        self.parent = None

        self.subplanes = {}
        self.subplanes_list = []

        # Caches for efficient rendering
        #
        self.last_image_id = id(self.image)

        # Initialize to None to trigger a rendering
        #
        self.last_rect = None

        # Save callbacks
        #
        self.left_click_callback = left_click_callback
        self.right_click_callback = right_click_callback
        self.up_click_callback = up_click_callback
        self.down_click_callback = down_click_callback
        self.dropped_upon_callback = dropped_upon_callback

        # Master plane for synchronous movements
        #
        self.sync_master_plane = None
        self.offset = None

        return

    def sub(self, plane, insert_after = None):
        """Remove the Plane given from its current parent and add it as a subplane of this Plane.

           If insert_after is given, the new subplane will be inserted
           immediately after the subplane with that name in Plane.subplanes_list,
           else it will simply be appended.

           If a subplane with the same name already exists, it is silently
           replaced by the new plane.
        """

        if plane.parent is not None:

            plane.parent.remove(plane.name)

        if plane.name in self.subplanes_list:

            del self.subplanes_list[self.subplanes_list.index(plane.name)]

        if insert_after is not None and insert_after in self.subplanes_list:

            self.subplanes_list.insert(self.subplanes_list.index(insert_after) + 1,
                                       plane.name)

        else:
            self.subplanes_list.append(plane.name)

        self.subplanes[plane.name] = plane

        plane.parent = self

        # Reset to None to trigger a rendering
        #
        plane.last_rect = None

        # Now that there is a subplane, make clear that the rendersurface no
        # longer equals the image.
        #
        if self.rendersurface == self.image:

            # We do not create a Surface here since render() will create a new
            # one from Plane.image anyway, so we would just waste memory.
            #
            self.rendersurface = None

        return

    def remove(self, plane_identifier):
        """Remove subplane by name or Plane instance.
        """

        # Accept Plane name as well as Plane instance
        #
        if isinstance(plane_identifier, Plane):

            name = plane_identifier.name

        else:
            name = plane_identifier

        if name in self.subplanes_list:
            self.subplanes[name].parent = None
            del self.subplanes[name]
            del self.subplanes_list[self.subplanes_list.index(name)]

        # If there are still subplanes, then trigger a redraw of all of them
        # by setting their last_rect to None.
        #
        for plane in self.subplanes.values():

            plane.last_rect = None

        return

    def remove_all(self):
        """Convenience method to call Plane.remove() for all subplanes.
        """

        # Make a copy since subplanes_list will be changed by remove()
        #
        for name in list(self.subplanes_list):

            self.remove(name)

        # We do not need to worry about rendering here: once all subplanes
        # are gone, render() will point the rendersurface to image and
        # redraw.

        return

    def __getattr__(self, name):
        """Access subplanes as attributes.
        """

        # The Python interpreter has already checked instance and class
        # attributes. If this fails, an appropriate KeyError will be raised.
        #
        return self.subplanes[name]

    def render(self, displayrect = None):
        """Draw a composite surface of this plane and all subplanes, in order of their addition.

           displayrect is the Rect of the Display, displaced relatively to this
           Plane's Rect, so collision of subplanes can be tested using
           Rect.colliderect(displayrect).

           Returns True if anything has been rendered (i.e. when
           Plane.rendersurface has changed), False otherwise.

           This method will highlight subplanes that have the Plane.mousover
           flag set.
        """

        # We only need to render if self.rendersurface does not point
        # to self.image.
        #
        if self.rendersurface is self.image and id(self.image) == self.last_image_id:

            STATS.unchanged_planes += 1

            STATS.total_pixels += self.rect.width * self.rect.height

            return False

        # Still here? Then it does not. But is this correct? Maybe the user has
        # updated the image, but when there are no subplanes, there is no need
        # to render.
        #
        if not self.subplanes:

            # Fix the pointer
            #
            self.rendersurface = self.image

            # Fix cached id
            #
            self.last_image_id = id(self.image)

            STATS.total_pixels += self.rect.width * self.rect.height

            return True

        # At this point, we know that rendersurface differs from image and that
        # there are subplanes.

        STATS.total_pixels += self.rect.width * self.rect.height * 2

        # If the image of this plane or any subplane has changed or if a
        # subplane has moved: redraw everything.
        #
        # (The alternative would be to check for rect collisions to see where
        # the background can be restored by using image, or caching inbetween
        # rendering steps).
        #
        # TODO: This doesn't catch draw and blit operations outside render()!
        #
        subplane_changed = False

        if displayrect is None:

            # That means we are the Display and are just starting the rendering
            # cascade.
            #
            displayrect = self.rect

        for plane in (self.subplanes[name] for name in self.subplanes_list):

            # Only render if actually intersecting with Display
            # TODO: bookkeeping: count rendered Planes
            #
            if plane.rect.colliderect(displayrect):

                displayrect_to_pass = displayrect.move(- plane.rect.left,
                                                       - plane.rect.top)

                if plane.render(displayrect_to_pass):

                    subplane_changed = True

                elif plane.rect != plane.last_rect:

                    subplane_changed = True

                    # We need a copy!
                    #
                    plane.last_rect = pygame.Rect(plane.rect)

            else:

                STATS.render_skip += 1

        if id(self.image) != self.last_image_id or subplane_changed:

            # Instead of clearing an existing Surface, we copy Plane.image. This
            # is a little slower but has the huge benefit of creating an RGBA
            # Surface with per pixel alpha when needed.
            #
            self.rendersurface = self.image.copy()

            # Subplanes are already rendered. Force-blit them in order.
            # Obey mouseover flag.
            #
            surface = None

            for subplane in (self.subplanes[name] for name in self.subplanes_list):

                # Again, only blit if actually intersecting with Display
                # TODO: bookkeeping: count rendered and not rendered Planes
                #
                if subplane.rect.colliderect(displayrect):

                    # First blit ordinary rendersurface
                    #
                    self.rendersurface.blit(subplane.rendersurface,
                                            subplane.rect)

                    # Add a highlight on top if mouseover is set
                    #
                    if subplane.mouseover:

                        overlay = subplane.rendersurface.copy()

                        # Only premultiply Surfaces with the SRCALPHA flag, will
                        # raise an exception otherwise.
                        #
                        if overlay.get_flags() & 0x00010000:

                            # Premultiply alpha channel to RGB. Otherwise
                            # invisible RGB values will be added by BLEND_ADD.
                            # Technique suggested by Rene Dudfield
                            # <renesd@gmail.com> on pygame-users@seul.org
                            # on 19 Dec 2011
                            #
                            overlay = pygame.image.fromstring(pygame.image.tostring(overlay,
                                                                                    "RGBA_PREMULT"),
                                                              overlay.get_size(),
                                                              "RGBA")

                        overlay.blit(overlay, (0, 0), special_flags = pygame.BLEND_MULT)
                        overlay.blit(overlay, (0, 0), special_flags = pygame.BLEND_MULT)

                        self.rendersurface.blit(overlay,
                                                subplane.rect,
                                                special_flags = pygame.BLEND_ADD)

                else:

                    STATS.blit_skip += 1

            self.last_image_id = id(self.image)

            return True

        else:

            STATS.unchanged_planes += 1

            return False

    def get_plane_at(self, coordinates):
        """Return the (sub)plane and the succeeding parent coordinates at the given coordinates.
           Subplanes are tested in reverse order of their addition (i.e. latest first).
        """

        # It's probaly me.
        #
        return_plane = self
        return_coordinates = coordinates

        for name in self.subplanes_list:

            plane = self.subplanes[name]

            if plane.rect.collidepoint(coordinates):

                return_coordinates = (coordinates[0] - plane.rect.left, coordinates[1] - plane.rect.top)

                return_plane, return_coordinates = plane.get_plane_at(return_coordinates)

        return (return_plane, return_coordinates)

    def update(self):
        """Update hook.
           The default implementation calls update() on all subplanes. If
           Plane.sync_master_plane is not None, the position of this Plane will
           be synced to that of the master Plane, using Plane.offset.
           Compare pygame.sprite.Sprite.update.
        """

        # update() will be called for all planes.
        #
        STATS.total_planes += 1

        # Subplanes may be destroyed in update(). So, create a list copy in case
        # self.subplanes changes during iteration.
        #
        for plane in list(self.subplanes.values()):

            plane.update()

        if self.sync_master_plane is not None:

            self.rect.center = (self.sync_master_plane.rect.centerx + self.offset[0],
                                self.sync_master_plane.rect.centery + self.offset[1])

        return

    def clicked(self, button_name):
        """Called when there is a MOUSEDOWN event on this plane.
           If click callbacks are set, the appropriate one is called with this
           Plane as argument.
        """

        if button_name == "left" and self.left_click_callback is not None:

            self.left_click_callback(self)

        elif button_name == "right" and self.right_click_callback is not None:

            self.right_click_callback(self)

        elif button_name == "up" and self.up_click_callback is not None:

            self.up_click_callback(self)

        elif button_name == "down" and self.down_click_callback is not None:

            self.down_click_callback(self)

        return

    def dropped_upon(self, plane, coordinates):
        """If a plane is dropped on top of this one, call dropped_upon_callback() and conditionally grab it.

           If Plane.grab is True, the default implementation will remove the
           dropped Plane from its parent and make it a subplane of this one.

           If the dropped Plane is already a subplane of this one, its position
           is updated.

           If Plane.dropped_upon_callback is set, it is called with
           Plane.dropped_upon_callback(self, plane, coordinates)
        """

        if self.grab:

            plane.rect.center = coordinates

            if plane.name not in self.subplanes_list:

                plane.parent.remove(plane.name)

                self.sub(plane)

        if self.dropped_upon_callback is not None:
            self.dropped_upon_callback(self, plane, coordinates)

        return

    def destroy(self):
        """Remove this Plane from the parent plane, remove all subplanes and delete all pygame Surfaces.
        """

        if self.parent is not None:

            self.parent.remove(self.name)

        self.remove_all()

        self.image = self.rendersurface = None
        self.rect = self.draggable =  self.grab = None

        self.unsync()

        return

    def sync(self, master_plane):
        """Save the Plane given as master Plane and the position offset to that Plane for position synchronisation in Plane.update().
        """

        self.sync_master_plane = master_plane

        # Using the offset between the centers of the Planes
        #
        self.offset = (self.rect.centerx - master_plane.rect.centerx,
                       self.rect.centery - master_plane.rect.centery)

        return

    def unsync(self):
        """Remove the position synchronisation to the sync master Plane.
        """

        self.sync_master_plane = self.offset = None

        return

    def mouseover_callback(self):
        """Callback function when the mouse cursor moves over this plane.
           The default implementation sets Plan.mouseover to True when
           Plane.highlight is set.
        """

        if self.highlight:

            self.mouseover = True

            # Set to None to trigger a rendering
            #
            self.last_rect = None

        return

    def mouseout_callback(self):
        """Callback function when the mouse cursor has left this plane.
           The default implementation sets Plan.mouseover to False.
        """

        # Not checking self.highlight here - it might have changed

        self.mouseover = False

        # Set to None to trigger a rendering
        #
        self.last_rect = None

        return

    def random_name(self):
        """Return a random string that is not in Plane.subplanes_list.
           This is a convenience function to produce names for subplanes.
        """

        name = None

        while name is None or name in self.subplanes_list:

            name = "subplane{0}".format(str(random.randint(0, 99999)))

        return name

    def __repr__(self):
        """Readable string representation.
        """

        parent_name = "None"

        if self.parent is not None:
            parent_name = self.parent.name


        repr_str = "<planes.Plane name='{0}' image={1} rendersurface={2} rect={3} parent='{4}' subplanes_list={5} draggable={6} grab={7} last_image_id={8} last_rect={9} left_click_callback={10} right_click_callback={11} dropped_upon_callback={12} sync_master_plane={13}>"

        return repr_str.format(self.name,
                               "{0}@{1}".format(self.image, id(self.image)),
                               "{0}@{1}".format(self.rendersurface, id(self.rendersurface)),
                               self.rect,
                               parent_name,
                               self.subplanes_list,
                               self.draggable,
                               self.grab,
                               self.last_image_id,
                               self.last_rect,
                               self.left_click_callback,
                               self.right_click_callback,
                               self.dropped_upon_callback,
                               self.sync_master_plane)

class Display(Plane):
    """planes main screen class.
       A Display instance serves as the root Plane in planes.

       Additional attributes:

       Display.display
           The Pygame display Surface

       Display.dragged_plane
           The currently dragged plane

       Display.key_sensitive_plane
           The Plane to be notified of Pygame keyboard events. Initially None.

       Display.last_mouseover_plane
           The last Plane a mouseover condition was found for. Initially None.

       Display.mouse_buttons
           A dict mapping Pygame mouse button numbers to description strings.

       Display.show_stats
           Boolean flag to indicate whether to display performance statistics.
           Set in Display.process() by examining user input. Initially False.

       Display.font
           A pygame.font.Font instance using the system default font.
    """

    def __init__(self, resolution_tuple, fullscreen = False):
        """Calling pygame.display.set_mode().
           If fullscreen is True, the display will use the full screen.
        """

        # Init Pygame, just to be on the safe side.
        # pygame.init() can safely be called more than once.
        #
        pygame.init()

        flags = 0

        if fullscreen:

            flags = pygame.FULLSCREEN

        try:
            self.display = pygame.display.set_mode(resolution_tuple, flags)

        except pygame.error:

            # Microsoft Windows SDL error: "No available video device"
            # For a list see
            # http://www.libsdl.org/cgi/docwiki.cgi/SDL_envvars
            #
            import os

            os.environ['SDL_VIDEODRIVER'] = 'windib'

            self.display = pygame.display.set_mode(resolution_tuple, flags)

        Plane.__init__(self, "display", pygame.Rect((0, 0), resolution_tuple))

        self.draggable = False

        # Keep track of the dragged plane
        #
        self.dragged_plane = None

        self.key_sensitive_plane = None

        self.last_mouseover_plane = None

        self.mouse_buttons = {1: "left",
                              3: "right",
                              4: "up",
                              5: "down"}

        self.show_stats = False

        self.font = pygame.font.SysFont("Bitstream Vera Sans,DejaVu Sans,Verdana",
                                        14)

        # Convenience Surface for statistics display.
        # See Display.render()
        #
        self._stats_surface = pygame.Surface((320, 256))

        self._stats_surface.convert()

        # Make transparent. Currently has only a limited effect, since it might
        # be blitted over itself in render().
        #
        self._stats_surface.set_alpha(196, pygame.RLEACCEL)

        return

    def key_sensitive(self, plane):
        """Register the Plane given as sensitive to Pygame keyboard events.
           Display will call plane.keydown(KEYDOWN_event) when a key is
           pressed and the Plane has a parent.
           plane.activate() will be called when the plane is registered.
           plane.deactivate() will be called on the old plane.
        """

        # TODO: there should be a class containing keydown(), activate(), deactivate()

        if self.key_sensitive_plane:
            self.key_sensitive_plane.deactivate()

        self.key_sensitive_plane = plane

        self.key_sensitive_plane.activate()

        return

    def process(self, event_list):
        """Process a pygame event list.
           This is the main method of planes and should be called once per
           frame.
           It will also check mouseover conditions, even if event_list is empty.
        """

        # We will only process mouseovers when nothing else has happened.
        # So we set up a flag here.
        #
        nothing_happened = True

        for event in event_list:

            if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button in self.mouse_buttons.keys()):

                nothing_happened = False

                clicked_plane = self.get_plane_at(event.pos)[0]

                # Cant just compare to self in Python < 3.0.
                # Use id instead.
                #
                if id(clicked_plane) != id(self):

                    button_name = self.mouse_buttons[event.button]

                    # Notify plane instance
                    #
                    clicked_plane.clicked(button_name)

                    if button_name == "left" and clicked_plane.draggable:

                        # Use a copy for new coordinates etc.
                        #
                        self.dragged_plane = Plane("dragged_plane", clicked_plane.rect.copy())
                        self.dragged_plane.rendersurface = clicked_plane.rendersurface.copy()

                        # Keep original for reference
                        #
                        self.dragged_plane.source = clicked_plane

                        # 2/3 transparency
                        #
                        self.dragged_plane.rendersurface.set_alpha(170, pygame.RLEACCEL)

            elif (event.type == pygame.MOUSEBUTTONUP
                  and event.button == 1):

                # Left button == 1, right button == 3

                nothing_happened = False

                if self.dragged_plane is not None:

                    target_plane, coordinates = self.get_plane_at(event.pos)

                    # Don't drop to self
                    # Cant compare Planes in Python < 3.0.
                    # Use id instead.
                    #
                    if id(target_plane) != id(self.dragged_plane.source):

                        target_plane.dropped_upon(self.dragged_plane.source, coordinates)

                    self.dragged_plane = None

                    # Render without dragged Plane and force-blit to Pygame
                    # display
                    #
                    self.render(force = True)

            # Hardwire F12 key to stats display.
            # Catch it before forwarding keys to key_sensitive_plane.
            #
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_F12):

                # Reverse
                #
                if self.show_stats:

                    self.show_stats = False

                else:
                    self.show_stats = True

            elif (event.type == pygame.KEYDOWN
                  and self.key_sensitive_plane is not None
                  and self.key_sensitive_plane.parent is not None):

                nothing_happened = False

                # TODO: remove a destroyed Plane from key_sensitive_plane

                # Notify the latest registered listener
                #
                self.key_sensitive_plane.keydown(event)

        # All events have been processed now. If nothing happened, process
        # mouseover.
        #
        if nothing_happened:

            try:

                mouseover_plane = self.get_plane_at(pygame.mouse.get_pos())[0]

            except pygame.error:

                # This most probably means that Pygame has been shut down in the
                # meantime.
                #
                return

            if id(mouseover_plane) == id(self.last_mouseover_plane):

                # Still over it. No action.
                #
                pass

            else:

                if self.last_mouseover_plane is not None:

                    self.last_mouseover_plane.mouseout_callback()

                if id(mouseover_plane) == id(self):

                    # Ignore the Display
                    #
                    self.last_mouseover_plane = None

                else:

                    mouseover_plane.mouseover_callback()

                    self.last_mouseover_plane = mouseover_plane

        return

    def render(self, force = False):
        """Call base class render(), then blit to the Pygame display if something has changed.
           If force is True, blit to Pygame display regardless.
        """

        starttime = time.clock()

        rendered_something = Plane.render(self)

        STATS.log_render_time(time.clock() - starttime)

        if rendered_something or force or self.dragged_plane is not None:

            self.display.blit(self.rendersurface, (0, 0))

            if self.dragged_plane is not None:

                # For some reason MOUSEBUTTONUP is sometimes missed.
                # Check whether button is still pressed
                #
                if pygame.mouse.get_pressed() != (0, 0, 0):

                    # Dragged plane on top
                    #
                    self.dragged_plane.rect.center = pygame.mouse.get_pos()

                    self.display.blit(self.dragged_plane.rendersurface,
                                      self.dragged_plane.rect)

                else:
                    # Delete without dropping
                    #
                    self.dragged_plane = None

        if self.show_stats:

            # Font.render(text, antialias, color, background)

            antialias = True

            color = (255, 255, 255)

            background = (64, 64, 64)

            padding = 5

            lineheight = self.font.get_height() + padding

            self._stats_surface.fill(background)

            y = 3

            self._stats_surface.blit(self.font.render("planes {0} Runtime Statistics".format(VERSION),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Total planes: {0}".format(STATS.total_planes),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Total pixels: {0:.1f} M, {1:.2f} MB RGB video RAM".format(STATS.total_pixels / 1000000, STATS.total_pixels * 24 / 8 / 1024 / 1024),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Unchanged planes: {0}".format(STATS.unchanged_planes),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Rendering skipped: {0}".format(STATS.render_skip),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Blitting skipped: {0}".format(STATS.blit_skip),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Render time: {0:.1f} ms".format(STATS.render_time * 1000),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Mean render time: {0:.1f} ms".format(STATS.mean_render_time * 1000),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))

            y += lineheight

            self._stats_surface.blit(self.font.render("Mean rendering capacity: {0} renderings / s".format(STATS.renders_per_second),
                                                      antialias,
                                                      color,
                                                      background), (padding, y))


            self.display.blit(self._stats_surface, (10, 10))

            # Update and reset stats counter
            #
            STATS.update(self)

        return

class Stats:
    """A Stats instance stores and computes several runtime statistics.

       Attributes:

       Stats.total_planes
           Total number of planes.

       Stats.total_pixels
           Total number of pixels allocated for all planes.

       Stats.unchanged_planes
           Number of planes whose bitmap did not change in the last run.

       Stats.render_skip
           Number of planes for which rendering has been skipped because they
           are outside the screen.

       Stats.blit_skip
           Number of planes for which blitting has been skipped because they
           are outside the screen.

       Stats.render_time
           Time of last call to Display.render().

       Stats.mean_render_time
           Mean of the time of the last 30 calls to Display.render().

       Stats.renders_per_second
           Given Stats.mean_render_time, how many renders could be carried out
           in one second in theory. Note that this is not the actual FPS, which
           is largely determined by the application deploying the planes module.
    """

    # TODO: A Stats instance could be an iterator, yielding text Surfaces and rendering positions.

    def __init__(self):
        """Initialise.
        """

        self.total_planes = 0

        self.total_pixels = 0

        self.unchanged_planes = 0

        self.render_skip = 0

        self.blit_skip = 0

        self.render_time = 0

        self._render_time_list = []

        self.mean_render_time = 0

        self.renders_per_second = 0

        return

    def update(self, display):
        """Actively update stats from the display instance given, and reset frame-to-frame counters.
        """

        self.total_planes = 0

        self.total_pixels = 0

        self.unchanged_planes = 0

        self.render_skip = 0

        self.blit_skip = 0

        # self.render_time will be entirely handled from the outside and needs
        # no reset.

        if len(self._render_time_list):

            self.mean_render_time = sum(self._render_time_list) / len(self._render_time_list)

        if self.mean_render_time > 0:

            self.renders_per_second = int(1 / self.mean_render_time)

        return

    def log_render_time(self, render_time):
        """Set Stats.render_time to the time given, and register that time for computing the mean.
        """

        self. render_time = render_time

        self._render_time_list.append(render_time)

        # Keep it at 30 values
        #
        if len(self._render_time_list) > 30:

            self._render_time_list.pop(0)

        return

# As there will only ever be one Display instance, we can keep a global Stats
# instance and do not need to do it on a per-Display base.
#
STATS = Stats()

# --------------------------------------------------------------------------------------------
# Specific added modif go there!
# -------------------------------------------------------------------------------------------

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

    def clicked(self, button_name):
        print("click!")


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
    def build(target_dimension, list_image, list_corner_tuples=None, list_internal_margin=None):
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
            surface = ScaledSurface((width, height), list_image[0], list_corner_tuples[0]).surface
        else:
            surface = ScaledSurface((width, height), list_image[0]).surface

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
                new_surface = ScaledSurface(current_size, list_image[x], list_corner_tuples[x]).surface
            else:
                new_surface = ScaledSurface(current_size, list_image[x]).surface
            surface.blit(new_surface, (current_top_pos[0], current_top_pos[1]))
        return surface


import planes.gui
import Constants


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

    def __init__(self, name, preferred_size, kenney_style, padding_h=0, padding_v=0):
        """Initialise.
           style is an instance of kenney style, which should hold the image name as well as the
           default margins & paddings...
        """
        # Call base
        planes.gui.Container.__init__(self, name, padding_v)
        # save main arguments
        self.style = kenney_style
        self.background = None
        self.preferred_size = preferred_size

        # Initialise initial rect width. This may be changed later when adding new things in the container
        self.rect.width = preferred_size[0]
        self.rect.height = preferred_size[1]

        self.padding_h = padding_h
        self.padding_v = padding_v

        self.draggable = True
        self.grab = False
        self.subplanes_alignment = {}  # tuple (h_align, v_align) to remember the alignment of each.

        return

    def sub(self,
            plane,
            h_align=H_ALIGN_CENTER,
            v_align=V_ALIGN_MIDDLE):
        # TODO: this only resize the height as teh whidth is supposed to be fixed, needs to change that!
        # TODO WE ARE STACKING ALL VERTICALY HERE....
        """
        Resize the container, update the position of plane and add it as a subplane.
        This will also repaint TMBContainer.background.
        """

        # Adapted from gui.Container method

        # First add the subplane by calling the base class method.
        # This also cares for re-adding an already existing subplane.
        planes.Plane.sub(self, plane)
        self.subplanes_alignment[plane.name] = (h_align, v_align)
        # Existing subplanes are already incorporated in self.rect.
        # We need it a couple of times
        # TODO: make that dependent from Kenney Style instead!
        margin_top = 50  # this is the height of the top part
        margin_bottom = 10  # this is the height of the bottom part
        margin_left = 10  # this is the height of the bottom part
        margin_right = 10  # this is the height of the bottom part

        # Mandatory fit new height, observe padding
        max_width = max_height = 0
        for a_plane in self.subplanes.values():
            if a_plane.rect.width > max_width:
                max_width = a_plane.rect.width
            if a_plane.rect.height > max_height:
                max_height = a_plane.rect.height

        ypos = margin_top

        for name in self.subplanes_list:
            (h_plane_align, v_plane_align) = self.subplanes_alignment[name]

            if v_plane_align == KenneyContainer.V_ALIGN_MIDDLE:
                self.subplanes[name].rect.centery = ypos + int(max_height / 2)
            elif v_plane_align == KenneyContainer.V_ALIGN_TOP:
                self.subplanes[name].rect.top = ypos
            elif v_plane_align == KenneyContainer.V_ALIGN_BOTTOM:
                self.subplanes[name].rect.bottom = ypos + max_height
            ypos += (max_height + self.padding_v)

            if h_plane_align == KenneyContainer.H_ALIGN_CENTER:
                self.subplanes[name].rect.centerx = margin_left + int(max_width / 2)
            elif h_plane_align == KenneyContainer.H_ALIGN_LEFT:
                self.subplanes[name].rect.left = margin_left
            elif h_plane_align == KenneyContainer.H_ALIGN_RIGHT:
                self.subplanes[name].rect.right = margin_right

        self.rect.size = (max_width + margin_right + margin_left,
                          max_height * len(self.subplanes) + margin_top + margin_bottom)
        # Recreate background
        self.background = ScaledSurface.render(self.rect.size,
                                               Constants.KENNEY_IMAGE_RESOURCE_FOLDER + "panel_beige.png")
        self.redraw()

        return

    def redraw(self):
        """Redraw TMBContainer.image using TMBContainer.background.
           This also creates a new TMBContainer.rendersurface.
        """
        self.image = self.background.copy()
        self.rendersurface = self.image.copy()
        return

    def remove(self, plane_identifier):
        """Remove the subplane, then reposition remaining subplanes and resize the container.
        """

        # Adapted from gui.Container method

        # Accept Plane name as well as Plane instance
        #
        if isinstance(plane_identifier, planes.Plane):
            name = plane_identifier.name
        else:
            name = plane_identifier

        # Save the height of the removed plane
        height_removed = self.subplanes[name].rect.height + self.padding

        planes.Plane.remove(self, name)

        # Reposition remaining subplanes.
        #
        # TODO: make that dependent from Kenney Style instead!
        margin_top = 50  # this is the height of the top part
        margin_bottom = 10  # this is the height of the bottom part

        for name in self.subplanes_list:
            rect = self.subplanes[name].rect
            rect.top = margin_top
            margin_top = margin_top + rect.height + self.padding_v

        # Now shrink and redraw.
        #
        self.rect.height = self.rect.height - height_removed

        self.redraw()
        return


class KenneyLabel(KenneyContainer, planes.gui.OkBox):
    """A box which displays a message and an LMR OK button over a TMB background.
       It is destroyed when OK is clicked.
       The message will be wrapped at newline characters.
    """

    def __init__(self, message, style, button_style=None):
        """Initialise.

           style is an optional instance of TMBStyle. If no style is given, it
           defaults to C_256_STYLE.

           button_style is an optional instance of lmr.LMRStyle.
        """

        # Base class __init__()
        # We need a unique random name and just use this instance's id.
        # TODO: prefix with some letters to make it usable via attribute calls
        #
        KenneyContainer.__init__(self, str(id(self)), (120, 20), style, padding_v=5)

        # Adapted from planes.gui.OkBox
        #
        lines = message.split("\n")

        for line_no in range(len(lines)):
            self.sub(planes.gui.Label("message_line_{0}".format(line_no),
                                      lines[line_no],
                                      pygame.Rect((0, 0),
                                                  (len(lines[line_no]) * planes.gui.PIX_PER_CHAR, 30)),
                                      background_color=(128, 128, 128, 0)))


        # Use default style
        self.sub(planes.gui.lmr.LMRButton("OK", 50, self.ok))

        return
