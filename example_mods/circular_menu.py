from soldat_extmod_api.mod_api import *
from soldat_extmod_api.graphics_helper.math_utils import lerpf, radians, cos, sin
from soldat_extmod_api.graphics_helper.sm_text import CharacterSize, FontStyle
from soldat_extmod_api.graphics_helper.gui_addon import Container, Interactive, Rectangle, Button
import time


class CircularMenu(Container, Interactive):
    def __init__(self, mod_api: ModAPI, parent: Frame):
        self.mod_api = mod_api
        self.button_1 = AccountMenuButton(parent, mod_api)
        self.top_panel_button = TopPanelToggleMenuButton(parent, mod_api)
        self.button_3 = AccountMenuButton(parent, mod_api)
        self.button_4 = AccountMenuButton(parent, mod_api)
        self.button_5 = AccountMenuButton(parent, mod_api)
        self.buttons: list[CircularMenuButton] = [self.button_1, self.top_panel_button, self.button_3, self.button_4, self.button_5]
        image = mod_api.create_interface_image("rm_logo.png", scale=Vector2D(0.1, 0.1), color=BLACK)
        self.max_retraction_offset = 20
        self.max_protraction_offset = 60
        self.buttons_max_retraction_offset = 5
        self.buttons_max_protraction_offset = 60
        self.retracted_position_x_padding = parent.position.x - ((image.get_dimensions.x / 2) * 0.1) + self.max_retraction_offset
        self.retracted_position_y_padding = parent.position.y - ((image.get_dimensions.y / 2) * 0.1) - self.max_protraction_offset
        self.image_height_half = ((image.get_dimensions.y / 2) * 0.1)
        self.image_width_half = ((image.get_dimensions.x / 2) * 0.1)
        super().__init__(parent, self.retracted_position_x_padding, self.retracted_position_y_padding, image, True)
        Interactive.__init__(self, self.mod_api)
        self.button_center_offset_x = self.image_width_half - (self.button_1.image.get_dimensions.x / 2) * self.button_1.scale.x
        self.button_center_offset_y = self.image_height_half - (self.button_1.image.get_dimensions.y / 2) * self.button_1.scale.y
        self.dragging = False
        self.cursor_inside = False
        self.area_trigger_cursor_inside = False
        self.start_position = self.position.x
        self.target_position_x = self.position.x
        self.button_center_x = self.position.x + self.image_width_half - self.button_center_offset_x
        self.target_position_y = self.position.y
        self.target_color = BLACK
        self.update_delay = 0.01
        self.transition_smoothness = 0.1
        self.past_time = 0
        self.area_trigger = Rectangle(self.position.sub(Vector2D(65, 30)), self.dimensions, self.scale + Vector2D(0.2, 0.2))
        self.start_angle_rad = radians(210) # left cone
        self.end_angle_rad = radians(140)
        self.calculate_button_positions(initial=True)

    def on_hover(self, position: Vector2D):
        is_inside = self.contains_point(position)
        if not self.cursor_inside and is_inside:
            self.cursor_inside = True
            self.on_cursor_enter()
        if self.cursor_inside and not is_inside:
            self.cursor_inside = False

        is_inside = self.area_trigger.contains_point(position)
        if not self.area_trigger_cursor_inside and is_inside:
            self.area_trigger_cursor_inside = True
        if self.area_trigger_cursor_inside and not is_inside:
            self.area_trigger_cursor_inside = False
            self.on_area_trigger_cursor_exit()
        if self.dragging:
            self.target_position_y = position.y - self.image_height_half
    
    def on_click(self, position: Vector2D):
        if not self.dragging and self.contains_point(position):
            self.dragging = True

    def on_mouse_release(self, position: Vector2D):
        if self.dragging:
            self.dragging = False
            self.target_position_y = position.y - self.image_height_half
            self.calculate_button_positions()
            self.on_area_trigger_cursor_exit()

    def on_cursor_enter(self):
        self.target_position_x = self.start_position - 30
        self.target_color = WHITE
        for button in self.buttons:
            button.target_position = button.end_position

    def on_area_trigger_cursor_exit(self):
        if not self.dragging:
            self.target_position_x = self.start_position
            self.target_color = BLACK
            for button in self.buttons:
                button.target_position = button.start_position

    def update_transitions(self):
        now = time.perf_counter()
        if now - self.past_time >= self.update_delay:
            self.set_pos(Vector2D(lerpf(self.position.x, self.target_position_x, self.transition_smoothness),
                                  lerpf(self.position.y, self.target_position_y, self.transition_smoothness)))
            self.image.set_color(Color.lerp_color(self.image.get_color, self.target_color, self.transition_smoothness))
            for button in self.buttons:
                button.set_pos(Vector2D(lerpf(button.position.x, button.target_position.x, self.transition_smoothness),
                                        lerpf(button.position.y, button.target_position.y, self.transition_smoothness)))
            self.past_time = now

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "area_trigger"):
            self.area_trigger.position = Vector2D(self.area_trigger.position.x, pos.y - 20)
        super().set_pos(pos)

    def calculate_button_positions(self, initial: bool = False):
        num_points = len(self.buttons)
        for i in range(num_points):
            angle = self.start_angle_rad + (self.end_angle_rad - self.start_angle_rad) * i / (num_points - 1)
            angle_cos = cos(angle)
            angle_sin = sin(angle)
            x = self.button_center_x + self.buttons_max_retraction_offset * angle_cos
            y = self.target_position_y + self.image_height_half - self.button_center_offset_y + self.buttons_max_retraction_offset * angle_sin
            self.buttons[i].start_position = Vector2D(x, y)
            x = self.button_center_x + self.buttons_max_protraction_offset * angle_cos
            y = self.target_position_y + self.image_height_half - self.button_center_offset_y + self.buttons_max_protraction_offset * angle_sin
            self.buttons[i].end_position = Vector2D(x, y)
            if initial: self.buttons[i].target_position = self.buttons[i].start_position

    def debug_area_trigger(self):
        idbg_dot1 = self.mod_api.create_interface_image("dbg_dot.png", Vector2D(self.area_trigger.corner_top_left.x, self.area_trigger.corner_top_left.y))
        idbg_dot1 = self.mod_api.create_interface_image("dbg_dot.png", Vector2D(self.area_trigger.corner_top_right.x, self.area_trigger.corner_top_right.y))
        idbg_dot1 = self.mod_api.create_interface_image("dbg_dot.png", Vector2D(self.area_trigger.corner_bottom_left.x, self.area_trigger.corner_bottom_left.y))
        idbg_dot1 = self.mod_api.create_interface_image("dbg_dot.png", Vector2D(self.area_trigger.corner_bottom_right.x, self.area_trigger.corner_bottom_right.y))

