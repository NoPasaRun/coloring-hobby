from application import pg
from typing import Callable, List, Tuple

from application.utils.enums import BezierFunctions
from application.base import ResizableObject


def check_active(func: Callable):
    def wrapper(self: AnimatedObject, *args, **kwargs):
        if self.active:
            self.set_time(*args)
            return func(self, *args, **kwargs)

    return wrapper


def color_generator():
    palette = [220, 180, 160]
    while True:
        for x in palette:
            for y in palette:
                for z in palette:
                    yield [x, y, z]


class AnimatedObject(ResizableObject):
    def __init__(self, *args, animation_time: float = 0.5, function=BezierFunctions.ease_out, **kwargs):
        super().__init__(*args, **kwargs)
        self.function = function
        self.animation_time = animation_time
        self.current_time = 0

    @property
    def active(self):
        return self.current_time > 0

    def activate(self):
        if self.current_time <= 0:
            self.current_time = 0.001

    def set_time(self, _time: float):
        if self.current_time + _time <= self.animation_time:
            self.current_time += _time
        else:
            self.current_time = self.animation_time

    def get_next_value(self, start: float, stop: float):
        p2 = self.function.value[0][1]
        p3 = self.function.value[1][1]
        t = self.current_time / self.animation_time

        y = 3 * (1 - t) ** 2 * t * p2 + 3 * (1 - t) * t ** 2 * p3 + t ** 3
        return start + (stop - start) * y

    def draw(self, *args):
        super().draw(*args)


class Frame(AnimatedObject):
    colors = iter(color_generator())

    def __init__(self, *args, width: int,
                 first_color: List[int],
                 second_color: List[int] = None,
                 border_width: int = 5, **kwargs
                 ):
        super().__init__(*args, **kwargs)
        ratio = self.image.get_width() / self.image.get_height()
        self.resize_image((width, width / ratio))
        self.border_width = border_width
        self.__first_color, self.__second_color = first_color, second_color
        if self.__second_color:
            self.default_colors = (self.__first_color[::], self.__second_color[::])
        self.__buttons = []

    @property
    def first_color(self):
        return self.__first_color

    @first_color.setter
    def first_color(self, value: List[int]):
        self.__first_color = value

    @property
    def second_color(self):
        if self.__second_color is not None:
            return self.__second_color
        return self.__first_color

    @property
    def color(self):
        return self.__first_color

    def set_button(self, *buttons):
        if isinstance(self, Frame):
            self.__buttons.extend(buttons)
            for button in buttons:
                button.x, button.y = self.x, self.y

    @property
    def buttons(self):
        return self.__buttons

    @check_active
    def set_animation(self, _time: float):
        for x in range(3):
            for y, color in enumerate([self.first_color, self.second_color]):
                color[x] = self.get_next_value(
                    self.default_colors[0 ^ y][x],
                    self.default_colors[1 ^ y][x]
                )

    def fill(self, main_color: Tuple, add_color: Tuple, padding: int = 0):
        color_rect = pg.Surface((2, 2), pg.SRCALPHA)
        pg.draw.line(color_rect, main_color, (0, 0), (1, 0))
        pg.draw.line(color_rect, add_color, (0, 1), (1, 1))
        color_area = pg.Rect(
            self.x - padding + self.margin_x,
            self.y - padding + self.margin_y,
            self.width + padding * 2,
            self.height + padding * 2
        )
        color_rect = pg.transform.smoothscale(color_rect, (color_area.width, color_area.height))
        color_rect.fill((0, 0, 0, 0), (padding, padding, self.width, self.height))
        self.surface.blit(color_rect, color_area)

    def draw(self, _time: float = 0, *args):
        if hasattr(self, "default_colors"):
            self.set_animation(_time)
        if self.border_width > 0:
            self.fill(self.first_color, self.second_color, self.border_width)
        super().draw(*args)
        if self.active:
            for button in self.buttons:
                button.x, button.y = self.x, self.y
                button.draw()


class Transition(AnimatedObject):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def activate(self):
        self.current_time = 0.001
        self.x = -self.width

    @property
    def active(self):
        return self.animation_time > self.current_time > 0

    @check_active
    def set_animation(self, _time: float):
        self.x = self.get_next_value(st := -self.width+self.margin_x, abs(st))

    def draw(self, _time: float, *args):
        super().draw(*args)
        self.set_animation(_time)
