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


@dataclass
class Character:
    """A selectable player look."""

    name: str
    shirt: tuple[int, int, int]
    pants: tuple[int, int, int]
    backpack: tuple[int, int, int]
    description: str


CHARACTERS = [
    Character("Miles", (82, 178, 154), (37, 67, 86), (222, 170, 82), "Balanced and observant"),
    Character("Knox", (201, 91, 83), (54, 63, 92), (84, 146, 171), "Bold and direct"),
    Character("Drew", (118, 112, 184), (68, 82, 69), (207, 143, 93), "Quiet and careful"),
]


BUILDINGS = [
    Building("home", "Apartment", "Start / Finish", 55, 220, 410, 575, (118, 122, 132)),
    Building("school", "School", "Homework talk", 570, 835, 420, 580, (137, 98, 84)),
    Building("bus", "Bus Stop", "Get across town", 342, 500, 430, 555, (88, 111, 130)),
    Building("pantry", "Food Pantry", "Pick up groceries", 330, 510, 70, 225, (126, 91, 118)),
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
        "bus",
        "Bus Stop: Missing The Transfer",
        "bus",
        (
            "After school, the bus is late and your next transfer leaves in four minutes. "
            "If you miss it, you will be late to work. If you walk, you save the fare but lose time and energy."
        ),
        [
            Choice(
                "Ask the driver to radio the transfer bus.",
                "The driver helps, but asking politely while everyone watches takes more patience than you expected.",
                -13,
                5,
                0,
                0,
                "patient",
            ),
            Choice(
                "Walk fast and hope your manager understands.",
                "You save the fare and keep moving, but you arrive tired and a little late.",
                -7,
                -4,
                0,
                0,
                "mixed",
            ),
            Choice(
                "Kick the bench and yell about the bus.",
                "People look away. The anger gets out, but work starts with another problem attached to your name.",
                11,
                -14,
                0,
                -2,
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
        "pantry",
        "Food Pantry: The Line",
        "pantry",
        (
            "Your mom texts that the fridge is almost empty, so you stop at the food pantry. "
            "The line is long, the volunteers are rushed, and homework time is disappearing."
        ),
        [
            Choice(
                "Wait calmly and thank the volunteer.",
                "You bring food home and keep the peace, but the wait drains what was left of your evening.",
                -15,
                10,
                -6,
                8,
                "patient",
            ),
            Choice(
                "Take the smallest bag so you can leave faster.",
                "You save time for schoolwork, but dinner is thin and your mom has to stretch it.",
                -8,
                -4,
                5,
                -3,
                "mixed",
            ),
            Choice(
                "Argue when they run out of the food your family needed.",
                "The volunteer asks you to step outside. You leave with less food and more frustration.",
                12,
                -16,
                -4,
                -10,
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
        self.character_select = True
        self.selected_character = 0
        self.choice_buttons: list[tuple[int, int, int, int, int]] = []
        self.character_buttons: list[tuple[int, int, int, int, int]] = []
        self.restart_button = (350, 550, 44, 92)

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def on_key_press(self, key: int, modifiers: int) -> None:
        if self.character_select:
            if key in {arcade.key.KEY_1, arcade.key.NUM_1}:
                self.select_character(0)
            elif key in {arcade.key.KEY_2, arcade.key.NUM_2}:
                self.select_character(1)
            elif key in {arcade.key.KEY_3, arcade.key.NUM_3}:
                self.select_character(2)
            return

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
        if self.character_select:
            for index, left, right, bottom, top in self.character_buttons:
                if left <= x <= right and bottom <= y <= top:
                    self.select_character(index)
                    return
            return

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
        if self.character_select or self.current_scene or self.game_over:
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
        self.character_select = True

    def on_draw(self) -> None:
        self.clear()
        self.draw_world()
        self.draw_hud()
        if self.character_select:
            self.draw_character_select()
        elif self.game_over:
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

        self.draw_player_sprite(self.player_x, self.player_y, CHARACTERS[self.selected_character], 1.0)

    def draw_player_sprite(self, x: float, y: float, character: Character, scale: float) -> None:
        backpack_w = 8 * scale
        body_w = 18 * scale
        body_h = 24 * scale
        head_r = 8 * scale
        arcade.draw_lrbt_rectangle_filled(x - body_w / 2 - backpack_w, x - body_w / 2, y - 12 * scale, y + 11 * scale, character.backpack)
        arcade.draw_lrbt_rectangle_filled(x - body_w / 2, x + body_w / 2, y - 14 * scale, y + 10 * scale, character.shirt)
        arcade.draw_lrbt_rectangle_filled(x - body_w / 2, x - 1 * scale, y - 24 * scale, y - 12 * scale, character.pants)
        arcade.draw_lrbt_rectangle_filled(x + 1 * scale, x + body_w / 2, y - 24 * scale, y - 12 * scale, character.pants)
        arcade.draw_circle_filled(x, y + 21 * scale, head_r, (194, 139, 96))
        arcade.draw_circle_filled(x + 3 * scale, y + 23 * scale, 1.7 * scale, (30, 28, 24))

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

    def draw_character_select(self) -> None:
        self.draw_panel(74, 826, 92, 558)
        arcade.draw_text("Choose Your Character", SCREEN_WIDTH / 2, 510, COLOR_TEXT, 28, anchor_x="center", bold=True)
        arcade.draw_text(
            "Pick one sprite to play through the day. The story is the same, but the character you choose appears on the map.",
            SCREEN_WIDTH / 2,
            468,
            COLOR_MUTED,
            13,
            width=650,
            align="center",
            anchor_x="center",
            multiline=True,
        )

        self.character_buttons.clear()
        card_width = 200
        card_height = 240
        gap = 28
        start_x = (SCREEN_WIDTH - (card_width * 3 + gap * 2)) / 2
        for index, character in enumerate(CHARACTERS):
            left = int(start_x + index * (card_width + gap))
            right = left + card_width
            bottom = 170
            top = bottom + card_height
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (50, 52, 56))
            arcade.draw_lrbt_rectangle_filled(left, right, top - 5, top, character.shirt)
            self.draw_player_sprite((left + right) / 2, bottom + 128, character, 2.0)
            arcade.draw_text(character.name, (left + right) / 2, bottom + 58, COLOR_TEXT, 20, anchor_x="center", bold=True)
            arcade.draw_text(character.description, (left + right) / 2, bottom + 35, COLOR_MUTED, 11, anchor_x="center")
            arcade.draw_text(f"Press {index + 1}", (left + right) / 2, bottom + 13, (232, 225, 176), 12, anchor_x="center")
            self.character_buttons.append((index, left, right, bottom, top))

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
