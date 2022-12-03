import random
import os
import tkinter as tk
import math


# Constants for the screen
# NOTE: For Replit, 500x300 is the maximum dimensions
_BACKGROUND = '#C0C0C0'
_OUTLINE = 'black'
_OUTLINE_WIDTH = 2


# Constants for the player movement
_DIRECTIONS = ((0, -1), (0, 1), (-1, 0), (1, 0))
_P1 = ('w', 's', 'a', 'd', 'z')
_P2 = ('Up','Down', 'Left', 'Right', 'Return')
_P3 = ('t', 'g', 'f', 'h', 'Space')
_P4 = ('i', 'k', 'j', 'l', 'm')
_COLOURS = ('blue', 'purple', 'orange', 'yellow')


# Other constants for the game
_GAME_NAME = 'PixelCooked!'
_INGREDIENT_SIZE_PERCENT = 0.7
_PLAYER_SIZE_PERCENT = 0.8
_REFRESH_IN_MS = 10


"""
Classes for the different types of blocks
"""


class Block:

    """
    Represents a simple block on the map.
    Allows for the following:
        - Placing ingredients on the block
    """

    def __init__(self, screen, x, y, length, fill, outline=_OUTLINE):
        self._block = screen.create_rectangle(x, y, x + length, y + length,
                                             outline=outline,
                                             fill=fill,
                                             width=0 if outline is None else _OUTLINE_WIDTH)
        self._ingredient = None
        self._screen = screen

    def get_coords(self):
        return self._screen.coords(self._block)

    def has_ingredient(self):
        return self._ingredient is not None

    def receive_ingredient(self, ingredient):
        if not self.has_ingredient():
            self._ingredient = ingredient

    def remove_ingredient(self):
        ingredient = self._ingredient
        self._ingredient = None
        return ingredient


class Placeholder(Block):

    """
    Represents an inaccessible block on the map.
    Does not allow for placing of ingredients.
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='gray', outline=None)

    def receive_ingredient(self, ingredient):
        # Overrides the parent function to disable receiving of ingredients
        pass


class Trash(Block):

    """
    Represents the trash block on the map.
    Allows for the following:
        - Deletion of ingredients by placing them on the trash block
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#111111')

    def receive_ingredient(self, ingredient):
        # Overrides the parent function to delete ingredients once received
        self._screen.delete(ingredient.get_ingredient())


class Crate(Block):

    """
    Represents an ingredient crate on the map.
    Allows for the following:
        - Retrieval of ingredient by removing them from the crate block
    """

    def __init__(self, screen, x, y, length, ingredient):
        # ingredient is a callable function that creates a specified ingredient
        super().__init__(screen, x, y, length, fill='#BC8F8F')
        self._ingredient = ingredient

    def receive_ingredient(self, ingredient):
        # Overrides the parent function to disable receiving of ingredients
        pass

    def remove_ingredient(self):
        # Overrides the parent function to return the specified ingredient
        x1, y1, x2, y2 = self.get_coords()
        return self._ingredient(self._screen,
                                x1 + (1 - _INGREDIENT_SIZE_PERCENT) / 2 * (x2 - x1),
                                y1 + (1 - _INGREDIENT_SIZE_PERCENT) / 2 * (y2 - y1),
                                size=(x2 - x1) * _INGREDIENT_SIZE_PERCENT)


