from soldat_extmod_api.graphics_helper.color import Color, WHITE
from soldat_extmod_api.graphics_helper.vector_utils import Vector2D
from soldat_extmod_api.graphics_helper.sm_image_linkedlist import ImageNode
from soldat_extmod_api.graphics_helper.sm_text import InterfaceText
from soldat_extmod_api.graphics_helper.sm_text import TEXT_MAX_LENGTH
from soldat_extmod_api.event_dispatcher import Event
from pynput.keyboard import Key
import math


SLIDER_DEFAULT_COLOR = WHITE
SLIDER_FILLED_COLOR = Color(0x67, 0x67, 0x67, "100%")
SLIDER_KNOB_DEFAULT_COLOR = Color(0xBD, 0xBD, 0xBD, "100%")
SLIDER_KNOB_HOVER_COLOR = Color(0xAA, 0xAA, 0xAA, "100%")
SLIDER_KNOB_PRESSED_DEFAULT_COLOR = Color(0x9E, 0x9E, 0x9E, "100%")
SLIDER_BACK_DEFAULT_COLOR = Color(0, 0, 0, "50%")

BUTTON_BACK_DEFAULT_COLOR = Color(0, 0, 0, "50%")
BUTTON_DEFAULT_COLOR = WHITE
BUTTON_HOVER_DEFAULT_COLOR = Color(0xAA, 0xAA, 0xAA, "100%")
BUTTON_PRESSED_DEFAULT_COLOR = Color(0x6E, 0x6E, 0x6E, "100%")


class Rectangle:
    def __init__(self, position: Vector2D, dimensions: Vector2D, scale: Vector2D):
        self.position = position
        self.dimensions = dimensions
        self.scale = scale

    def contains_point(self, point: Vector2D) -> bool:
        """
        Returns True if the point falls within the rectangle, False otherwise.
        """
        x = point.x
        y = point.y
        if x >= self.corner_top_left.x and x <= self.corner_top_right.x and \
           y <= self.corner_bottom_left.y and y >= self.corner_top_left.y:
            return True
        else:
            return False

    @property
    def corner_top_left(self):
        return self.position
    
    @property
    def corner_top_right(self):
        return Vector2D(self.position.x + (self.dimensions.x * self.scale.x), self.position.y)
    
    @property
    def corner_bottom_right(self):
        return Vector2D(self.corner_top_right.x, self.position.y + (self.dimensions.y * self.scale.x))
    
    @property
    def corner_bottom_left(self):
        return Vector2D(self.corner_top_left.x, self.position.y + (self.dimensions.y * self.scale.x))

    def rect_set_pos(self, pos: Vector2D):
        self.position = pos


