from application import pg, Surface

import abc
import os
from pathlib import Path
from typing import Tuple


class Object(abc.ABC):
    def __init__(self, surface: Surface, path: Path, save_origin: bool = False):
        if not os.path.exists(path):
            raise FileNotFoundError("Provided path is wrong")
        self.surface = surface
        origin_image = pg.image.load(path)
        if save_origin:
            self.origin_image = origin_image
        self.__image = pg.transform.smoothscale(origin_image.convert_alpha(), origin_image.get_size())
        self.__rect = self.__image.get_rect()
        self.__fixed = False

    def set_pos(self, pos: Tuple):
        if not self.__fixed:
            self.__rect.x, self.__rect.y = pos
            self.__fixed = True

    @property
    def image(self):
        return self.__image

    def move_position(self, size: Tuple[int, int]):
        return self.x * (size[0] / self.width), self.y * (size[1] / self.height)

    def resize_image(self, size: Tuple[int, int], update_rect: bool = True):
        if hasattr(self, "origin_image"):
            origin_image = self.origin_image
        else:
            origin_image = self.image
        coords = self.move_position(size)
        self.__image = pg.transform.smoothscale(origin_image.convert_alpha(), size)
        if update_rect:
            self.__rect = self.image.get_rect()
            self.x, self.y = coords

    def grayscale(self):
        self.__image = pg.transform.grayscale(self.__image)
        if hasattr(self, "origin_image"):
            self.origin_image = pg.transform.grayscale(self.origin_image)

    def centre(self):
        self.x = (self.surface.get_width() - self.width) // 2
        self.y = (self.surface.get_height() - self.height) // 2

    @abc.abstractmethod
    def draw(self, *args):
        ...

    @property
    def x(self):
        return self.__rect.x

    @x.setter
    def x(self, value: int):
        self.__rect.x = value

    @property
    def y(self):
        return self.__rect.y

    @y.setter
    def y(self, value: int):
        self.__rect.y = value

    @property
    def rect(self):
        margin_x = self.margin_x if hasattr(self, "margin_x") else 0
        margin_y = self.margin_y if hasattr(self, "margin_y") else 0
        return self.x + margin_x, self.y + margin_y, self.width, self.height

    @property
    def width(self):
        return self.__rect.width

    @property
    def height(self):
        return self.__rect.height


class ResizableObject(Object):

    def __init__(self, *args, resize: bool, **kwargs):
        super().__init__(*args, kwargs.get("save_origin", False))
        self.surface_size = (None, None)
        self.margin_x, self.margin_y = 0, 0
        self.__resize = resize

    def get_rotated_size(self, size: Tuple[int, int]):
        width, height = self.origin_image.get_size()
        origin_ratio = width / height
        ratio = size[0] / size[1]
        if origin_ratio >= ratio:
            return int(size[1] * (origin_ratio - ratio) + size[0]), size[1]
        return size[0], int(size[0] * (1 / origin_ratio - 1 / ratio) + size[1])

    def resize(self):
        new_size = self.surface.get_width(), self.surface.get_height()
        if self.surface_size != new_size:
            bg_width, bg_height = self.get_rotated_size(new_size)
            self.resize_image((bg_width, bg_height))
            self.margin_x = -(bg_width - new_size[0]) // 2
            self.margin_y = -(bg_height - new_size[1]) // 2
            self.surface_size = new_size

    @property
    def resizable(self):
        return self.__resize

    def draw(self, *args, **kwargs):
        if self.resizable:
            self.resize()
        self.surface.blit(self.image, (self.margin_x + self.x, self.margin_y + self.y))