class ServingBlock(Block):

    """
    Represents a serving block on the map for players to deliver the completed orders.
    Allows for the following:
        - Serving of ingredients by placing them on the serving block
        - Completing orders by using one or more ingredients stored here
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='green')
        
        self.container = {'Sashimi': 0, 'FishFillet': 0, 'FriedFish': 0, 'Fish': 0, 'Salad': 0, 'Lettuce': 0, 'Crouton':0, 'Breadpiece': 0, 'Toast': 0, 'Bread': 0}
        self.current_order = []
        self.current_order.append(self.generate_order) #appends 3 generated orders to current_order
        self.current_order.append(self.generate_order)
        self.current_order.append(self.generate_order)

    def check_order(self):
        #checks current order and if self.container has enough then removes that set of ingredients from self.container and prompts next order. Does nothing if container does not have enough ingredients.
        x = 0 
        for i in range(1, len(self.current_order[0])):
            if self.container[self.current_order[0][i]] > 0:
                x += 1
                
        if x == (len(self.current_order[0])-1):
            for i in range(1, len(self.current_order[0])):
                self.container[self.current_order[0][i]] -= 1
            self.update_order()
        

    def receive_ingredient(self, ingredient):
        #increases quantity of ingredient in container by 1 and runs check_order()
        self.container[ingredient] += 1
        self.check_order(self)

    def remove_ingredient(self):
        pass #disable removing of ingredients
    
    
    def _draw_order_menu():
        pass  # remove this statement

    def update_order(self):
        #is called when current order is completed. shifts all orders up by 1 and generates a new order using generate_order()
        self.current_order[0] = self.current_order[1]
        self.current_order[1] = self.current_order[2]
        self.current_order[2] = self.generate_order

    def generate_order():
        #randomly chooses an order from a list that is stored here and returns it as a list of ingredients. 1st element is name of dish, subsequent elements are the ingredients needed
        list_of_orders = [('Sashimi','Sashimi'), ('FishFillet','FishFillet'), ('SashimiSalad','Sashimi','Salad'), ('Salad','Salad'), ('Crouton','Crouton'), ('CroutonSalad','Salad','Crouton'), ('FishFilletSandwich','FishFillet','Salad','Toast'),('Toast','Toast')]
        order = random.choice(list_of_orders)
        return order

    

    
class ProcessBlock(Block):

    """
    Represents a processing block on the map.
    Allows for the following:
        - Placing and removing of ingredients
        - Changing one ingredient to another via the specified process
    """

    _BAR_WIDTH_PERCENT = 0.1

    def __init__(self, screen, x, y, length, fill, process, time):
        # process is a callable function (either chop() or cook() function)
        # time is the amount of time that should pass for the process to complete
        super().__init__(screen, x, y, length, fill)
        self._timer = self._max_time = time
        self._process = process
        self._to_process = False
        
        # create the base outline for the loading bar
        # the base outline is represented by 4 white rectangles on the border of the block
        _ = self._draw_border_rectangles(1, 'white')

        # initialise the loading bar
        # the loading bar is represented by 4 rectangles on top of the base outline
        # they will be updated in both position and colour to reflect an actual loading bar
        self._loading_bar = []

    def _draw_border_rectangles(self, frac, fill):
        """
        This function draws the 4 rectangles that border the block to reflect a loading bar.
        The 4 rectangles are returned in an anticlockwise manner, starting from the top left.
        """
        x1, y1, x2, y2 = self.get_coords()
        length = x2 - x1
        return \
            None if frac == 0 else self._screen.create_rectangle(
                x1,
                y1,
                x1 + length * (1 - self._BAR_WIDTH_PERCENT) * 4 * min(frac, 0.25),
                y1 + length * self._BAR_WIDTH_PERCENT,
                fill=fill, width=0
            ), \
            None if frac <= 0.25 else self._screen.create_rectangle(
                x2 - length * self._BAR_WIDTH_PERCENT,
                y1,
                x2,
                y1 + length * (1 - self._BAR_WIDTH_PERCENT) * 4 * (min(frac, 0.5) - 0.25),
                fill=fill, width=0
            ), \
            None if frac <= 0.5 else self._screen.create_rectangle(
                x2,
                y2 - length * self._BAR_WIDTH_PERCENT,
                x2 - length * (1 - self._BAR_WIDTH_PERCENT) * 4 * (min(frac, 0.75) - 0.5),
                y2,
                fill=fill, width=0
            ), \
            None if frac <= 0.75 else self._screen.create_rectangle(
                x1,
                y2,
                x1 + length * self._BAR_WIDTH_PERCENT,
                y2 - length * (1 - self._BAR_WIDTH_PERCENT) * 4 * (frac - 0.75),
                fill=fill, width=0
            )

    def _clear_loading_bar(self):
        """
        This function clears the displayed loading bar on the screen.
        """
        while self._loading_bar:
            self._screen.delete(self._loading_bar.pop())

    def _update_loading_bar(self):
        """
        This function reflects the current timer on screen
        by displaying a loading bar wrapped around the block on screen.
        The bar is filled in proportion to how much time has passed from the timer
        and coloured on a scale from red to green using the same proportion.

        The RGB values from red to green increases from 0 to 255 from green first,
        followed by decreasing from 255 to 0 from red.
        """
        # remove the previous loading bar from the screen
        self._clear_loading_bar()

        # obtain colour based on fraction of time passed
        frac = (self._max_time - self._timer) / self._max_time
        red = round(255 * (1 - 2 * max(frac - 0.5, 0)))
        green = round(255 * 2 * min(frac, 0.5))
        r1, r2 = divmod(red, 16)
        g1, g2 = divmod(green, 16)
        chars = '0123456789ABCDEF'
        fill = f'#{chars[r1]}{chars[r2]}{chars[g1]}{chars[g2]}00'

        # draw rectangles
        self._loading_bar.extend(self._draw_border_rectangles(frac, fill))

    def update_timer(self, dt):
        """
        This functions takes in dt, the number of milliseconds that have passed.
        Updates the timer and loading bar to reflect the passing of dt milliseconds.
        Once the timer hits zero, performs the process and resets the timer.
        """
        self._timer-=dt
        return self._timer

    def reset_timer(self):
        """
        This function resets the timer and loading bar of the block.
        """
        if(self._timer == 0):
            self._timer = self._max_time
        else:
            self._update_loading_bar() #add loading bar if time is !=0
            

    def receive_ingredient(self, ingredient):
        # Overrides the parent function to start the timer once the ingredient is received
        # The timer is started by indicating that the ingredient should be processed
        self._to_process = self.has_ingredient()
        super().receive_ingredient(ingredient)

    def remove_ingredient(self):
        # Overrides the parent function to stop and reset the timer first
        # before returning the ingredient on the block
        self.reset_timer()
        return super().remove_ingredient()


class ChoppingBlock(ProcessBlock):

    """
    Represents a chopping block on the map.
    Allows for the following:
        - Placing and removing of ingredients
        - Chopping (calling the chop() function) of ingredients
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length,
                         fill='#F5F5DC',
                         process=lambda ingredient: ingredient.chop(),
                         time=5)