class DynamicRectangle:
    def __init__(self, position: Vector2D, dimensions: Vector2D, scale: Vector2D, rotation: float = 0.0, pivot: Vector2D = None):
        self.position = position
        self.dimensions = dimensions
        self.scale = scale
        self.rotation = rotation
        if pivot is None:
            self.pivot = Vector2D(
                self.position.x + (self.dimensions.x * self.scale.x) / 2,
                self.position.y + (self.dimensions.y * self.scale.x) / 2
            )
        else:
            self.pivot = pivot

    def contains_point(self, point: Vector2D) -> bool:
        """
        Returns True if the point falls within the rectangle, False otherwise.
        Handles both axis-aligned and rotated rectangles.
        Position is always top-left. Pivot is relative to top-left.
        """
        if self.rotation == 0:
            # Axis-aligned, X increases right, Y increases downward
            x = point.x
            y = point.y
            return (x >= self.position.x and 
                    x <= self.position.x + self.dimensions.x * self.scale.x and
                    y >= self.position.y and 
                    y <= self.position.y + self.dimensions.y * self.scale.x)
        else:
            translated_point = Vector2D(point.x - self.pivot.x, point.y - self.pivot.y)
            cos_neg = math.cos(self.rotation)
            sin_neg = math.sin(self.rotation)
            rotated_point = Vector2D(
                translated_point.x * cos_neg - translated_point.y * sin_neg,
                translated_point.x * sin_neg + translated_point.y * cos_neg
            )
            local_point = Vector2D(
                rotated_point.x + self.pivot.x,
                rotated_point.y + self.pivot.y
            )
            return (local_point.x >= self.position.x and 
                    local_point.x <= self.position.x + self.dimensions.x * self.scale.x and
                    local_point.y >= self.position.y and 
                    local_point.y <= self.position.y + self.dimensions.y * self.scale.x)

    def rotate_point(self, point: Vector2D, angle: float, pivot: Vector2D) -> Vector2D:
        """
        Rotate a point around a pivot by the given angle (invert direction for Y-down).
        """
        translated_point = Vector2D(point.x - pivot.x, point.y - pivot.y)
        cos_angle = math.cos(-angle)
        sin_angle = math.sin(-angle)
        rotated_point = Vector2D(
            translated_point.x * cos_angle - translated_point.y * sin_angle,
            translated_point.x * sin_angle + translated_point.y * cos_angle
        )
        return Vector2D(rotated_point.x + pivot.x, rotated_point.y + pivot.y)

    def get_corner(self, corner_name: str) -> Vector2D:
        """
        Get a specific corner of the rectangle, accounting for rotation.
        corner_name can be: 'top_left', 'top_right', 'bottom_right', 'bottom_left'
        Position is always top-left.
        """
        base_corners = {
            'top_left': self.position,
            'top_right': Vector2D(self.position.x + (self.dimensions.x * self.scale.x), self.position.y),
            'bottom_right': Vector2D(self.position.x + (self.dimensions.x * self.scale.x), 
                                   self.position.y + (self.dimensions.y * self.scale.x)),
            'bottom_left': Vector2D(self.position.x, self.position.y + (self.dimensions.y * self.scale.x))
        }
        if corner_name not in base_corners:
            raise ValueError(f"Invalid corner name: {corner_name}. Must be one of: {list(base_corners.keys())}")
        base_corner = base_corners[corner_name]
        if self.rotation == 0:
            return base_corner
        else:
            return self.rotate_point(base_corner, self.rotation, self.pivot)

    def rect_set_pos(self, pos: Vector2D):
        pivot_offset = Vector2D(
            self.pivot.x - self.position.x,
            self.pivot.y - self.position.y
        )
        self.position = pos
        self.pivot = Vector2D(
            pos.x + pivot_offset.x,
            pos.y + pivot_offset.y
        )

    def set_rotation(self, rotation: float):
        """
        Set the rotation angle in radians.
        """
        self.rotation = rotation

    def set_pivot(self, pivot: Vector2D):
        """
        Set the pivot point for rotation.
        """
        self.pivot = pivot

    def rotate(self, angle: float):
        """
        Rotate the rectangle by the given angle (in radians) around the current pivot.
        """
        self.rotation += angle

class Frame:
    def __init__(self, width: int = 853, height: int = 480, centered: bool = True):
        if centered:
            self.position = Vector2D(width / 2, height / 2)
        else:
            self.position = Vector2D(0, 0)
        self.dimensions = Vector2D(0, 0)
        self.scale = Vector2D(1, 1)


class UIElement(Rectangle):
    def __init__(self, parent, padding_x: float, padding_y: float, image: ImageNode, centered: bool = True):
        self.parent = parent
        self.padding = Vector2D(padding_x, padding_y)
        self.image = image
        self.dimensions = image.get_dimensions
        self.scale = image.get_scale
        self.pivot = Vector2D(0, 0)
        self.position = parent.position.add(self.padding)
        self.local_center = self.calc_local_center()
        if centered:
            self.pivot = self.local_center
            self.position = parent.position.add(self.padding).add(self.pivot)
        self.set_pos(self.position)
        super().__init__(self.position, self.dimensions, self.scale)

    def calc_local_center(self) -> Vector2D:
        return Vector2D((self.parent.dimensions.x * self.parent.scale.x / 2) - (self.dimensions.x * self.scale.x / 2),
                        (self.parent.dimensions.y * self.parent.scale.x / 2) - (self.dimensions.y * self.scale.x / 2))
    
    def set_pos(self, pos: Vector2D):
        self.rect_set_pos(pos)
        self.position = pos
        self.image.set_pos(pos)
    
class Container(UIElement):
    def __init__(self, parent, padding_x: float, padding_y: float, image: ImageNode, centered: bool = True):
        super().__init__(parent, padding_x, padding_y, image, centered)

