import random

from application import pg

import os
import threading
import wave

import numpy
import pyaudio
import scipy.fftpack as spfft
import soundfile

from pathlib import Path
from typing import Tuple, List, Any, Iterable, Dict

from application.animation import Transition, Frame
from application.base import ResizableObject
from application.ui import Heart, Grid, Button, Level, Square
from application.utils import LinkObject
from application.utils.builders import ParticleBuilder
from application.utils.enums import BezierFunctions, States


class Music:

    mixer = pyaudio.PyAudio()

    def __init__(self, filename: Path, chunk: int, amplitude: LinkObject):
        self.chunk = chunk
        self.song = wave.open(str(filename), 'rb')
        self.stream = self.mixer.open(
            format=self.mixer.get_format_from_width(self.song.getsampwidth()),
            channels=self.song.getnchannels(),
            rate=self.song.getframerate(),
            output=True
        )
        data, _ = soundfile.read(str(filename))
        self.data = data if data.ndim == 1 else data[:, 0]
        self.hamming = numpy.hamming(self.chunk)
        self.amplitude = amplitude

    def play(self):
        start = 0
        while len(data := self.song.readframes(self.chunk)) > 0:
            if len(fragment := self.data[start:start + self.chunk]) == self.chunk:
                values = self.hamming * fragment
                self.amplitude.value = sum(
                    [numpy.sqrt(row.real ** 2 + row.imag ** 2) for row in spfft.fft(values)]
                ) * 0.25
            self.stream.write(data)
            start += self.chunk
        self.stream.stop_stream()
        self.stream.close()


class App:
    instance = None
    root_path = Path('.').parent

    src_path = root_path / "src"
    saves_path = root_path / "saves"

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            return super().__new__(cls)
        return cls.instance

    def __init__levels__(self):
        font = LinkObject(pg.font.SysFont("monospace", 24))
        for filename in os.listdir(self.saves_path):
            # Set levels
            self.games.append(
                frame := Frame(
                    self.screen,
                    self.saves_path / filename,
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
                    resize=False, first_color=color, width=150, data=self.saves_path / filename,
                    font=font, function=self.change_state, border_width=0
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
            builder=ParticleBuilder(Square), particles=5000,
            path=self.src_path / "square.png"
        )
        level_frame.activate()
        level_frame.centre()
        level_frame.grayscale()
        self.level.zoom(1)

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
            border_width=0
        )
        palitre_frame.set_pos((25, 25))

        self.palitre = Level(
            palitre_frame, path=self.src_path / "rubber.png", particles=len(self.level.colors()),
            builder=ParticleBuilder(Square, remain_height=True, limit=True), pad=1.5
        )
        palitre_frame.activate()

        if palitre_frame.buttons:
            self.__init__palitre__buttons__(palitre_frame.buttons, palitre_data)
            palitre_frame.buttons[0].click()
        return palitre_data

    def __post__init__(self):
        self.__run__level__()
        color_matcher = self.__create__palitre__()

        for button in self.level.builder.particles:
            button.text = color_matcher[button.data]

    def __init__(self, screen_size: Tuple[int, int]):
        # Set screen parameters
        self.screen = pg.display.set_mode(screen_size, pg.RESIZABLE, pg.SRCALPHA)

        # Set FPS
        self.FPS = 60
        self.mouse_pos: float = None
        self.__run: bool = True

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

        # Set gameplay objects
        self.__current_state: int = None
        self.__state = LinkObject(None)
        self.games = Grid(self.screen)

        self.__level_path = LinkObject(None)
        self.level: Level = None
        self.palitre: Level = None
        self.__selected_color = (0, 0, 0, 0)

        # Init levels
        pg.font.init()
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

        pg.init()

    def change_state(self, **kwargs):
        self.__state.value = States(1)
        self.__level_path.value = kwargs.get("data")
        pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

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

    def start_music(self):
        music = Music(self.src_path / "song.wav", 1024, self.amplitude)
        thread = threading.Thread(
            target=music.play,
            args=(), daemon=True
        )
        thread.start()
        return thread

    def check_menu_events(self, events) -> bool:
        for ev in events:
            if ev.type == pg.QUIT:
                self.__run = False
            if ev.type == pg.MOUSEWHEEL:
                self.games.scroll(ev.y * 25)
            if ev.type == pg.MOUSEMOTION:
                self.games.check_collision(ev.pos)
            if pg.mouse.get_pressed()[0]:
                self.games.check_clicked(
                    ev.pos
                )

    def check_level_events(self, events) -> bool:
        for ev in events:
            if ev.type == pg.QUIT:
                self.__run = False
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
                self.level.check_clicked(ev.pos, self.__selected_color)

    def draw_intractable(self, events, delta: float):
        match self.state:
            case States.menu:
                self.check_menu_events(events)

                self.games.draw(delta)
                # Draw heart
                self.heart.draw(delta, self.amplitude.value if self.amplitude.value else 200)
            case States.level:
                if self.level is not None:
                    self.check_level_events(events)

                if self.level is None:
                    self.__post__init__()

                self.level.draw()
                self.palitre.draw(delta)

    def loop(self):
        music_thread = self.start_music()
        clock = pg.time.Clock()
        while self.__run:
            # Tick the clock
            dt = clock.tick(self.FPS) / 1000

            # Draw background
            self.background.draw()

            # Draw intractable
            self.draw_intractable(pg.event.get(), dt)

            # Draw transition
            self.check_state()
            self.transition.draw(dt)

            # Check music
            if not music_thread.is_alive():
                music_thread = self.start_music()

            # Update
            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    app = App(screen_size=(800, 600))
    app.loop()