class CookingBlock(ProcessBlock):

    """
    Represents a cooking block on the map.
    Allows for the following:
        - Placing and removing of items
        - Cooking (calling of the cook() function) of ingredients
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length,
                         fill='#ED820E',
                         process=lambda ingredient: ingredient.cook(),
                         time=10)


"""
Classes for the different types of ingredients
"""


class Ingredient:

    """
    Represents a generic interactible ingredient on the map.
    Allows for the following:
        - Picking up / placing down
        - Moving around
        - Chopping and cooking
    """

    def __init__(self, screen, x, y, length, fill, *, can_chop=False, can_cook=False):
        # (x, y) is the top left corner
        self._ingredient = screen.create_oval(x, y, x + length, y + length,
                                              outline=_OUTLINE,
                                              fill=fill,
                                              width=_OUTLINE_WIDTH)
        self._player = None
        self._screen = screen
        self._can_chop = can_chop
        self._can_cook = can_cook

    def get_ingredient(self):
        return self._ingredient

    def get_coords(self):
        return self._screen.coords(self._ingredient)

    def move(self, x, y):
        self._screen.move(self._ingredient, x, y)

    def moveto(self, x, y):
        self._screen.moveto(self._ingredient, x, y)

    def drop(self, x=None, y=None):
        """
        This function takes an (x, y) coordinate to drop the ingredient to.
        Moves the ingredient to those coordinates and removes any player owner.
        """
        if self._player and x is not None and y is not None:
            self.moveto(x, y)
        self._player = None

    def pick_up(self, player):
        """
        This function takes the player that is about to pick up this ingredient.
        Moves the ingredient to the player coordinates and sets the player as owner.
        """
        if self._player:
            # another player has already picked this ingredient up
            return
        self._player = player
        x1, y1, x2, y2 = player.get_coords()
        x = x1 - self._size if player.get_direction() == Player.LEFT() else \
            x2 if player.get_direction() == Player.RIGHT() else \
            (x1 + x2 - self._size) / 2
        y = y1 - self._size if player.get_direction() == Player.UP() else \
            y2 if player.get_direction() == Player.DOWN() else \
            (y1 + y2 - self._size) / 2
        self.moveto(x, y)

    def can_chop(self):
        """
        This function indicates if the ingredient can be chopped.
        """
        return self._can_chop

    def can_cook(self):
        """
        This function indicates if the ingredient can be cooked.
        """
        return self._can_cook

    def chop(self):
        """
        This function returns self if the ingredient cannot be chopped.
        Otherwise, it return the resultant ingredient from the chopping process.
        Abstract method to be overriden in child(ren) class(es).
        """
        return self

    def cook(self):
        """
        This function returns self if the ingredient cannot be cooked.
        Otherwise, it return the resultant ingredient from the cooking process.
        Abstract method to be overriden in child(ren) class(es).
        """
        return self


class Sashimi(Ingredient):

    """
    Represents the sashimi ingredient.
    Allows for the following:
        - Combines with Salad to form SashimiSalad
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#F56C57')


class FishFillet(Ingredient):

    """
    Represents the fish fillet ingredient.
    Allows for the following:
        - Combines with Salad and Toast to form FishFilletSandwich
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#D3A44A')


class FriedFish(Ingredient):

    """
    Represents the fried fish ingredient.
    Allows for the following:
        - Can be chopped to form FishFillet
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#A26F25', can_chop=True)

    def chop(self):
        # Overrides the parent function to return FishFillet
        x1, y1, x2, _ = self.get_coords()
        self._screen.delete(self._ingredient)
        return FishFillet(self._screen, x1, y1, x2 - x1)


class Fish(Ingredient):

    """
    Represents the raw fish ingredient.
    Allows for the following:
        - Can be chopped to form Sashimi
        - Can be cooked to form FriedFish
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#B245A5', can_chop=True, can_cook=True)

    def chop(self):
        # Overrides the parent function to return Sashimi
        x1, y1, x2, _ = self.get_coords()
        self._screen.delete(self._ingredient)
        return Sashimi(self._screen, x1, y1, x2 - x1)

    def cook(self):
        # Overrides the parent function to return FriedFish
        x1, y1, x2, _ = self.get_coords()
        self._screen.delete(self._ingredient)
        return FriedFish(self._screen, x1, y1, x2 - x1)


class Salad(Ingredient):

    """
    Represents the salad ingredient.
    Allows for the following:
        - Combines with Sashimi to form SashimiSalad
        - Combines with FishFillet and Toast to form FishFilletSandwich
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#9B9246')


class Lettuce(Ingredient):

    """
    Represents the lettuce ingredient.
    Allows for the following:
        - Can be chopped to form Salad
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#B9E3AB', can_chop=True)

    def chop(self):
        # Overrides the parent function to return Salad
        x1, y1, x2, _ = self.get_coords()
        self._screen.delete(self._ingredient)
        return Salad(self._screen, x1, y1, x2 - x1)


class Crouton(Ingredient):

    """
    Represents the croutons ingredient.
    Allows for the following:
        - Combines with Salad to form CroutonSalad
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#80471C')


class BreadPiece(Ingredient):

    """
    Represents the bread pieces ingredient.
    Allows for the following:
        - Can be cooked to form Crouton
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#E3D5C5', can_cook=True)

    def cook(self):
        # Overrides the parent function to return Crouton
        x1, y1, x2, _ = self.get_coords()
        self._screen.delete(self._ingredient)
        return Crouton(self._screen, x1, y1, x2 - x1)


class Toast(Ingredient):

    """
    Represents the toast ingredient.
    Allows for the following:
        - Combines with FishFillet and Salad to form FishFilletSandwich
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#E3A10F')


class Bread(Ingredient):

    """
    Represents the bread ingredient.
    Allows for the following:
        - Can be chopped to form BreadPiece
        - Can be cooked to form Toast
    """

    def __init__(self, screen, x, y, length):
        super().__init__(screen, x, y, length, fill='#FDF3E8', can_chop=True, can_cook=True)

    def chop(self):
        # Overrides the parent function to return BreadPiece
        x1, y1, x2, _ = self.get_coords()
        self._screen.delete(self._ingredient)
        return BreadPiece(self._screen, x1, y1, x2 - x1)

    def cook(self):
        # Overrides the parent function to return Toast
        x1, y1, x2, _ = self.get_coords()
        self._screen.delete(self._ingredient)
        return Toast(self._screen, x1, y1, x2 - x1)


"""
The player class
"""