class TextLabel(UIElement):
    def __init__(self, parent, text: InterfaceText, padding_x: float, padding_y: float, text_padding_x: float, text_padding_y: float, image: ImageNode):
        super().__init__(parent, padding_x, padding_y, image, False)
        self.text = text
        if isinstance(parent, TextLabel):
            self.set_pos(self.parent.corner_bottom_left.add(Vector2D(padding_x, padding_y)))
            self.text.set_pos(self.position.add(Vector2D(2, (self.corner_bottom_left.y - self.corner_top_left.y) * self.scale.y / 2)).\
                              add(Vector2D(text_padding_x, text_padding_y)))
        elif isinstance(parent, Frame):
            self.set_pos(self.parent.position.add(self.padding))
            self.text.set_pos(self.position.add(Vector2D(2,1)))
        else:
            self.set_pos(self.parent.corner_top_left.add(Vector2D(padding_x, padding_y)))
            self.text.set_pos(self.position.add(Vector2D(2, (self.corner_bottom_left.y - self.corner_top_left.y) * self.scale.y / 2)).\
                              add(Vector2D(text_padding_x, text_padding_y)))
        

    def update_text(self, new_text: str):
        self.text.set_text(new_text)

class Interactive:
    def __init__(self, mod_api):
        self.api = mod_api
        self.subscribe()

    def subscribe(self):
        self.api.subscribe_event(self.on_click, Event.MOUSE_DOWN)
        self.api.subscribe_event(self.on_mouse_release, Event.MOUSE_UP)
        self.api.subscribe_event(self.on_hover, Event.MOUSE_HOVER)

    def unsubscribe(self):
        self.api.unsubscribe_event(self.on_click, Event.MOUSE_DOWN)
        self.api.unsubscribe_event(self.on_mouse_release, Event.MOUSE_UP)
        self.api.unsubscribe_event(self.on_hover, Event.MOUSE_HOVER)

    def on_click(self, position: Vector2D):
        return position
    
    def on_mouse_release(self, position: Vector2D):
        return position

    def on_hover(self, position: Vector2D):
        return position


class TextField(Interactive, TextLabel):
    def __init__(self, mod_api, parent, text, padding_x, padding_y, text_padding_x, text_padding_y, image, max_text: int = TEXT_MAX_LENGTH):
        super().__init__(mod_api)
        TextLabel.__init__(self, parent, text, padding_x, padding_y, text_padding_x, text_padding_y, image)
        self.max_text = max_text
        self.is_writing = False
        self.input_text = ""
        self.cursor_position = 0
        self.shift_down = False
        self.capslock_toggled = False
        self.alt_down = False

    def subscribe(self):
        self.api.subscribe_event(self.on_anykbkey_down, Event.KEYBOARD_KEYDOWN)
        self.api.subscribe_event(self.on_anykbkey_up, Event.KEYBOARD_KEYUP)
        self.api.subscribe_event(self.on_internal_keypress, Event.INTERNAL_KEYPRESS)
        return super().subscribe()

    def unsubscribe(self):
        self.api.unsubscribe_event(self.on_anykbkey_down, Event.KEYBOARD_KEYDOWN)
        self.api.unsubscribe_event(self.on_anykbkey_up, Event.KEYBOARD_KEYUP)
        self.api.unsubscribe_event(self.on_internal_keypress, Event.INTERNAL_KEYPRESS)
        return super().unsubscribe()

    def on_anykbkey_down(self, key):
        if self.is_writing:
            char = ""
            if isinstance(key, Key):
                if key == Key.backspace:
                    if self.cursor_position > 0:
                        self.input_text = self.input_text[:self.cursor_position - 1] + self.input_text[self.cursor_position:]
                        self.cursor_position -= 1
                        self.update_text(self.input_text)
                        return
                elif key == Key.space:
                    char = " "
                elif key == Key.shift or key == Key.shift_l or key == Key.shift_r:
                    self.shift_down = True
                elif key == Key.alt or key == Key.alt_gr or key == Key.alt_l or key == Key.alt_r:
                    self.alt_down = True
            elif self.capslock_toggled:
                char = key.char.upper()
            elif not self.shift_down and not self.alt_down:
                char = key.char
            
            if len(self.input_text) < self.max_text and char != "":
                self.input_text = self.input_text[:self.cursor_position] + char + self.input_text[self.cursor_position:]
                self.cursor_position += 1
                self.update_text(self.input_text)

    def on_internal_keypress(self, key):
        if self.is_writing:
            if self.shift_down or self.alt_down:
                if len(self.input_text) < self.max_text:
                    self.input_text = self.input_text[:self.cursor_position] + key + self.input_text[self.cursor_position:]
                    self.cursor_position += 1
                self.update_text(self.input_text)

    def on_anykbkey_up(self, key):
        if isinstance(key, Key):
            if key == Key.caps_lock:
                self.capslock_toggled ^= True
            elif key == Key.shift or key == Key.shift_l or key == Key.shift_r:
                self.shift_down = False
            elif key == Key.alt or key == Key.alt_gr:
                self.alt_down = False

    def update_text(self, text, show_cursor: bool = True):
        if show_cursor:
            txt = text[:self.cursor_position] + "|" + text[self.cursor_position:]
        else:
            txt = text
        super().update_text(txt)

    def __handle_on_mdown(self, pos: Vector2D):
        pass

    def __handle_on_mup(self, pos: Vector2D):
        self.is_writing = self.contains_point(pos)
        if self.is_writing:
            self.cursor_position = len(self.input_text)

    def __handle_on_hover(self, pos): # optimize
        pass

    def on_click(self, position: Vector2D):
        self.__handle_on_mdown(super().on_click(position))

    def on_mouse_release(self, position: Vector2D):
        self.__handle_on_mup(super().on_mouse_release(position))

    def on_hover(self, position: Vector2D):
        self.__handle_on_hover(super().on_hover(position))

