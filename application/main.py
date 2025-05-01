import asyncio
import json

import pygame as pg

import os

from pathlib import Path
from typing import Tuple, List, Any, Iterable, Dict, Callable

from animation import Transition, Frame
from base import ResizableObject
from ui import Heart, Grid, Button, Level, Square
from utils import LinkObject
from utils.builders import ParticleBuilder
from utils.consts import (
    COLOR_DEPTH,
    DEFAULT_COLOR_DEPTH,
    AMOUNT_OF_PARTICLES,
    DEFAULT_AMOUNT_OF_PARTICLES,
    TURN_ON_MUSIC,
    BEAT_UPDATE_SECOND
)
from utils.enums import BezierFunctions, States


class App:
    instance = None
    root_path = Path('.').parent.absolute()

    src_path = root_path / "src"
    saves_path = root_path / "saves"

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(cls)
        return cls.instance

    def __init__levels__(self):
        font = LinkObject(pg.font.SysFont("monospace", 24))
        for dirname in os.listdir(self.saves_path):
            # Set levels
            full_path = self.saves_path / dirname
            if not ("image.png" in os.listdir(full_path)):
                continue
            self.games.append(
                frame := Frame(
                    self.screen,
                    full_path / "image.png",
                    resize=False,
                    width=200,
                    first_color=(color := [34, 34, 34]),
                    second_color=next(Frame.colors),
                )
            )
            # Set play buttons
            frame.set_button(
                button := Button(
                    self.screen, self.src_path / "play_button.png", text="Играть",
                    resize=False, first_color=color, width=150, data=full_path / "image.png",
                    font=font, function=self.change_state(States.level, self.__post__init__), border_width=0
                )
            )
            button.margin_x, button.margin_y = (
                (frame.width - button.width) // 2,
                (frame.height - button.height) // 2
            )

    def __run__level__(self):
        self.level = Level(
            level_frame := Frame(
                self.screen, self.__level_path.value,
                resize=False,
                width=300,
                first_color=[0, 0, 0],
                save_origin=True
            ),
            builder=ParticleBuilder(Square, remain_width=True, crop=True),
            particles=int(os.environ.get(AMOUNT_OF_PARTICLES, DEFAULT_AMOUNT_OF_PARTICLES)),
            path=self.src_path / "square.png"
        )
        self.level.draw = level_frame.draw

        level_frame.activate()
        level_frame.centre()
        level_frame.grayscale()
        self.level.zoom(0.001)

    def __init__palitre__buttons__(self, buttons: Iterable[Button], data: Dict):
        for index, (color, button) in enumerate(zip(self.level.colors(), buttons)):
            button.first_color = color.value if hash(color) > 0 else (150, 150, 150, 255)
            button.text = str(index + 1) if hash(color) > 0 else "R"
            button.border_width = 2
            button.data = color.value
            button.function = self.select_color(buttons)
            data[button.data] = button.text

    def __create__palitre__(self) -> Dict:
        palitre_data = dict()

        palitre_frame = Frame(
            self.screen, self.src_path / "line.png",
            resize=False,
            width=50,
            first_color=[0, 0, 0, 0],
            save_origin=False,
            border_width=0,
        )
        palitre_frame.set_pos((25, 25))

        self.palitre = Level(
            palitre_frame, path=self.src_path / "rubber.png", particles=len(self.level.colors()),
            builder=ParticleBuilder(Square, remain_height=True), pad=1.5
        )
        self.palitre.pad_procent = 0.06
        palitre_frame.activate()

        if palitre_frame.buttons:
            self.__init__palitre__buttons__(palitre_frame.buttons, palitre_data)
            palitre_frame.buttons[0].click()
        return palitre_data

    def __post__destroy__(self):
        self.palitre = None
        self.level = None
        self.__level_actions: list = []

    def __post__init__(self):
        self.__run__level__()
        color_matcher = self.__create__palitre__()

        for button in self.level.builder.particles:
            button.text = color_matcher[button.data]

    def __pre__destroy__(self):
        self.settings_editor_grid = Grid(self.editor_frame, pad_procent=0.2)
        self.color_depth_button = None
        self.amount_button = None

    def change_color_of_settings_button(self, **kwargs):
        data = [(True, [255, 0, 0, 255]), (False, [255, 255, 255, 255])]
        if kwargs.get("data") == "color":
            data.reverse()
        self.amount_button.__pressed__, self.amount_button.first_color = data[0]
        self.color_depth_button.__pressed__, self.color_depth_button.first_color = data[1]
        self.save_settings_button.text = "Сохранить"

    def __pre__init__(self):
        font = LinkObject(pg.font.SysFont("monospace", 16))
        self.settings_editor_grid.append(
            Button(
                self.screen, self.src_path / "play_button.png",
                resize=False,
                width=300,
                first_color=[255, 255, 255, 255],
                save_origin=False,
                border_width=0,
                text="Введите глубину цвета",
                data=None,
                font=font
            )
        )
        self.settings_editor_grid.append(
            color_depth_button := Button(
                self.screen, self.src_path / "play_button.png",
                text=str(os.environ.get(COLOR_DEPTH, DEFAULT_COLOR_DEPTH)),
                resize=False, first_color=[255, 255, 255], width=100, data="color",
                font=font, border_width=0
            )
        )
        self.settings_editor_grid.append(
            Button(
                self.screen, self.src_path / "play_button.png",
                resize=False,
                width=300,
                first_color=[255, 255, 255, 255],
                save_origin=False,
                border_width=0,
                text="Введите количество част.",
                data=None,
                font=font
            )
        )
        self.settings_editor_grid.append(
            amount_button := Button(
                self.screen, self.src_path / "play_button.png",
                text=str(os.environ.get(AMOUNT_OF_PARTICLES, DEFAULT_AMOUNT_OF_PARTICLES)),
                resize=False, first_color=[255, 255, 255], width=100, data="particles",
                font=font, border_width=0
            )
        )
        self.color_depth_button = color_depth_button
        self.amount_button = amount_button

        color_depth_button.function = self.change_color_of_settings_button
        amount_button.function = self.change_color_of_settings_button

    def apply_settings(self, **_):
        if self.amount_button.text.isdigit():
            os.environ.__setitem__(AMOUNT_OF_PARTICLES, self.amount_button.text)
        if self.color_depth_button.text.isdigit():
            os.environ.__setitem__(COLOR_DEPTH, self.color_depth_button.text)
        self.save_settings_button.text = "Сохранено"

    def __init__(self, screen_size: Tuple[int, int]):
        # Init levels
        pg.font.init()
        pg.init()

        # Set screen parameters
        self.screen = pg.display.set_mode(screen_size, pg.RESIZABLE, pg.SRCALPHA)

        # Set FPS
        self.FPS = 60
        self.mouse_pos: float = None
        self.run: bool = True
        pg.mixer.music.load(self.src_path / "song.mp3")

        # Set music beat data
        with open(self.src_path / "beats.json") as f:
            self.beats = json.load(f)

        # Set transition image
        self.transition = Transition(
            self.screen,
            self.src_path / "dead.jpg",
            animation_time=3,
            function=BezierFunctions.stop_in_center,
            resize=True, save_origin=True
        )

        # Set background image
        self.background = ResizableObject(
            self.screen, self.src_path / "start_back.png",
            resize=True, save_origin=True
        )

        # Set heart image
        self.heart = Heart(
            self.screen, self.src_path / "heart.png",
            resize=True, save_origin=True
        )

        # Set setting button
        font = LinkObject(pg.font.SysFont("monospace", 16))
        self.menu_header_grid = Grid(self.screen, pad_procent=0.001)
        self.level_header_grid = Grid(self.screen, pad_procent=0.002)
        self.settings_header_grid = Grid(self.screen, pad_procent=0.001)

        self.editor_frame = Frame(
            self.screen, self.src_path / "line.png",
            resize=False,
            width=700,
            first_color=[0, 0, 0, 0],
            save_origin=False,
            border_width=0,
        )
        self.color_depth_button: Button = None
        self.amount_button: Button = None
        self.settings_editor_grid = Grid(self.editor_frame, pad_procent=0.2)

        back_button = Button(
            self.screen, self.src_path / "play_button.png", text="Меню",
            resize=False, first_color=[255, 255, 255], width=100, data=None,
            font=font, function=self.change_state(
                States.menu, self.__post__destroy__, self.__pre__destroy__
            ), border_width=0
        )

        def toggle_ready_image(data):
            if not self.level:
                return
            fill_color = None if not data else (0, 0, 0, 0)
            for particle in self.level.builder.particles:
                particle.fill_color = fill_color or particle.data
                particle.image.fill(particle.fill_color)
            self.auto_button.data = not self.auto_button.data

        self.menu_header_grid.append(
            Button(
                self.screen, self.src_path / "play_button.png", text="Настройки",
                resize=False, first_color=[255, 255, 255], width=100, data=None,
                font=font, function=self.change_state(States.settings, self.__pre__init__), border_width=0
            )
        )
        action_frame = Frame(
            self.screen, self.src_path / "line.png",
            resize=False,
            width=250,
            first_color=[0, 0, 0, 0],
            save_origin=False,
            border_width=0,
        )
        action_frame.set_button(
            Button(
                self.screen, self.src_path / "play_button.png", text="Отменить",
                resize=False, first_color=[255, 255, 255], width=100, data=None,
                font=font, function=self.apply_prev_action, border_width=0
            ),
            auto_button := Button(
                self.screen, self.src_path / "play_button.png", text="Авто",
                resize=False, first_color=[255, 255, 255], width=100, data=False,
                font=font, function=toggle_ready_image, border_width=0,
            )
        )
        self.auto_button = auto_button
        self.auto_button.margin_x = 150
        self.level_header_grid.append(action_frame)
        self.level_header_grid.append(back_button)

        self.settings_header_grid.append(back_button)
        self.settings_header_grid.append(
            save_settings_button := Button(
                self.screen, self.src_path / "play_button.png", text="Сохранить",
                resize=False, first_color=[255, 255, 255], width=100, data=None,
                font=font, border_width=0, function=self.apply_settings
            )
        )
        self.save_settings_button = save_settings_button

        # Set gameplay objects
        self.__current_state: int = None
        self.__state = LinkObject(None)
        self.games = Grid(self.screen)

        self.__level_path = LinkObject(None)
        self.__level_actions: list = []
        self.__mouse_release: bool = True
        self.level: Level = None
        self.palitre: Level = None
        self.__selected_color = (0, 0, 0, 0)

        self.__init__levels__()

        # Set music configuration
        self.amplitude = LinkObject(None)

        # Set icon image
        icon = pg.image.load(self.src_path / "icon.png")
        pg.display.set_icon(icon)

        # Set caption
        pg.display.set_caption("Разукрашка от Богдашки")

        # Set menu state
        self.__state.value = States(0)

    def change_state(self, val: States, *funcs: Iterable[Callable]):
        def wrapper(**kwargs):
            self.__state.value = val
            self.__level_path.value = kwargs.get("data")
            pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)
            [func() for func in funcs]

        return wrapper

    def select_color(self, buttons: List[Button]):
        width, height = buttons[0].width, buttons[0].height

        def wrapper(data: Any):
            not_selected, selected = None, None
            for button in buttons:
                if button.data == self.__selected_color:
                    not_selected = button
                if button.data == data:
                    selected = button
                if not_selected and selected:
                    not_selected.resize_image((selected.width, selected.height))
                    break
            self.__selected_color = data
            selected.resize_image((width + 5, height + 5))
            selected.font = pg.font.SysFont("monospace", int((width + 5) / 1.6))

        return wrapper

    @property
    def state(self):
        return self.__state.value

    def check_state(self):
        if (val := self.__state.value) != self.__current_state:
            self.__current_state = val
            self.transition.activate()

    def check_menu_events(self, events) -> bool:
        for ev in events:
            if ev.type == pg.QUIT:
                self.run = False
            if ev.type == pg.MOUSEWHEEL:
                self.games.scroll(ev.y * 25)
            if ev.type == pg.MOUSEMOTION:
                if self.menu_header_grid.check_collision(ev.pos):
                    continue
                self.games.check_collision(ev.pos)
            if pg.mouse.get_pressed()[0]:
                if self.games.check_clicked(ev.pos):
                    continue
                self.menu_header_grid.check_clicked(ev.pos)

    def apply_prev_action(self, **_):
        if not self.__level_actions:
            return
        for button, color in self.__level_actions.pop().items():
            button.fill_color = color
            button.image.fill(color)

    def check_level_events(self, events) -> bool:
        for ev in events:
            if ev.type == pg.QUIT:
                self.run = False
            if ev.type == pg.MOUSEBUTTONUP and ev.button == 1:
                self.__mouse_release = True
            if ev.type == pg.MOUSEMOTION:
                self.level_header_grid.check_collision(ev.pos)
            if ev.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[2]:
                if self.mouse_pos is not None:
                    self.level.move_frame(self.mouse_pos, ev.pos)
            if ev.type == pg.MOUSEWHEEL:
                self.level.zoom(1.5 if ev.y > 0 else 0.6)
            if hasattr(ev, "pos"):
                self.mouse_pos = ev.pos
            if pg.mouse.get_pressed()[0]:
                if self.palitre.check_clicked(ev.pos):
                    continue
                if self.level_header_grid.check_clicked(ev.pos):
                    continue
                if self.__mouse_release:
                    self.__level_actions.append(dict())
                self.__mouse_release = False
                self.level.check_clicked(ev.pos, self.__level_actions, self.__selected_color)

    def check_settings_events(self, events) -> bool:
        for ev in events:
            if ev.type == pg.QUIT:
                self.run = False
            if ev.type == pg.MOUSEMOTION:
                if self.settings_header_grid.check_collision(ev.pos):
                    continue

                self.settings_editor_grid.check_collision(ev.pos)
            if hasattr(ev, "pos"):
                self.mouse_pos = ev.pos
            if pg.mouse.get_pressed()[0]:
                if self.settings_header_grid.check_clicked(ev.pos):
                    continue

                self.settings_editor_grid.check_clicked(ev.pos)
            if ev.type == pg.KEYDOWN:
                for button in [self.amount_button, self.color_depth_button]:
                    if hasattr(button, "__pressed__") and button.__pressed__:
                        if ev.key == pg.K_BACKSPACE:
                            button.text = button.text[:-1] if button.text[:-1] else "0"
                        elif (button == self.amount_button and len(self.amount_button.text) < 4) or \
                                (button == self.color_depth_button and len(self.color_depth_button.text) < 2):
                            button.text = button.text + ev.unicode if button.text != "0" else ev.unicode
                        continue

    def draw_intractable(self, events, delta: float):
        match self.state:
            case States.menu:
                self.check_menu_events(events)
                if self.state != States.menu:
                    return

                self.games.draw(delta)
                # Draw heart
                self.heart.draw(delta, self.amplitude.value if self.amplitude.value else 0)
                # Draw setting button
                self.menu_header_grid.draw(delta)
            case States.level:
                self.check_level_events(events)
                if self.state != States.level:
                    return

                self.level.draw(delta)
                self.level_header_grid.draw(delta)
                self.palitre.draw(delta)
            case States.settings:
                self.check_settings_events(events)
                if self.state != States.settings:
                    return

                self.settings_header_grid.draw(delta)
                self.settings_editor_grid.draw(delta)

    def update_amplitude(self):
        current_time = pg.mixer.music.get_pos() / 1000

        # Проверка битов
        for beat in self.beats:
            if abs(beat["time"] - current_time) < BEAT_UPDATE_SECOND:
                self.amplitude.value = beat["intensity"]
                break

    async def loop(self):
        clock = pg.time.Clock()
        if TURN_ON_MUSIC:
            pg.mixer.music.play()
        while self.run:
            # Tick the clock
            dt = clock.tick(self.FPS) / 1000

            # Draw background
            self.background.draw()

            # Draw intractable
            self.draw_intractable(pg.event.get(), dt)

            # Draw transition
            self.check_state()
            self.transition.draw(dt)

            # Update amplitude
            if TURN_ON_MUSIC:
                self.update_amplitude()

                # Replay music
                if not pg.mixer.music.get_busy():
                    pg.mixer.music.play()

            # Update
            pg.display.update()
            await asyncio.sleep(0)

        pg.quit()


if __name__ == '__main__':
    app = App(screen_size=(800, 600))
    asyncio.run(app.loop())
