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