class Button(Interactive, UIElement):
    def __init__(self, mod_api, parent, padding_x: float, padding_y: float, image: ImageNode, centered: bool = True):
        super().__init__(mod_api)
        UIElement.__init__(self, parent, padding_x, padding_y, image, centered)
        self.cursor_inside = False

    def on_click(self, position: Vector2D):
        return position

    def on_mouse_release(self, position: Vector2D):
        return position
    
    def on_hover(self, position: Vector2D):
        is_inside = self.contains_point(position)
        if not self.cursor_inside and is_inside:
            self.cursor_inside = True
            self.on_cursor_enter()
        if self.cursor_inside and not is_inside:
            self.cursor_inside = False
            self.on_cursor_exit()
    
    def on_cursor_enter(self):
        pass
    
    def on_cursor_exit(self):
        pass

class Checkbox(Interactive, UIElement):
    def __init__(self, mod_api, parent, padding_x: float, padding_y: float, image: ImageNode, centered: bool = True):
        super().__init__(mod_api)
        UIElement.__init__(self, parent, padding_x, padding_y, image, centered)
        self.checked_color = Color.from_bytes(b"\x9c\x9c\x9c\xff")
        self.unchecked_color = Color.from_bytes(b"\xee\xee\xee\xff")
        self.image.set_color(self.unchecked_color)
        self.checked = False

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            self.checked ^= True
            if self.checked: self.image.set_color(self.checked_color)
            else: self.image.set_color(self.unchecked_color)

class PauseButton(Button):
    def __init__(self, mod_api, 
                 parent, 
                 padding_x: float, 
                 padding_y: float, 
                 image_playing: ImageNode, 
                 image_paused: ImageNode, 
                 centered: bool = True):
        super().__init__(mod_api, parent, padding_x, padding_y, image_playing, centered)
        self.image_playing = image_playing
        self.image_paused = image_paused

        self.image_paused.set_pos(self.position)
        self.image_playing.toggle()

        self.image_paused.set_color(BUTTON_DEFAULT_COLOR)
        self.image_playing.set_color(BUTTON_DEFAULT_COLOR)
        self.paused = True

    def __handle_on_mdown(self, pos: Vector2D):
        if self.contains_point(pos):
            self.image.set_color(BUTTON_PRESSED_DEFAULT_COLOR)
            self.image_paused.set_color(BUTTON_PRESSED_DEFAULT_COLOR)

    def __handle_on_mup(self, pos: Vector2D):
        contains = self.contains_point(pos)
        if contains:
            if self.paused:
                self.play()
            else:
                self.pause()
        return contains

    def pause(self):
        self.paused = True
        self.image_paused.show()
        self.image_playing.hide()
        self.image.set_color(BUTTON_DEFAULT_COLOR)
        self.image_paused.set_color(BUTTON_DEFAULT_COLOR)

    def play(self):
        self.paused = False
        self.image_paused.hide()
        self.image_playing.show()
        self.image.set_color(BUTTON_DEFAULT_COLOR)
        self.image_paused.set_color(BUTTON_DEFAULT_COLOR)

    def on_cursor_enter(self):
        self.image_playing.set_color(BUTTON_HOVER_DEFAULT_COLOR)
        self.image_paused.set_color(BUTTON_HOVER_DEFAULT_COLOR)

    def on_cursor_exit(self):
        self.image_playing.set_color(BUTTON_DEFAULT_COLOR)
        self.image_paused.set_color(BUTTON_DEFAULT_COLOR)

    def on_click(self, position: Vector2D):
        self.__handle_on_mdown(super().on_click(position))

    def on_mouse_release(self, position: Vector2D):
        return self.__handle_on_mup(super().on_mouse_release(position))

    def hide(self):
        self.image_playing.hide()
        self.image_paused.hide()

    def show(self):
        if not self.paused:
            self.image_playing.show()
        else:
            self.image_paused.show()

