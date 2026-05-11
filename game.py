"""A serious game about one difficult day living in poverty.

Move around the small neighborhood, enter each location, and make choices.
The patience bar is the key mechanic from the design doc: calm/safe choices
cost patience, while angry or risky choices may feel easier but cause fallout.
"""

from __future__ import annotations

from dataclasses import dataclass
import textwrap

import arcade

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
SCREEN_TITLE = "One Long Day"

PLAYER_SPEED = 4

COLOR_BG = (42, 45, 48)
COLOR_ROAD = (64, 66, 68)
COLOR_SIDEWALK = (101, 103, 100)
COLOR_PANEL = (24, 26, 29, 238)
COLOR_PANEL_BORDER = (210, 214, 203)
COLOR_TEXT = (245, 242, 231)
COLOR_MUTED = (184, 183, 174)
COLOR_PLAYER = (82, 178, 154)
COLOR_LOCKED = (96, 96, 96)
COLOR_GOOD = (91, 169, 121)
COLOR_WARN = (218, 171, 78)
COLOR_BAD = (198, 83, 78)


@dataclass
class Building:
    """A place the player can visit."""

    key: str
    name: str
    prompt: str
    left: int
    right: int
    bottom: int
    top: int
    color: tuple[int, int, int]

    @property
    def center(self) -> tuple[float, float]:
        return ((self.left + self.right) / 2, (self.bottom + self.top) / 2)


@dataclass
class Choice:
    """One selectable response in a scene."""

    label: str
    result: str
    patience: int
    stability: int
    grades: int
    family: int
    kind: str


@dataclass
class Scene:
    """A story moment tied to a location."""

    key: str
    title: str
    location: str
    situation: str
    choices: list[Choice]


BUILDINGS = [
    Building("home", "Apartment", "Start / Finish", 55, 220, 410, 575, (118, 122, 132)),
    Building("school", "School", "Homework talk", 570, 835, 420, 580, (137, 98, 84)),
    Building("work", "Corner Store", "After-school shift", 80, 310, 80, 250, (104, 128, 93)),
    Building("gas", "Gas Station", "Friends outside", 600, 820, 70, 250, (128, 118, 74)),
]


SCENES = [
    Scene(
        "morning",
        "Morning: Already Behind",
        "home",
        (
            "You wake up late because your mom's second job ran past midnight, "
            "and you had to watch your little brother. Your homework is half done. "
            "The bus leaves soon."
        ),
        [
            Choice(
                "Finish a little homework and risk being late.",
                "You turn in something incomplete. The teacher still notices, but you keep some control over the day.",
                -12,
                -2,
                7,
                0,
                "patient",
            ),
            Choice(
                "Leave now and hope the teacher understands.",
                "You make it on time, but the missing work follows you into class.",
                -6,
                0,
                -5,
                0,
                "mixed",
            ),
            Choice(
                "Skip first period because it already feels impossible.",
                "For one hour you breathe, but school marks you absent and the day starts heavier.",
                10,
                -12,
                -12,
                -2,
                "rash",
            ),
        ],
    ),
    Scene(
        "teacher",
        "School: The Homework",
        "school",
        (
            "Your teacher stops you in front of everyone about the missing assignment. "
            "You can feel people staring. A calm answer might help, but staying calm takes energy."
        ),
        [
            Choice(
                "Apologize and ask for one more night.",
                "The teacher gives you a short extension, but you spend patience you were trying to save.",
                -18,
                4,
                12,
                0,
                "patient",
            ),
            Choice(
                "Stay quiet and take the zero.",
                "Nobody argues, but your grade drops and the silence feels like swallowing a rock.",
                -7,
                -3,
                -13,
                0,
                "mixed",
            ),
            Choice(
                "Snap back at the teacher.",
                "You are sent out of class. It feels good for ten seconds, then the principal calls home.",
                12,
                -18,
                -15,
                -10,
                "rash",
            ),
        ],
    ),
    Scene(
        "work",
        "Work: Extra Shift",
        "work",
        (
            "After school, your manager asks you to stay late because someone called out. "
            "The extra money matters, but you still have homework and your body is tired."
        ),
        [
            Choice(
                "Stay late and keep the paycheck steady.",
                "You earn more money, but the evening gets squeezed tight.",
                -14,
                14,
                -5,
                0,
                "patient",
            ),
            Choice(
                "Ask for only one extra hour.",
                "Your manager is annoyed, but you protect a little time for school.",
                -8,
                4,
                5,
                0,
                "mixed",
            ),
            Choice(
                "Leave without explaining.",
                "You get your night back, but your manager cuts next week's hours.",
                10,
                -18,
                3,
                0,
                "rash",
            ),
        ],
    ),
    Scene(
        "gas",
        "Gas Station: A Place To Belong",
        "gas",
        (
            "Some older kids wave you over outside the gas station. They make you laugh, "
            "and they do not treat you like a problem. Your mom hates when you hang around them."
        ),
        [
            Choice(
                "Go home even though it feels lonely.",
                "Your mom is relieved, but you spend another night feeling cut off from people who accept you.",
                -16,
                2,
                4,
                10,
                "patient",
            ),
            Choice(
                "Talk for ten minutes, then leave.",
                "You get a little relief and still make it home before things explode.",
                -8,
                0,
                0,
                2,
                "mixed",
            ),
            Choice(
                "Hang out all night.",
                "You finally feel wanted. At home, your mom is terrified and furious.",
                12,
                -12,
                -8,
                -18,
                "rash",
            ),
        ],
    ),
    Scene(
        "night",
        "Night: What Is Left",
        "home",
        (
            "Back home, your brother needs help, your mom wants to know why school called, "
            "and tomorrow is already waiting. You decide what to do with the little energy left."
        ),
        [
            Choice(
                "Help your brother, then do homework until you fall asleep.",
                "You do not fix everything, but you keep the people around you from falling further.",
                -18,
                4,
                10,
                8,
                "patient",
            ),
            Choice(
                "Do the homework and avoid the conversation.",
                "Your grade recovers a bit, but the house stays tense.",
                -9,
                0,
                9,
                -4,
                "mixed",
            ),
            Choice(
                "Argue, shut the door, and sleep.",
                "You finally stop dealing with people. The problems are still there in the morning.",
                10,
                -8,
                -6,
                -12,
                "rash",
            ),
        ],
    ),
]