class CircularMenuButton(Button):
    def __init__(self, mod_api: ModAPI, parent: Frame, icon_image_path: str, tooltip_text: str = "Default tooltip"):
        image = mod_api.create_interface_image("circle.png", scale=Vector2D(0.15, 0.15), color=BLACK)
        self.button_icon = mod_api.create_interface_image(icon_image_path, scale=Vector2D(0.35, 0.35))
        self.button_icon_half = Vector2D(((self.button_icon.get_dimensions.x / 2) * self.button_icon.get_scale.x) - ((image.get_dimensions.x / 2) * 0.15) ,
                                         ((self.button_icon.get_dimensions.y / 2) * self.button_icon.get_scale.y) - ((image.get_dimensions.y / 2) * 0.15) + 1)
        super().__init__(mod_api, parent, 0, 0, image, True)
        self.action: Callable = None
        self.start_position = Vector2D.zero()
        self.target_position = Vector2D.zero()
        self.end_position = Vector2D.zero()
        self.tooltip_text_scale = 0.7
        self.tooltip_text = tooltip_text
        self.tooltip_interface_text = mod_api.create_interface_text(tooltip_text, self.position, WHITE, BLACK, 1, Vector2D(0.7, 1.4), FontStyle.FONT_SMALL_BOLD, self.tooltip_text_scale)
        self.tooltip_interface_text.hide()
        self.text_center_offset = Vector2D(((len(self.tooltip_text) // 2) * (CharacterSize.FONT_SMALL_BOLD * self.tooltip_text_scale)) +
                                           ((len(self.tooltip_text) // 2) * (CharacterSize.FONT_SMALL_BOLD_SPACING * self.tooltip_text_scale)), 0)
        self.text_center_offset.y += 8

    def set_pos(self, pos: Vector2D):
        self.button_icon.set_pos(pos.sub(self.button_icon_half))
        return super().set_pos(pos)
    
    def on_hover(self, position: Vector2D):
        super().on_hover(position)
        if self.cursor_inside:
            self.tooltip_interface_text.set_pos(position.sub(self.text_center_offset))

    def on_cursor_enter(self):
        self.tooltip_interface_text.show()

    def on_cursor_exit(self):
        self.tooltip_interface_text.hide()

    def set_tooltip_text(self, text: str):
        self.text_center_offset = Vector2D(((len(self.tooltip_text) // 2) * (CharacterSize.FONT_SMALL_BOLD * self.tooltip_text_scale)) +
                                           ((len(self.tooltip_text) // 2) * (CharacterSize.FONT_SMALL_BOLD_SPACING * self.tooltip_text_scale)), 0)
        self.text_center_offset.y += 8
        
        self.tooltip_interface_text.set_text(text)
        self.tooltip_text = text

    def set_action_callback(self, callback: Callable):
        self.action = callback


class AccountMenuButton(CircularMenuButton):
    def __init__(self, parent: Frame, mod_api: ModAPI):
        super().__init__(mod_api, parent, "fa-user-solid.png", "Account")

class TopPanelToggleMenuButton(CircularMenuButton):
    def __init__(self, parent: Frame, mod_api: ModAPI):
        super().__init__(mod_api, parent, "fa-eye-solid.png", "Hide top panel")
        self.button_icon_toggled = mod_api.create_interface_image("fa-eye-slash-solid.png", scale=Vector2D(0.35, 0.35))
        self.button_icon_toggled.hide()
        self.toggled = False
        self.toggled_action = None

    def on_mouse_release(self, position: Vector2D):
        if self.contains_point(position):
            if self.toggled:
                self.button_icon_toggled.show()
                self.button_icon.hide()
                self.set_tooltip_text("Hide top panel")
                if self.toggled_action: self.toggled_action()
            else:
                self.button_icon_toggled.hide()
                self.button_icon.show()
                self.set_tooltip_text("Show top panel")
                if self.action: self.action()
            self.toggled ^= True

    def set_pos(self, pos: Vector2D):
        if hasattr(self, "button_icon_toggled"):
            self.button_icon_toggled.set_pos(pos.sub(self.button_icon_half))
        return super().set_pos(pos)
    
    def set_action_callback(self, callback: Callable):
        return super().set_action_callback(callback)
    
    def toggled_action_callback(self, callback: Callable):
        self.toggled_action = callback


class ModMain:
    def __init__(self):
        self.api = ModAPI()
        self.api.subscribe_event(self.on_dxready, Event.DIRECTX_READY)
        self.api.subscribe_event(self.on_lcontrol_down, Event.LCONTROL_DOWN)
        self.api.subscribe_event(self.on_lcontrol_up, Event.LCONTROL_UP)
        self.freeze_cam = False
        while True:
            try:
                if hasattr(self, "circular_menu"):
                    self.circular_menu.update_transitions()
                self.api.tick_event_dispatcher()
            except KeyboardInterrupt:
                break
            time.sleep(0.01)

    def on_dxready(self):
        self.circular_menu = CircularMenu(self.api, self.api.get_gui_frame())
        self.api.enable_drawing()

    def on_lcontrol_down(self):
        if not self.freeze_cam:
            self.api.take_cursor_controls()
            self.api.take_camera_controls()
            self.freeze_cam = True

    def on_lcontrol_up(self):
        self.api.restore_cursor_controls()
        self.api.restore_camera_controls()
        self.freeze_cam = False


if __name__ == "__main__":
    mod_main = ModMain()