class SliderContainer(Container):
    def __init__(self, parent, padding_x: float, padding_y: float, image: ImageNode, centered: bool = True):
        super().__init__(parent, padding_x, padding_y, image, centered)
        self.image.set_color(SLIDER_BACK_DEFAULT_COLOR)

class SliderBar(Interactive, UIElement):
    def __init__(self, mod_api, parent, padding_x: float, padding_y: float, image: ImageNode, slider_filled: ImageNode, centered: bool = True):
        super().__init__(mod_api)
        UIElement.__init__(self, parent, padding_x, padding_y, image, centered)
        self.dragging = False
        self.knob: SliderKnob = None
        self.image.set_color(SLIDER_DEFAULT_COLOR)
        self.slider_filled = slider_filled
        self.slider_filled.set_pos(self.position)
        self.slider_filled.set_color(Color("40%", "40%", "40%", "100%"))
        self.slider_filled.set_scale(Vector2D(0, 0.5))

    def __handle_on_hover(self, pos: Vector2D): #optimize, mouse enter and exit instead of hover
        if self.knob.contains_point(pos):
            self.knob.image.set_color(SLIDER_KNOB_HOVER_COLOR)

    def __handle_on_mup(self, pos: Vector2D):
        self.dragging = False
        self.knob.image.set_color(SLIDER_KNOB_DEFAULT_COLOR)

    def __handle_on_mdown(self, pos: Vector2D):
        if not self.dragging:
            if self.contains_point(pos):
                perc_from_pos = self.knob.pos_to_percentage(pos.x)
                self.slider_filled.set_scale(Vector2D((perc_from_pos / self.slider_filled.get_dimensions.x) + 0.01, 0.5))
                self.knob.index = int(perc_from_pos)
                self.dragging = True
                self.knob.image.set_color(SLIDER_KNOB_PRESSED_DEFAULT_COLOR)
        else:
            perc_from_pos = self.knob.pos_to_percentage(min(max(pos.x, self.corner_top_left.x), self.corner_top_right.x - self.local_center.x))
            self.knob.index = int(perc_from_pos)

    def on_click(self, position: Vector2D):
        self.__handle_on_mdown(super().on_click(position))
    
    def on_mouse_release(self, position: Vector2D):
        self.__handle_on_mup(super().on_mouse_release(position))

    def on_hover(self, position: Vector2D):
        self.__handle_on_hover(super().on_hover(position))


class SliderKnob(UIElement):
    def __init__(self, parent: SliderBar, padding_x: float, padding_y: float, image: ImageNode, percentage: float):
        super().__init__(parent, padding_x, padding_y, image, False)
        self.image.set_color(SLIDER_KNOB_DEFAULT_COLOR)
        if percentage > 100:
            self.percentage = 100
        else:
            self.percentage = percentage
        self.parent = parent
        self.increment_val = (((self.parent.dimensions.x - self.dimensions.x) - self.parent.padding.x) * parent.scale.x) / 100
        self.percentage = self.percentage * self.increment_val
        self.parent.knob = self
        self.index = 0

    def update_percentage(self, percentage: float):
        percent = self.increment_val * percentage
        self.set_pos(Vector2D(self.parent.position.x + percent, self.position.y))
        self.parent.slider_filled.set_scale(Vector2D((percent / self.parent.slider_filled.get_dimensions.x) + 0.01, 0.5))

    def map_percentage(self, length: int):
        self.increment_val = (((self.parent.dimensions.x - self.dimensions.x) - self.parent.padding.x) * self.parent.scale.x) / length

    def pos_to_percentage(self, click_pos):
        percentage = (click_pos - self.parent.position.x) / self.increment_val
        return percentage

'''
TODO: Add graphics reloading, do it while avoiding race hazards.
'''