class Player:

    """
    Represents a human player.
    Allows for the following:
        - Moving around (with keyboard keys)
        - Picking up / move / drop ingredients
        - Collision with blocks
    """

    _VELOCITY = 2
    _UP, _DOWN, _LEFT, _RIGHT = range(4)

    def __init__(self, screen, x, y, length, fill):
        # (x, y) is the top left corner
        self._ingredient = None
        self._direction = self._UP
        self._vx = self._vy = 0
        self._screen = screen
        self._fill = fill
        triangle = ((x, y + length),
            (x + 0.5 * length, y),
            (x + length, y + length))
        self._player = self._create(triangle)

    def _create(self, triangle):
        return self._screen.create_polygon(triangle,
                                           outline=_OUTLINE,
                                           fill=self._fill,
                                           width=_OUTLINE_WIDTH)

    @classmethod
    def UP(cls):
        return cls._UP

    @classmethod
    def DOWN(cls):
        return cls._DOWN

    @classmethod
    def LEFT(cls):
        return cls._LEFT

    @classmethod
    def RIGHT(cls):
        return cls._RIGHT

    def get_coords(self):
        x1, y1, x2, y2, x3, y3 = self._screen.coords(self._player)
        return min(x1, x2, x3), min(y1, y2, y3), max(x1, x2, x3), max(y1, y2, y3)

    def get_direction(self):
        return self._direction

    def move(self,block,players):
        """
        This function handles the movement update of the player.
        
        Whenever this function is called, the function tries to move the player by
        self._vx (horizontally) and self._vy (vertically).
        If it encounters any collidable objects along the path,
        the movement of the player will be limited by the position of that object.
        
        Finally, the player character is moved by (dx, dy) to the current position:
            self._screen.move(self._player, dx, dy)  # move player by dx and dy
        If the player is holding an ingredient, that ingredient is moved too:
            self._ingredient.move(dx, dy)  # move ingredient by dx and dy
        """
        self._screen.move(self._player, 0 , self._vy)
        for player in players:
            if intersects(self,block) or intersects(self,player) == True:
                self._screen.move(self._player, 0 , -self._vy)
                break
            else:
                pass
                
        self._screen.move(self._player, self._vx , 0)
        for player in players:
            if intersects(self,block) or intersects(self,player) == True:
                self._screen.move(self._player, -self._vx , 0) 
                break
            else:
                pass

        """
        if self._ingredient:
            self._ingredient.move(self._vx, self._vy)
        """

    def has_ingredient(self):
        return self._ingredient is not None

    def pick_up_ingredient(self, ingredient):
        self._ingredient = ingredient
        ingredient.pick_up(self)

    def drop_ingredient(self, x=None, y=None):
        if x is None and y is None:
            x, y, _, _ = self.get_coords()
        self._ingredient.drop(x, y)
        self._ingredient = None

    def move_up(self, event):
        """
        This function activates when the event that tells the player to move up is triggered
        (i.e., when the corresponding key to move up is pressed).
        Re-draws the player character and any ingredients being held to match the up movement.
        """
        self._vy = -self._VELOCITY
        if self._direction != self._UP:
            self._direction = self._UP
            # Re-draw the player character to face up
            x1, y1, x2, y2 = self.get_coords()
            triangle = ((x1, y2),
                        (x1 + 0.5 * (x2 - x1), y1),
                        (x2, y2))
            self._screen.delete(self._player)
            self._player = self._create(triangle)
            # Stop player from moving horizontally
            self.stop_moving_horizontally(event)
            # Re-draw the ingredient to match the player character
            if self._ingredient:
                x3, _, x4, _ = self._ingredient.get_coords()
                self._ingredient.moveto((x1 + x2 + x3 - x4) / 2, y1 + x3 - x4)

    def move_down(self, event):
        """
        This function activates when the event that tells the player to move down is triggered
        (i.e., when the corresponding key to move down is pressed).
        Re-draws the player character and any ingredients being held to match the down movement.
        """
        self._vy = self._VELOCITY
        if self._direction != self._DOWN:
            self._direction = self._DOWN
            # Re-draw the player character to face down
            x1, y1, x2, y2 = self.get_coords()
            triangle = ((x1, y1),
                        (x1 + 0.5 * (x2 - x1), y2),
                        (x2, y1))
            self._screen.delete(self._player)
            self._player = self._create(triangle)
            # Stop player from moving horizontally
            self.stop_moving_horizontally(event)
            # Re-draw the ingredient to match the player character
            if self._ingredient:
                x3, _, x4, _ = self._ingredient.get_coords()
                self._ingredient.moveto((x1 + x2 + x3 - x4) / 2, y2)

    def move_left(self, event):
        """
        This function activates when the event that tells the player to move left is triggered
        (i.e., when the corresponding key to move left is pressed).
        Re-draws the player character and any ingredients being held to match the left movement.
        """
        self._vx = -self._VELOCITY
        if self._direction != self._LEFT:
            self._direction = self._LEFT
            # Re-draw the player character to face left
            x1, y1, x2, y2 = self.get_coords()
            triangle = ((x1, y1 + 0.5 * (x2 - x1)),
                        (x2, y1),
                        (x2, y2))
            self._screen.delete(self._player)
            self._player = self._create(triangle)
            # Stop player from moving vertically
            self.stop_moving_vertically(event)
            # Re-draw the ingredient to match the player character
            if self._ingredient:
                x3, _, x4, _ = self._ingredient.get_coords()
                self._ingredient.moveto(x1 + x3 - x4, (y1 + y2 + x3 - x4) / 2)

    def move_right(self, event):
        """
        This function activates when the event that tells the player to move right is triggered
        (i.e., when the corresponding key to move right is pressed).
        Re-draws the player character and any ingredients being held to match the right movement.
        """
        self._vx = self._VELOCITY
        if self._direction != self._RIGHT:
            self._direction = self._RIGHT
            # Re-draw the player character to face right
            x1, y1, x2, y2 = self.get_coords()
            triangle = ((x1, y1),
                        (x1, y2),
                        (x2, y1 + 0.5 * (x2 - x1)))
            self._screen.delete(self._player)
            self._player = self._create(triangle)
            # Stop player from moving vertically
            self.stop_moving_vertically(event)
            # Re-draw the ingredient to match the player character
            if self._ingredient:
                x3, _, x4, _ = self._ingredient.get_coords()
                self._ingredient.moveto(x2, (y1 + y2 + x3 - x4) / 2)

    def stop_moving_horizontally(self, event):
        self._vx = 0

    def stop_moving_vertically(self, event):
        self._vy = 0