class GameView(arcade.View):
    """Top-down choice game based on the MVP design document."""

    def __init__(self) -> None:
        super().__init__()
        self.background_color = COLOR_BG
        self.player_x = 145
        self.player_y = 493
        self.keys_pressed: set[int] = set()
        self.scene_index = 0
        self.current_scene: Scene | None = SCENES[0]
        self.awaiting_continue = False
        self.last_result = ""
        self.game_over = False
        self.ending_text = ""
        self.patience = 55
        self.stability = 50
        self.grades = 50
        self.family = 50
        self.choice_buttons: list[tuple[int, int, int, int, int]] = []
        self.restart_button = (350, 550, 44, 92)

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def on_key_press(self, key: int, modifiers: int) -> None:
        if key == arcade.key.R and self.game_over:
            self.setup()
            return
        if key in {arcade.key.UP, arcade.key.DOWN, arcade.key.LEFT, arcade.key.RIGHT, arcade.key.W, arcade.key.A, arcade.key.S, arcade.key.D}:
            self.keys_pressed.add(key)
        if key == arcade.key.E and not self.current_scene and not self.game_over:
            self.try_start_nearby_scene()
        if key == arcade.key.SPACE and self.awaiting_continue:
            self.advance_scene()

    def on_key_release(self, key: int, modifiers: int) -> None:
        self.keys_pressed.discard(key)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.game_over:
            left, right, bottom, top = self.restart_button
            if left <= x <= right and bottom <= y <= top:
                self.setup()
            return

        if self.awaiting_continue:
            self.advance_scene()
            return

        if not self.current_scene:
            return

        for index, left, right, bottom, top in self.choice_buttons:
            if left <= x <= right and bottom <= y <= top:
                self.choose(index)
                return

    def on_update(self, delta_time: float) -> None:
        if self.current_scene or self.game_over:
            return

        dx = 0
        dy = 0
        if arcade.key.LEFT in self.keys_pressed or arcade.key.A in self.keys_pressed:
            dx -= PLAYER_SPEED
        if arcade.key.RIGHT in self.keys_pressed or arcade.key.D in self.keys_pressed:
            dx += PLAYER_SPEED
        if arcade.key.DOWN in self.keys_pressed or arcade.key.S in self.keys_pressed:
            dy -= PLAYER_SPEED
        if arcade.key.UP in self.keys_pressed or arcade.key.W in self.keys_pressed:
            dy += PLAYER_SPEED

        self.player_x = max(25, min(SCREEN_WIDTH - 25, self.player_x + dx))
        self.player_y = max(25, min(SCREEN_HEIGHT - 25, self.player_y + dy))

    def setup(self) -> None:
        self.player_x = 145
        self.player_y = 493
        self.keys_pressed.clear()
        self.scene_index = 0
        self.current_scene = SCENES[0]
        self.awaiting_continue = False
        self.last_result = ""
        self.game_over = False
        self.ending_text = ""
        self.patience = 55
        self.stability = 50
        self.grades = 50
        self.family = 50

    def on_draw(self) -> None:
        self.clear()
        self.draw_world()
        self.draw_hud()
        if self.game_over:
            self.draw_ending()
        elif self.current_scene:
            self.draw_scene()
        elif self.awaiting_continue:
            self.draw_result()
        else:
            self.draw_location_hint()

    def draw_world(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, COLOR_BG)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 285, 365, COLOR_ROAD)
        arcade.draw_lrbt_rectangle_filled(410, 490, 0, SCREEN_HEIGHT, COLOR_ROAD)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 272, 285, COLOR_SIDEWALK)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 365, 378, COLOR_SIDEWALK)
        arcade.draw_lrbt_rectangle_filled(397, 410, 0, SCREEN_HEIGHT, COLOR_SIDEWALK)
        arcade.draw_lrbt_rectangle_filled(490, 503, 0, SCREEN_HEIGHT, COLOR_SIDEWALK)

        for building in BUILDINGS:
            arcade.draw_lrbt_rectangle_filled(building.left, building.right, building.bottom, building.top, building.color)
            arcade.draw_lrbt_rectangle_filled(building.left, building.right, building.top - 16, building.top, (38, 39, 41))
            arcade.draw_text(building.name, building.left + 10, building.top - 12, COLOR_TEXT, 12)
            arcade.draw_text(building.prompt, building.left + 10, building.bottom + 12, (232, 225, 176), 10)

        arcade.draw_circle_filled(self.player_x, self.player_y, 15, COLOR_PLAYER)
        arcade.draw_circle_filled(self.player_x + 5, self.player_y + 6, 3, (20, 50, 45))

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 600, 650, (18, 19, 21, 245))
        arcade.draw_text("One Long Day", 18, 620, COLOR_TEXT, 18, bold=True)
        self.draw_meter("Patience", self.patience, 180, COLOR_WARN)
        self.draw_meter("Stability", self.stability, 365, COLOR_GOOD)
        self.draw_meter("Grades", self.grades, 550, (104, 156, 212))
        self.draw_meter("Family", self.family, 735, (207, 134, 181))

    def draw_meter(self, label: str, value: int, x: int, color: tuple[int, int, int]) -> None:
        value = max(0, min(100, value))
        arcade.draw_text(label, x, 628, COLOR_MUTED, 10)
        arcade.draw_lrbt_rectangle_filled(x, x + 130, 611, 623, (68, 69, 72))
        arcade.draw_lrbt_rectangle_filled(x, x + 1.3 * value, 611, 623, color)
        arcade.draw_text(str(value), x + 138, 609, COLOR_TEXT, 11)

    def draw_scene(self) -> None:
        assert self.current_scene is not None
        self.draw_panel(78, 822, 92, 558)
        arcade.draw_text(self.current_scene.title, 108, 515, COLOR_TEXT, 24, bold=True)
        arcade.draw_text(
            self.current_scene.situation,
            108,
            468,
            COLOR_TEXT,
            15,
            width=684,
            multiline=True,
        )
        arcade.draw_text(
            "Calm choices spend patience. If patience runs out, only the harshest option stays available.",
            108,
            392,
            COLOR_MUTED,
            12,
        )

        self.choice_buttons.clear()
        for index, choice in enumerate(self.current_scene.choices):
            left = 108
            right = 792
            top = 350 - index * 82
            bottom = top - 58
            locked = self.choice_locked(index)
            fill = COLOR_LOCKED if locked else self.choice_color(choice)
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, fill)
            arcade.draw_lrbt_rectangle_filled(left, right, top - 4, top, (255, 255, 255, 35))
            label = choice.label if not locked else "Patience is empty: this choice is unavailable."
            arcade.draw_text(label, left + 16, bottom + 33, COLOR_TEXT, 13, width=640, multiline=True)
            arcade.draw_text(self.effect_text(choice), left + 16, bottom + 12, (236, 234, 220), 10)
            self.choice_buttons.append((index, left, right, bottom, top))

    def draw_result(self) -> None:
        self.draw_panel(96, 804, 178, 492)
        arcade.draw_text("Consequence", 126, 445, COLOR_TEXT, 24, bold=True)
        arcade.draw_text(self.last_result, 126, 386, COLOR_TEXT, 15, width=648, multiline=True)
        arcade.draw_text("Click or press SPACE to continue.", 126, 224, COLOR_MUTED, 13)

    def draw_ending(self) -> None:
        self.draw_panel(92, 808, 116, 542)
        arcade.draw_text("End of the Day", 122, 494, COLOR_TEXT, 26, bold=True)
        arcade.draw_text(self.ending_text, 122, 436, COLOR_TEXT, 15, width=656, multiline=True)
        arcade.draw_text("What the game is showing: poverty can turn normal teen choices into trade-offs with no perfect answer.", 122, 210, COLOR_MUTED, 13, width=656, multiline=True)
        left, right, bottom, top = self.restart_button
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (82, 128, 120))
        arcade.draw_text("Restart", (left + right) / 2, bottom + 18, COLOR_TEXT, 16, anchor_x="center", bold=True)

    def draw_location_hint(self) -> None:
        scene = SCENES[self.scene_index]
        building = self.get_building(scene.location)
        near = self.near_building(building)
        text = f"Next: go to {building.name} for {scene.title}. "
        text += "Press E." if near else "Use WASD or arrow keys to move."
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, 42, (18, 19, 21, 230))
        arcade.draw_text(text, SCREEN_WIDTH / 2, 14, COLOR_TEXT, 13, anchor_x="center")

    def draw_panel(self, left: int, right: int, bottom: int, top: int) -> None:
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, COLOR_PANEL)
        arcade.draw_lrbt_rectangle_filled(left, right, top - 3, top, COLOR_PANEL_BORDER)
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, bottom + 3, (80, 82, 78))

    def choose(self, index: int) -> None:
        if not self.current_scene or self.choice_locked(index):
            return
        choice = self.current_scene.choices[index]
        self.patience = max(0, min(100, self.patience + choice.patience))
        self.stability = max(0, min(100, self.stability + choice.stability))
        self.grades = max(0, min(100, self.grades + choice.grades))
        self.family = max(0, min(100, self.family + choice.family))
        self.last_result = choice.result
        self.current_scene = None
        self.awaiting_continue = True

    def choice_locked(self, index: int) -> bool:
        if self.patience > 0:
            return False
        return index != 2

    def choice_color(self, choice: Choice) -> tuple[int, int, int]:
        if choice.kind == "patient":
            return (66, 103, 96)
        if choice.kind == "mixed":
            return (107, 103, 75)
        return (125, 67, 62)

    def effect_text(self, choice: Choice) -> str:
        signs = []
        for label, value in [
            ("patience", choice.patience),
            ("stability", choice.stability),
            ("grades", choice.grades),
            ("family", choice.family),
        ]:
            if value:
                signs.append(f"{label} {value:+}")
        return " | ".join(signs)

    def advance_scene(self) -> None:
        self.awaiting_continue = False
        self.scene_index += 1
        if self.scene_index >= len(SCENES):
            self.finish_game()
        else:
            self.current_scene = None

    def try_start_nearby_scene(self) -> None:
        scene = SCENES[self.scene_index]
        if self.near_building(self.get_building(scene.location)):
            self.current_scene = scene

    def get_building(self, key: str) -> Building:
        for building in BUILDINGS:
            if building.key == key:
                return building
        raise ValueError(f"Missing building: {key}")

    def near_building(self, building: Building) -> bool:
        cx, cy = building.center
        return abs(self.player_x - cx) < 140 and abs(self.player_y - cy) < 115

    def finish_game(self) -> None:
        self.game_over = True
        self.awaiting_continue = False
        average = (self.stability + self.grades + self.family + self.patience) / 4
        weakest = min(
            [("patience", self.patience), ("stability", self.stability), ("grades", self.grades), ("family trust", self.family)],
            key=lambda item: item[1],
        )
        if average >= 58 and self.grades >= 45 and self.family >= 45:
            headline = "You made it through, but it cost you."
        elif self.stability <= 25:
            headline = "The day spiraled into survival mode."
        elif self.family <= 25:
            headline = "Home feels less safe than it did this morning."
        elif self.grades <= 25:
            headline = "School became one more place you fell behind."
        else:
            headline = "Nothing fully broke, but nothing felt easy."

        wrapped_stats = textwrap.dedent(
            f"""
            {headline}

            Final scores:
            Patience {self.patience} | Stability {self.stability} | Grades {self.grades} | Family {self.family}

            Your lowest area was {weakest[0]}. That does not mean you made one bad choice. It means the same choice can cost more when money, time, rest, and support are all limited.
            """
        ).strip()
        self.ending_text = wrapped_stats


def main() -> None:
    """Start the game window."""
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    view = GameView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
