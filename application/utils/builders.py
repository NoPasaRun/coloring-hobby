import math
from typing import Type, List, Tuple, Set

import pygame as pg


class Color:
    def __init__(self, value: Tuple[int, int, int, int], depth: int = 2):
        self.__value = tuple(round(val / 255 * (depth - 1)) for val in value)
        self.depth = depth

    def __repr__(self):
        return "Color(({}, {}, {}, {}))".format(*self.__value)

    def __str__(self):
        return self.__color_repr__(4)

    def __color_repr__(self, n: int):
        n = n if n <= 4 else 4
        pattern = "".join([f"{{{i}}}" for i in range(n)])
        return str(int("".join(pattern.format(*self.__value)), self.depth))

    @property
    def value(self) -> Tuple:
        return tuple(
            math.ceil(val * 255 / (self.depth - 1)) for val in self.__value
        )

    def __hash__(self):
        return int(str(self))

    def __eq__(self, other: 'Color'):
        if isinstance(other, Color):
            return hash(self) == hash(other)


class ParticleBuilder:

    def __init__(self, creation_class: Type[object],
                 remain_height: bool = False, remain_width: bool = False, crop: bool = False):
        self.__class = creation_class
        self.__particles = []
        self.__row, self.__column, self.__size = 0, 0, 0
        self.remain_height, self.remain_width, self.crop = remain_height, remain_width, crop

    @property
    def row(self) -> int:
        return self.__row

    @property
    def column(self) -> int:
        return self.__column

    @property
    def size(self) -> int:
        return self.__size

    @property
    def particles(self) -> List[object]:
        return self.__particles

    @property
    def first(self) -> object:
        if self.built:
            return self.__particles[0]
        raise Exception("Not initialized")

    @property
    def built(self):
        return bool(self.__particles)

    @staticmethod
    def change_color(object: object):
        def wrapper(data,  *args, **kwargs):
            object.fill_color = data
            object.image.fill(data)
        return wrapper

    def create_particle(self, frame: object, coords: Tuple[int, int], color_depth: int, *args, **kwargs) -> Color:
        pos = (coords[0] * self.__size, coords[1] * self.__size)
        color = pg.transform.average_color(
            frame.image, (*pos, self.__size, self.__size)
        )

        color_data = Color((color[0], color[1], color[2], 255), color_depth)

        square = self.__class(
            frame.surface, *args, resize=False, width=self.__size, data=color_data.value,
            text="", first_color=[0, 0, 0], border_width=0, save_origin=True, **kwargs
        )
        square.function = self.change_color(square)
        square.margin_x, square.margin_y = pos

        self.__particles.append(square)
        return color_data

    def build(self, frame: object, particles: int, color_depth: int, *args, pad: int = 1, **kwargs) -> Set:
        if self.__particles:
            raise Exception("Already initialized")
        self.__size = int(math.sqrt((frame.width * frame.height) / particles))

        if self.remain_width:
            self.__row = math.ceil(frame.width / self.__size / pad)
            self.__column = particles // self.__row
        else:
            self.__column = math.ceil(frame.height / self.__size / pad)
            self.__row = particles // self.__column

        area = self.column * self.row

        colors = set()
        for y in range(self.__column):
            for x in range(self.__row):
                colors.add(
                    self.create_particle(frame, (x * pad, y * pad), color_depth, *args, **kwargs)
                )
        if self.remain_width and particles - area > 0 and not self.crop:
            for x in range(particles - area):
                colors.add(
                    self.create_particle(
                        frame, (x * pad, self.__column * pad), color_depth, *args, **kwargs
                    )
                )
            self.__column += 1
        elif self.remain_height and particles - area > 0 and not self.crop:
            for y in range(particles - area):
                colors.add(
                    self.create_particle(
                        frame, (self.__row * pad, y * pad), color_depth, *args, **kwargs
                    )
                )
            self.__row += 1
        colors.add(Color((0, 0, 0, 0), color_depth))
        return colors

    def rebuild(self, new_size: Tuple):
        for y in range(self.__column):
            for x in range(self.__row):
                if y * self.__row + x == len(self.particles) - 1:
                    break
                square = self.__particles[y * self.__row + x]
                square.resize_image(new_size)
                square.margin_x = square.width * x
                square.margin_y = square.height * y
            else:
                continue
            break