"""
Functions for updating game mechanics
"""


def bind_player_controls(window, players, controls):
    # Expects a list of players and a list of controls, both of the same length
    window.focus_set()
    for player, (up, down, left, right, interact) in zip(players, controls):
        window.bind(f'<KeyPress-{up}>', player.move_up)
        window.bind(f'<KeyPress-{down}>', player.move_down)
        window.bind(f'<KeyPress-{left}>', player.move_left)
        window.bind(f'<KeyPress-{right}>', player.move_right)
        window.bind(f'<KeyRelease-{up}>', player.stop_moving_vertically)
        window.bind(f'<KeyRelease-{down}>', player.stop_moving_vertically)
        window.bind(f'<KeyRelease-{left}>', player.stop_moving_horizontally)
        window.bind(f'<KeyRelease-{right}>', player.stop_moving_horizontally)


def unbind_player_controls(window, controls):
    # Expects a list of conrols
    window.focus_set()
    for (up, down, left, right, interact) in controls:
        window.unbind(f'<KeyPress-{up}>')
        window.unbind(f'<KeyPress-{down}>')
        window.unbind(f'<KeyPress-{left}>')
        window.unbind(f'<KeyPress-{right}>')
        window.unbind(f'<KeyRelease-{up}>')
        window.unbind(f'<KeyRelease-{down}>')
        window.unbind(f'<KeyRelease-{left}>')
        window.unbind(f'<KeyRelease-{right}>')


def intersects(obj1, obj2):
    """
    This function takes in two (collidable) objects.
    Assume that the bounding box of both objects can be obtained by
        x1, y1, x2, y2 = obj.get_coords(),
    where
        (x1, y1) is the top-left corner,
        (x2, y2) is the bottom-right corner,
        0 <= x1 <= x2 <= _WIDTH and 0 <= y1 <= y2 <= _HEIGHT.
    Returns True if the bounding boxes of the two objects intersect and False otherwise.

    @example
    player1 = Player(screen, 100, 100, 50, 'red')
    print(player1.get_coords())  # prints 100 100 150 150
    block1 = Block(screen, 100, 100, 50, 'brown')
    print(block1.get_coords())  # prints 100 100 150 150
    print(intersects(player1, block1))  # prints True

    @example
    block2 = Block(screen, 150, 150, 50, 'brown')
    print(block2.get_coords())  # prints 150 150 200 200
    print(intersects(player1, block2))  # prints True

    @example
    block3 = Block(screen, 120, 120, 50, 'brown')
    print(block3.get_coords())  # prints 120 120 170 170
    print(intersects(player1, block3))  # prints True

    @example
    block4 = Block(screen, 80, 80, 10, 'brown')
    print(block4.get_coords())  # prints 80 80 90 90
    print(intersects(player1, block4))  # prints False

    @example
    block5 = Block(screen, 145, 75, 50, 'brown')
    print(block5.get_coords())  # prints 145 75 195 125
    print(intersects(player1, block5))  # prints True

    @example
    block6 = Block(screen, 25, 35, 80, 'brown')
    print(block6.get_coords())  # prints 25 35 105 115
    print(intersects(player1, block6))  # prints True
    """
    a1,b1,a2,b2 = obj1.get_coords()
    x1,y1,x2,y2 = obj2.get_coords()
    if (x1 <= a1 <= x2 or x1 <= a2 <= x2)  and (y1 <= b1 <= y2 or y1 <= b2 <= y2):
      return True  
    else:
      return False 
  


def distance(obj1, obj2):
    """
    This function takes in two (interactible) objects.
    Assume that the bounding box of both objects can be obtained via
        x1, y1, x2, y2 = obj.get_coords(),
    where
        (x1, y1) is the top-left corner of the bounding box,
        (x2, y2) is the bottom-right corner of the bounding box,
        0 <= x1 <= x2 <= _WIDTH and 0 <= y1 <= y2 <= _HEIGHT.
    Return the distance between the two objects, given by the formula
        sqrt(pow(xc1 - xc2, 2) + pow(yc1 - yc2, 2)),
    where
        (xc1, yc1) is the centre of the bounding box of obj1,
        (xc2, yc2) is the centre of the bounding box of obj2,
        sqrt and pow are the square-root and power functions respectively.

    @example
    player1 = Player(screen, 100, 100, 50, 'red')
    print(player1.get_coords())  # prints 100 100 150 150
    block1 = Block(screen, 100, 100, 50, 50, 'brown')
    print(block1.get_coords())  # prints 100 100 150 150
    print(distance(player1, block1))  # prints 0

    @example
    block2 = Block(screen, 150, 150, 50, 50, 'brown')
    print(block2.get_coords())  # prints 150 150 200 200
    print(distance(player1, block2))  # prints 70.7106...
    """
    x1, y1 , x2, y2 = obj1.get_coords()
    x3, y3 , x4, y4 = obj2.get_coords()
  
    obj_1_x = (x1 + x2)/2 
    obj_1_y = (y1 + y2)/2
  
    obj_2_x = (x3 + x4)/2
    obj_2_y = (y3 + y4)/2

    dist = math.sqrt(pow(obj_1_x - obj_2_x, 2) + pow(obj_1_y - obj_2_y, 2))

    return dist
    

