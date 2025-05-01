import os
from pathlib import Path
from typing import Tuple, Any, Set

import pygame as pg

from animation import Frame, AnimatedObject
from base import ResizableObject
from utils import LinkObject
from utils.builders import ParticleBuilder, Color
from utils.consts import COLOR_DEPTH, DEFAULT_COLOR_DEPTH


class Heart(ResizableObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amplitude = 1

    def bump(self, _time: float, intensity: float):
        k = round(1 + intensity, 2)
        self.resize_image((
            width := self.width * k,
            height := self.height * k
        ), False)
        self.x = -(width - self.width) // 2
        self.y = -(height - self.height) // 2

    def draw(self, _time: float, intensity: float):
        self.bump(_time, intensity)
        super().draw()


class Button(Frame):
    def __init__(self, *args, text: str, data: Any, font: LinkObject, **kwargs):
        super().__init__(*args, **kwargs)
        self.text, self.__font = text, font
        self.data = data
        if (function := kwargs.get("function")) is None:
            self.function = lambda *func_args, **func_kwargs: None
        else:
            self.function = function

    @property
    def font(self):
        return self.__font.value

    @font.setter
    def font(self, value):
        self.__font.value = value

    @property
    def label(self):
        return self.font.render(self.text, 1.5, self.color)

    @property
    def text_rect(self):
        return pg.Rect(
            self.x + self.margin_x + (self.width - (width := self.label.get_width())) // 2,
            self.y + self.margin_y + (self.height - (height := self.label.get_height())) // 2,
            width, height
        )

    def draw(self, *args):
        super().draw(*args)
        self.surface.blit(self.label, self.text_rect)

    def click(self, data: Any = None):
        self.function(data=data if data else self.data)


class Square(Button):
    def __init__(self, *args, **kwargs):
        self.fill_color = (0, 0, 0, 0)
        super().__init__(*args, **kwargs)

    def resize_image(self, *args):
        super().resize_image(*args)
        self.image.fill(self.fill_color)

    def draw(self, *args):
        super().draw(*args)

    def __str__(self):
        return f"({self.x}, {self.y})"


def collide_condition(object: ResizableObject, coords: Tuple[int, int]):
    return all([
        object.x + object.margin_x <= coords[0] <= object.x + object.width + object.margin_x,
        object.y + object.margin_y <= coords[1] <= object.y + object.height + object.margin_y
    ])


class Grid(list):

    def __init__(self, surface: pg.Surface, pad_procent: float = 0.0625):
        super().__init__(self)
        self.surface = surface
        self.surface_size = (None, None)
        self.hovered = None
        self.scroll_offset = 0
        self.max_height = 0
        self.pad_procent = pad_procent

    def draw(self, _time: float):
        width = self.surface.get_width()
        y = padding = self.pad_procent * width
        for frames in list(zip(self[0::2], self[1::2])) + ([[self[-1]]] if len(self) % 2 == 1 else []):
            max_height = 0
            for is_last, frame in enumerate(frames):
                max_height = frame.height if max_height < frame.height else max_height
                x = padding if not is_last else width - padding - frame.width
                frame.x, frame.y = (x, y + self.scroll_offset)
                frame.draw(_time if self.hovered == frame else -_time)
            y += padding + max_height
        self.max_height = y

    def scroll(self, offset: int):
        next_height = self.surface.get_height() + -self.scroll_offset + -offset
        if (next_height <= self.max_height and offset < 0) or (self.surface.get_height() <= next_height and offset > 0):
            self.scroll_offset += offset

    def check_collision(self, coords: Tuple[int, int]) -> bool:
        for frame in self:
            if collide_condition(frame, coords):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
                self.hovered = frame
                frame.activate()
                return True
        self.hovered = None
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
        return False

    def check_clicked(self, coords: Tuple[int, int], tracker: list = None, *args, **kwargs):
        for frame in self:
            buttons = frame.buttons + ([frame] if isinstance(frame, Button) else [])
            for button in buttons:
                if collide_condition(button, coords):
                    if tracker and not tracker[-1].get(button):
                        tracker[-1][button] = button.fill_color
                    button.click(*args, **kwargs)
                    return True


class Level(Grid):

    def __init__(self, frame: Frame, particles: int, path: Path, builder: ParticleBuilder, **kwargs):
        super().__init__(frame.surface)
        self.append(frame)

        font = LinkObject(pg.font.SysFont("monospace", 24))

        self.builder = builder
        self.__colors = self.builder.build(
            self.frame, particles,
            int(os.environ.get(COLOR_DEPTH, DEFAULT_COLOR_DEPTH)),
            path, font=font, **kwargs
        )
        frame.set_button(*self.builder.particles)

        self.frame.resize_image((
            self.builder.size * self.builder.row,
            self.builder.size * self.builder.column
        ))

    @property
    def frame(self):
        return self[0] if self else None

    def colors(self) -> Set[Color]:
        return self.__colors

    def move_frame(self, start: Tuple[int, int], stop: Tuple[int, int]):
        if collide_condition(self.frame, start):
            self.frame.x += stop[0] - start[0]
            self.frame.y += stop[1] - start[1]

    def zoom(self, k: float):
        size = (self.frame.width, self.frame.height)

        width = int(size[0] * k) // self.builder.row * self.builder.row
        height = int(size[1] * k) // self.builder.column * self.builder.column

        square_width = self.builder.first.width + (width - size[0]) // self.builder.row
        square_height = self.builder.first.height + (height - size[1]) // self.builder.column

        if 50 < square_width:
            square_width, square_height, width, height = 50, 50, self.builder.row * 50, self.builder.column * 50
        elif 5 > square_width:
            square_width, square_height, width, height = 5, 5, self.builder.row * 5, self.builder.column * 5

        self.frame.resize_image((width, height))
        self.builder.rebuild((square_width, square_height))
        self.builder.first.font = pg.font.SysFont("monospace", int(self.builder.first.width / 1.6))
        self.frame.centre()

    def draw(self, _delta: float):
        super().draw(_delta)