def object_with_min_distance(obj, obj_list):
    """
    This function takes in an object obj and a list of (interactible) objects obj_list.
    Assume that the bounding box of all objects can be obtained via
        x1, y1, x2, y2 = obj.get_coords(),
    where
        (x1, y1) is the top-left corner of the bounding box,
        (x2, y2) is the bottom-right corner of the bounding box,
        0 <= x1 <= x2 <= _WIDTH and 0 <= y1 <= y2 <= _HEIGHT.
    Return the object in obj_list with the smallest distance to obj.
    """
    total_dist_list = []
    for i in obj_list:
    
        object_with_dist = distance(obj,i)
        total_dist_list.append(object_with_dist)
    
    index_dist = total_dist_list.index(min(total_dist_list))
    return obj_list[index_dist]


    #index of min dist match obj in the list

def ms_to_time(ms):
    """
    This function converts milliseconds into MM:SS:DD, where
        MM  - the number of minutes
        SS  - the number of seconds
        DDD - the number of milliseconds
    Returns the string that the input represents.
    """
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    return f'{str(minutes).zfill(2)}:{str(seconds).zfill(2)}:{str(milliseconds).zfill(3)}'


def time_to_ms(time):
    """
    This function converts a string representing time into the number of milliseconds.
    The string is always in the form MM:SS:DDD, where
        MM  - the number of minutes
        SS  - the number of seconds
        DDD - the number of milliseconds
    Returns the number of milliseconds.
    """
    minutes, seconds, milliseconds = map(int, time.split(':'))
    return minutes * 60000 + seconds * 1000 + milliseconds


def update_game_frame(grid_length, grid_width,
                      window, timer,
                      players, controls,
                      all_blocks, process_blocks):
    """
    This function updates the attributes of all objects on the map according to:
        - The amount of time passed, calculated from the (approximated) frame rate
        - User input at the given moment, handled by event bindings to the relevant functions
    """
    ms = time_to_ms(timer.cget('text'))
    
    # Stop the game if there is no time remaining
    if ms == 0:
        for player in players:
            player.stop_moving_horizontally(None)
            player.stop_moving_vertically(None)
        unbind_player_controls(window, controls)
        # TODO navigate to scoring screen
        return

    # Otherwise:
    # 1. Update game timer
    timer.config(text=ms_to_time(max(ms - _REFRESH_IN_MS, 0)))

    # 2. Update movement for each player
    x3, _, x4, _ = list(all_blocks.values())[0].get_coords()
    for i, player in enumerate(players):
        # Get the relative coordinates of the player
        # with respect to the grid-based system of the blocks
        x1, y1, x2, y2 = player.get_coords()
        col = int(x1 // (x4 - x3))
        crmd = int(x2 // (x4 - x3)) - col
        row = int(y1 // (x4 - x3))
        rrmd = int(y2 // (x4 - x3)) - row
        
        # Get the block nearest to the player,
        # considering the direction of the player
        blocks_to_check = []
        dx, dy = _DIRECTIONS[player.get_direction()]
        row += int(rrmd and dy == -1)
        col += int(crmd and dx == -1)
        while 0 <= col < grid_length and 0 <= row < grid_width:
            if (row, col) in all_blocks:
                blocks_to_check.append(all_blocks[(row, col)])
            if dx == 0 and (row, col + crmd) in all_blocks:
                blocks_to_check.append(all_blocks[(row, col + crmd)])
            if dy == 0 and (row + rrmd, col) in all_blocks:
                blocks_to_check.append(all_blocks[(row + rrmd, col)])
            row += dy
            col += dx
        nearest_block = object_with_min_distance(player, blocks_to_check)

        # Update player movement given the nearest block and all other players
        player.move(nearest_block, players[:i] + players[i+1:])

    # 3. Update timer for each process block, if applicable
    for block in process_blocks:
        # TODO call function to update timer
        break

    # Wait for the desired FPS to refresh the screen and update again
    window.after(_REFRESH_IN_MS,
                 lambda: update_game_frame(grid_length, grid_width,
                                           window, timer,
                                           players, controls,
                                           all_blocks, process_blocks))


"""
Functions for controlling map generation
"""


def is_map_accessible(spaces):
    """
    This function takes in a set of (x, y) coordinates representing empty spaces.
    Returns True if all empty areas of the map are accessible and False otherwise.
    """
    if not spaces:
        # there are no empty spaces to access
        # so technically, all empty spaces can be accessed
        return True
    curr = [spaces.pop()]
    while curr and spaces:
        # find all adjacent empty spaces using breadth-first search
        nxt = []
        for row, col in curr:
            for dr, dc in _DIRECTIONS:
                if (row + dr, col + dc) in spaces:
                    spaces.discard((row + dr, col + dc))
                    nxt.append((row + dr, col + dc))
        curr = nxt
    return not spaces


def is_block_accessible(row, col, grid_length, grid_width, blocks, placeholders):
    """
    This function takes in the (row, col) coordinate of a block
    and all other placeholders and blocks already generated.
    Returns True if the new block is accessible and False otherwise.
    """
    return any(0 <= col + dc < grid_length and
               0 <= row + dr < grid_width and
               (row + dr, col + dc) not in placeholders and
               (row + dr, col + dc) not in blocks
               for dr, dc in _DIRECTIONS)


def generate_map(screen, block_length, grid_length, grid_width, probability):
    """
    This function generates a map of given grid_length x grid_width.

    The function first generates the border of blocks
    that make up the outer boundary of the map.
    For a given probability, the function then determines how many more blocks to generate.
    The blocks are then generated on a grid-based system based on
    whether they allow the entire map to remain accessible to any player.

    Next, the function determines which blocks should be assigned a specialised role.
    There are 7 different types of specialised blocks which need to be taken into consideration:
    
          Block Type     Minimum Number   Maximum Number
        ==============   ==============   ==============
          Fish Crate           1                1
         Lettuce Crate         1                1
         Bread Crate           1                1
         Trash Block           1                1
         Serving Block         1                1
        Chopping Block         1                -
         Cooking Block         1                -

    Finally, the function draws all the blocks on the screen and returns them, in order of:
        - Placeholders
        - Normal blocks
        - Chopping blocks
        - Cooking blocks
        - Fish crate
        - Lettuce crate
        - Bread crate
        - Trash block
        - Serving block
    """
    # Define default blocks and placeholders
    placeholders = {
        (0, 0),
        (0, grid_length - 1),
        (grid_width - 1, 0),
        (grid_width - 1, grid_length - 1)
    }
    blocks = set()
    for row in range(1, grid_width - 1):
        blocks.add((row, 0))
        blocks.add((row, grid_length - 1))
    for col in range(1, grid_length - 1):
        blocks.add((0, col))
        blocks.add((grid_width - 1, col))

    # Determine if another block should be generated
    # If there are less than 7 available blocks, another block must be generated
    attempts = 0
    while attempts < 3 or len(blocks) < 7:
        if random.random() <= (probability if len(blocks) >= 7 else 1):
            # Generate the coordinates of the next block
            coord = random.randint(0, grid_length * grid_width - 1)
            row, col = divmod(coord, grid_length)
            while attempts < 10 and \
                    ((row, col) in blocks or
                     (row, col) in placeholders or
                     not is_map_accessible({(r, c) for r in range(grid_width) for c in range(grid_length)
                                           if (r, c) not in placeholders and (r, c) not in blocks and (r, c) != (row, col)})):
                coord = random.randint(0, grid_length * grid_width - 1)
                row, col = divmod(coord, grid_length)
                # Try again; maximum of 10 attempts
                attempts += 1
            if attempts == 10:
                break
            # Generate the next block and check adjacent blocks
            if is_block_accessible(row, col, grid_length, grid_width, blocks, placeholders):
                blocks.add((row, col))
            else:
                placeholders.add((row, col))
            for dr, dc in _DIRECTIONS:
                if (row + dr, col + dc) in blocks and \
                        not is_block_accessible(row + dr, col + dc, grid_length, grid_width, blocks, placeholders):
                    blocks.discard((row + dr, col + dc))
                    placeholders.add((row + dr, col + dc))
            # Reset the attempt counter for the next iteration
            attempts = 0
        else:
            # Try again; maximum of 3 attempts
            attempts += 1

    # Generate specialised blocks from the given set of blocks
    # Each map must have one of each ingredient crate, serving block, trash block,
    # and one or more each of chopping and cooking blocks
    individual_blocks = []
    for _ in range(7):
        crate = list(blocks)[random.randint(0, len(blocks)-1)]
        blocks.remove(crate)
        individual_blocks.append(crate)
    cooking_blocks = [individual_blocks.pop()]
    chopping_blocks = [individual_blocks.pop()]
    (fish_crate_row, fish_crate_col), \
        (lettuce_crate_row, lettuce_crate_col), \
        (bread_crate_row, bread_crate_col), \
        (serving_block_row, serving_block_col), \
        (trash_block_row, trash_block_col) = individual_blocks

    # Determine if there should be more than 1 chopping block
    # or more than 1 cooking block
    while blocks and random.random() <= probability:
        chopping_block = list(blocks)[random.randint(0, len(blocks)-1)]
        blocks.remove(chopping_block)
        chopping_blocks.append(chopping_block)
    while blocks and random.random() <= probability:
        cooking_block = list(blocks)[random.randint(0, len(blocks)-1)]
        blocks.remove(cooking_block)
        cooking_blocks.append(cooking_block)

    # Generate all the blocks and placeholders
    all_placeholders = {
        (row, col): Placeholder(screen, col * block_length, row * block_length, block_length)
        for row, col in placeholders
    }
    all_blocks = {
        (row, col): Block(screen, col * block_length, row * block_length, block_length, fill='brown')
        for row, col in blocks
    }
    all_chopping_blocks = {
        (row, col): ChoppingBlock(screen, col * block_length, row * block_length, block_length)
        for row, col in chopping_blocks
    }
    all_cooking_blocks = {
        (row, col): CookingBlock(screen, col * block_length, row * block_length, block_length)
        for row, col in cooking_blocks
    }
    return \
        all_placeholders, \
        all_blocks, \
        all_chopping_blocks, \
        all_cooking_blocks, \
        {
            (fish_crate_row, fish_crate_col): Crate(screen, fish_crate_col * block_length, fish_crate_row * block_length, block_length, Fish),
            (lettuce_crate_row, lettuce_crate_col): Crate(screen, lettuce_crate_col * block_length, lettuce_crate_row * block_length, block_length, Lettuce),
            (bread_crate_row, bread_crate_col): Crate(screen, bread_crate_col * block_length, bread_crate_row * block_length, block_length, Bread),
            (serving_block_row, serving_block_col): ServingBlock(screen, serving_block_col * block_length, serving_block_row * block_length, block_length),
            (trash_block_row, trash_block_col): Trash(screen, trash_block_col * block_length, trash_block_row * block_length, block_length)
        }


"""
Functions for controlling screen displays
"""


def clear_window(window):
    """
    This function clears the current screen and frame in the window.
    """
    for widget in window.winfo_children():
        widget.destroy()


def create_info_screen(window, length, time):
    """
    This function takes in the current window and creates the information screen on it.
    It creates and displays the new screen without replacing any previous screens.
    
    The function takes in the time (in milliseconds) and displays a timer on the left.
    Then, the function displays the order menu on the right.
    
    Returns the timer label and the order screen in the info screen for updating.
    """
    # Create a frame to store the separate components
    frame = tk.Frame(window, bg=_BACKGROUND, width=length)
    frame.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X)

    # Create timer component
    timer_screen = tk.Canvas(frame, bg=_BACKGROUND, width=length * 0.1)
    timer_screen.pack(side=tk.LEFT, anchor=tk.CENTER, fill=tk.X)
    timer = tk.Label(timer_screen, text=ms_to_time(time))
    timer.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X)

    # Create order menu component
    order_frame = tk.Frame(frame, bg=_BACKGROUND, width=length * 0.9)
    order_frame.pack(side=tk.LEFT, anchor=tk.CENTER, fill=tk.X)

    # Return components to update
    return timer, order_frame


def create_game_screen(window, length, grid_length, grid_width, *controls):
    """
    This function takes in the current window and creates the game scren on it.
    It creates and displays the new game screen, replacing any previous screens.

    Next, the function takes in the dimensions of the grid-based system for the game.
    It generates the map based on the grid-based system.
    
    Next, the function then accounts for the number of sets of player controls.
    It creates the appropriate number of players and binds all controls.

    Finally, the function starts the game updating process to refresh each frame of the game.

    @example
    window = tk.Tk()
    # Create one player
    create_game_screen(window, 50, 10, 6, _P1)

    @example
    window = tk.Tk()
    # Create multiple players
    create_game_screen(window, 50, 10, 6, _P1, _P2)

    @example
    window = tk.Tk()
    # Create window of different size and dimensions
    create_game_screen(window, 20, 20, 12, _P1, _P2)
    """
    clear_window(window)
    screen_length = length * grid_length
    game_width = length * grid_width

    # Split the screen into two parts: the information screen and the game screen
    timer, order_frame = create_info_screen(window, screen_length, 5 * 60 * 1000)
    window.geometry(f'{screen_length}x{round(game_width*1.1)}')
    game_screen = tk.Canvas(window, bg='white', width=screen_length, height=game_width)
    game_screen.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.BOTH)

    # Create objects
    placeholders, \
        blocks, \
        chopping_blocks, \
        cooking_blocks, \
        individual_blocks = generate_map(game_screen, length, grid_length, grid_width, 0.5)

    # Create players
    players = {}
    for fill in _COLOURS[:len(controls)]:
        coord = random.randint(0, grid_length * grid_width - 1)
        row, col = divmod(coord, grid_length)
        while (row, col) in placeholders or \
                (row, col) in blocks or \
                (row, col) in chopping_blocks or \
                (row, col) in cooking_blocks or \
                (row, col) in individual_blocks or \
                (row, col) in players:
            coord = random.randint(0, grid_length * grid_width - 1)
            row, col = divmod(coord, grid_length)
        players[(row, col)] = Player(game_screen,
                                     (col + (1 - _PLAYER_SIZE_PERCENT) / 2) * length,
                                     (row + (1 - _PLAYER_SIZE_PERCENT) / 2) * length,
                                     _PLAYER_SIZE_PERCENT * length,
                                     fill=fill)

    # Bind movement
    players = list(players.values())
    bind_player_controls(window, players, controls)
    game_screen.focus_set()

    # Update each frame accordingly
    update_game_frame(grid_length, grid_width,
                      window, timer,
                      players, controls,
                      {**placeholders, **blocks, **chopping_blocks, **cooking_blocks, **individual_blocks},
                      list(chopping_blocks.values()) + list(cooking_blocks.values()))


def create_main_menu(window, length, width):
    """
    This function takes in the current window and creates the main menu on it.
    It creates and displays the new main menu, replacing any previous screens.

    @example
    window = tk.Tk()
    create_main_menu(window, 500, 300)  # displays the main menu
    window.mainloop()
    """
    clear_window(window)
    window.geometry(f'{length}x{width}')
    frame = tk.Frame(window, bg=_BACKGROUND, width=length, height=width)
    frame.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.BOTH)

    # Display the game title
    title_label = tk.Label(frame, bg=_BACKGROUND, width=length, text=_GAME_NAME, font=('Arial', 25))
    title_label.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X, expand=True)

    # Display the character preview
    # By default, the number of characters to display is 2
    character_frame = tk.Frame(frame, bg=_BACKGROUND, width=length)
    character_frame.pack(side=tk.TOP, anchor=tk.CENTER, fill=tk.X, expand=True)


"""
Main menu function
"""


def main():
    """
    This function initialises the Tkinter window used to display the full program.
    It then directs control to other functions to create new screens or perform updates.
    """
    # Initialise the window
    window = tk.Tk()
    window.title(_GAME_NAME)
    window.resizable(False, False)

    """
    # Create the main menu
    create_main_menu(window, 500, 300)
    """

    # Create the game screen
    create_game_screen(window, 45, 10, 6, _P1, _P2)

    # Allow refresh
    window.mainloop()


if __name__ == '__main__':
    """
    This is where the code starts running when the python file is run
    """
    # Disable automatic key repeat
    # https://stackoverflow.com/questions/27215326/tkinter-keypress-and-keyrelease-events
    os.system('xset r off')
    main()
    # Enable automatic key repeat
    os.system('xset r on')
