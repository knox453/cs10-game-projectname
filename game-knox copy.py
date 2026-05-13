"""A serious game about one difficult day living in poverty.

Move around the small neighborhood, enter each location, and make choices.
The morality bar is the key mechanic from the design doc: calm/safe choices
cost morality, while angry or risky choices may feel easier but cause fallout.
"""

from __future__ import annotations

from dataclasses import dataclass
import textwrap

import arcade

SCREEN_WIDTH = 1120
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
COLOR_TARGET = (232, 213, 132)
COLOR_STICK = (25, 25, 25)
COLOR_BAG = (49, 49, 49)
COLOR_BAG_HIGHLIGHT = (205, 205, 205)


def draw_outline_lrbt(left: float, right: float, bottom: float, top: float, color: tuple[int, int, int], border_width: int = 1) -> None:
    """Draw a rectangle outline while tolerating Arcade naming differences."""

    try:
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, color, border_width)
    except AttributeError:
        try:
            arcade.draw_lrtb_rectangle_outline(left, right, top, bottom, color, border_width)
        except AttributeError:
            arcade.draw_rectangle_outline((left + right) / 2, (bottom + top) / 2, right - left, top - bottom, color, border_width)


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
class CharacterProfile:
    """A small personalization choice for the opening screen."""

    key: str
    name: str
    bio: str
    body_type: str
    patience_bonus: int
    stability_bonus: int
    grades_bonus: int
    family_bonus: int
    accent: tuple[int, int, int]


BUILDINGS = [
    Building("home", "Apartment", "Start / Finish", 55, 220, 410, 575, (118, 122, 132)),
    Building("school", "School", "Homework talk", 570, 835, 420, 580, (137, 98, 84)),
    Building("primary", "Primary School", "Pickup line", 860, 1060, 420, 580, (155, 111, 86)),
    Building("work", "Corner Store", "After-school shift", 80, 310, 80, 250, (104, 128, 93)),
    Building("gas", "Gas Station", "Friends outside", 600, 820, 70, 250, (128, 118, 74)),
    Building("bus", "Bus Stop", "Long wait", 396, 462, 270, 332, (95, 112, 132)),
    Building("pantry", "Food Pantry", "Aid pickup", 845, 1035, 70, 250, (90, 137, 109)),
    Building("park", "Park", "Quiet break", 255, 470, 430, 560, (82, 145, 97)),
]


CHARACTER_PROFILES = [
    CharacterProfile(
        "planner",
        "The Quiet Planner",
        "Keeps notes, thinks ahead, and tries to hold the day together before it falls apart.",
        "average",
        5,
        0,
        8,
        2,
        (88, 160, 148),
    ),
    CharacterProfile(
        "helper",
        "The Family Helper",
        "Helps at home and at work, but school often gets pushed to the edge of the day.",
        "fat",
        2,
        6,
        -2,
        8,
        (173, 136, 86),
    ),
    CharacterProfile(
        "connector",
        "The Social Connector",
        "Knows people everywhere, leans on friends for energy, and has a hard time staying out of trouble.",
        "skinny",
        4,
        3,
        -4,
        4,
        (143, 114, 179),
    ),
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
                "The teacher gives you a short extension, but you spend moral resolve you were trying to save.",
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
        "primary",
        "Primary School: The Pickup Line",
        "primary",
        (
            "Your little brother's primary school calls because he forgot his lunch. "
            "If you bring it now, you lose time for your own day. If you do not, he waits embarrassed."
        ),
        [
            Choice(
                "Bring the lunch and head back fast.",
                "You help your brother and keep the morning from turning into a bigger problem.",
                -10,
                2,
                0,
                12,
                "patient",
            ),
            Choice(
                "Ask the office to let him wait a few minutes.",
                "They agree, but you spend some energy trying to be polite when you are already stressed.",
                -8,
                6,
                0,
                6,
                "mixed",
            ),
            Choice(
                "Ignore the call and hope someone else handles it.",
                "The problem does not disappear. It just moves onto someone else in the family.",
                6,
                -6,
                0,
                -14,
                "rash",
            ),
        ],
    ),
    Scene(
        "bus",
        "Bus Stop: Waiting It Out",
        "bus",
        (
            "The bus is late, the weather is bad, and you can already feel the day slipping. "
            "You are stuck waiting with no good way to speed things up."
        ),
        [
            Choice(
                "Stay patient and keep your head down.",
                "You save your energy, but the wait eats away at the little moral resolve you had left.",
                -14,
                2,
                0,
                0,
                "patient",
            ),
            Choice(
                "Text home and try to stay calm.",
                "At least someone knows where you are, and the waiting feels a little less alone.",
                -10,
                4,
                0,
                4,
                "mixed",
            ),
            Choice(
                "Give up and walk away.",
                "You get out of the cold, but now you are late and the rest of the day starts behind.",
                10,
                -8,
                -6,
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
        "Food Pantry: Waiting in Line",
        "pantry",
        (
            "After your shift, you and your mom stop at the food pantry. "
            "The line is long, the room is quiet, and everyone is trying not to look embarrassed."
        ),
        [
            Choice(
                "Wait your turn and take what is offered.",
                "You get food for the house, but the long line drains what is left of your patience.",
                -16,
                2,
                6,
                12,
                "patient",
            ),
            Choice(
                "Ask politely whether there is anything extra today.",
                "The worker helps where they can, and you leave with a little more than you expected.",
                -10,
                4,
                4,
                10,
                "mixed",
            ),
            Choice(
                "Leave early because the wait feels humiliating.",
                "You get out of the room fast, but now the fridge at home stays empty longer.",
                8,
                -8,
                -6,
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
        self.started = False
        self.selected_profile: CharacterProfile | None = None
        self.player_x = 145
        self.player_y = 493
        self.player_accent = (82, 178, 154)
        self.keys_pressed: set[int] = set()
        self.scene_index = 0
        self.current_scene: Scene | None = None
        self.awaiting_continue = False
        self.last_result = ""
        self.game_over = False
        self.ending_text = ""
        self.patience = 100
        self.stability = 50
        self.grades = 50
        self.family = 50
        self.choice_buttons: list[tuple[int, int, int, int, int]] = []
        self.profile_buttons: list[tuple[int, int, int, int, int]] = []
        self.restart_button = (350, 550, 44, 92)

    def on_show_view(self) -> None:
        arcade.set_background_color(self.background_color)

    def on_key_press(self, key: int, modifiers: int) -> None:
        if not self.started:
            if key in {arcade.key.KEY_1, arcade.key.NUM_1}:
                self.begin_game(0)
            elif key in {arcade.key.KEY_2, arcade.key.NUM_2}:
                self.begin_game(1)
            elif key in {arcade.key.KEY_3, arcade.key.NUM_3}:
                self.begin_game(2)
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
        if not self.started:
            for index, left, right, bottom, top in self.profile_buttons:
                if left <= x <= right and bottom <= y <= top:
                    self.begin_game(index)
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
        if not self.started or self.current_scene or self.game_over:
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
        self.started = False
        self.selected_profile = None
        self.player_x = 145
        self.player_y = 493
        self.player_accent = (82, 178, 154)
        self.keys_pressed.clear()
        self.scene_index = 0
        self.current_scene = None
        self.awaiting_continue = False
        self.last_result = ""
        self.game_over = False
        self.ending_text = ""
        self.patience = 100
        self.stability = 50
        self.grades = 50
        self.family = 50
        self.profile_buttons.clear()

    def on_draw(self) -> None:
        self.clear()
        if not self.started:
            self.draw_intro()
            return
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

    def draw_intro(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, COLOR_BG)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 580, 650, (18, 19, 21, 245))
        arcade.draw_text("One Long Day", SCREEN_WIDTH / 2, 610, COLOR_TEXT, 28, anchor_x="center", bold=True)
        arcade.draw_text(
            "Pick who you are before the day starts.",
            SCREEN_WIDTH / 2,
            582,
            COLOR_MUTED,
            14,
            anchor_x="center",
        )
        arcade.draw_text(
            "Each version begins the same story with a slightly different starting outlook and support.",
            SCREEN_WIDTH / 2,
            556,
            COLOR_MUTED,
            11,
            anchor_x="center",
        )

        card_lefts = [44, 312, 580]
        self.profile_buttons.clear()
        for index, profile in enumerate(CHARACTER_PROFILES):
            left = card_lefts[index]
            right = left + 236
            top = 500
            bottom = 150
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, (28, 30, 34, 245))
            arcade.draw_lrbt_rectangle_filled(left, right, top - 3, top, profile.accent)
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, bottom + 3, (86, 82, 78))
            draw_outline_lrbt(left, right, bottom, top, (205, 209, 198), 2)
            self.draw_profile_icon(left + 54, top - 65, profile)
            arcade.draw_text(profile.name, left + 88, top - 38, COLOR_TEXT, 17, bold=True, width=120, multiline=True)
            arcade.draw_text(profile.bio, left + 18, top - 100, COLOR_TEXT, 12, width=200, multiline=True)
            arcade.draw_text(
                f"1. Morality {profile.patience_bonus:+}  2. Stability {profile.stability_bonus:+}",
                left + 18,
                top - 210,
                COLOR_MUTED,
                10,
                width=200,
                multiline=True,
            )
            arcade.draw_text(
                f"3. Grades {profile.grades_bonus:+}  4. Family {profile.family_bonus:+}",
                left + 18,
                top - 228,
                COLOR_MUTED,
                10,
                width=200,
                multiline=True,
            )
            arcade.draw_text(
                f"Press {index + 1} or click",
                left + 18,
                bottom + 18,
                COLOR_TEXT,
                11,
            )
            self.profile_buttons.append((index, left, right, bottom, top))

        arcade.draw_text(
            "The choice is just a starting point, not a judgment.",
            SCREEN_WIDTH / 2,
            106,
            COLOR_MUTED,
            12,
            anchor_x="center",
        )

    def draw_profile_icon(self, x: float, y: float, profile: CharacterProfile) -> None:
        """Draw a tiny stick figure on the intro cards."""

        accent = profile.accent
        if profile.body_type == "fat":
            head_radius = 11
            torso_half = 9
            arm_span = 12
            leg_span = 11
            line_width = 3
        elif profile.body_type == "skinny":
            head_radius = 8
            torso_half = 5
            arm_span = 8
            leg_span = 8
            line_width = 1
        else:
            head_radius = 10
            torso_half = 7
            arm_span = 10
            leg_span = 9
            line_width = 2

        head_y = y + 24
        torso_top = y + 7
        torso_bottom = y - 12
        hip_y = y - 12

        shirt_left = x - torso_half
        shirt_right = x + torso_half
        shirt_top = y + 9
        shirt_bottom = y - 10
        arcade.draw_lrbt_rectangle_filled(shirt_left, shirt_right, shirt_bottom, shirt_top, accent)
        draw_outline_lrbt(shirt_left, shirt_right, shirt_bottom, shirt_top, COLOR_STICK, 1)

        arcade.draw_circle_outline(x, head_y, head_radius, COLOR_STICK, max(1, line_width - 1))
        arcade.draw_line(x - head_radius // 3, head_y + 3, x - head_radius // 3, head_y - 1, COLOR_STICK, max(1, line_width - 1))
        arcade.draw_line(x + head_radius // 3, head_y + 3, x + head_radius // 3, head_y - 1, COLOR_STICK, max(1, line_width - 1))
        arcade.draw_line(x - 1, head_y - 1, x - 1, head_y - 4, COLOR_STICK, max(1, line_width - 1))
        arcade.draw_line(x - head_radius // 2, head_y - 7, x + head_radius // 2, head_y - 7, COLOR_STICK, max(1, line_width - 1))
        arcade.draw_line(x, torso_top, x, torso_bottom, COLOR_STICK, line_width)

        # Small backpack/shoulder detail so each figure feels lived-in.
        bag_left = x - 16 - torso_half
        bag_right = x - 6
        bag_top = y + 4
        bag_bottom = y - 8
        arcade.draw_lrbt_rectangle_filled(bag_left, bag_right, bag_bottom, bag_top, accent)
        draw_outline_lrbt(bag_left, bag_right, bag_bottom, bag_top, COLOR_STICK, 1)
        arcade.draw_line(bag_left + 2, y + 1, bag_right - 2, y + 4, accent, 1)

        arcade.draw_line(x - 1, torso_top, x - arm_span, y - 2, COLOR_STICK, line_width)
        arcade.draw_line(x + 1, torso_top, x + arm_span, y - 1, COLOR_STICK, line_width)
        arcade.draw_line(x, hip_y, x - leg_span, y - 24, accent, line_width)
        arcade.draw_line(x, hip_y, x + leg_span + 1, y - 22, accent, line_width)

    def draw_world(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, COLOR_BG)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 285, 365, COLOR_ROAD)
        arcade.draw_lrbt_rectangle_filled(410, 490, 0, SCREEN_HEIGHT, COLOR_ROAD)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 272, 285, COLOR_SIDEWALK)
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 365, 378, COLOR_SIDEWALK)
        arcade.draw_lrbt_rectangle_filled(397, 410, 0, SCREEN_HEIGHT, COLOR_SIDEWALK)
        arcade.draw_lrbt_rectangle_filled(490, 503, 0, SCREEN_HEIGHT, COLOR_SIDEWALK)

        target_location = None
        if not self.game_over and self.scene_index < len(SCENES):
            target_location = SCENES[self.scene_index].location

        for building in BUILDINGS:
            arcade.draw_lrbt_rectangle_filled(building.left, building.right, building.bottom, building.top, building.color)
            arcade.draw_lrbt_rectangle_filled(building.left, building.right, building.top - 16, building.top, (38, 39, 41))
            if building.key == "bus":
                cx, cy = building.center
                for offset in (-32, -16, 0, 16, 32):
                    arcade.draw_lrbt_rectangle_filled(cx + offset - 6, cx + offset + 6, cy - 6, cy + 6, (118, 137, 156))
                    draw_outline_lrbt(cx + offset - 6, cx + offset + 6, cy - 6, cy + 6, COLOR_STICK, 1)
            if building.key == target_location:
                draw_outline_lrbt(building.left, building.right, building.bottom, building.top, COLOR_TARGET, 4)
            arcade.draw_text(building.name, building.left + 10, building.top - 12, COLOR_TEXT, 12)
            arcade.draw_text(building.prompt, building.left + 10, building.bottom + 12, (232, 225, 176), 10)

        self.draw_player()

    def draw_player(self) -> None:
        """Draw a hand-drawn stick figure that matches the reference image."""

        x = self.player_x
        y = self.player_y

        head_y = y + 34
        torso_top = y + 14
        torso_bottom = y - 16
        left_shoulder = x - 2
        right_shoulder = x + 2
        hip_x = x
        hip_y = y - 16

        # Head and face
        head_radius = 17

        shirt_left = x - 11
        shirt_right = x + 11
        shirt_top = y + 13
        shirt_bottom = y - 9
        arcade.draw_lrbt_rectangle_filled(shirt_left, shirt_right, shirt_bottom, shirt_top, self.player_accent)
        draw_outline_lrbt(shirt_left, shirt_right, shirt_bottom, shirt_top, COLOR_STICK, 2)

        arcade.draw_circle_outline(x, head_y, head_radius, COLOR_STICK, 2)
        arcade.draw_line(x - 6, head_y + 5, x - 6, head_y - 1, COLOR_STICK, 2)
        arcade.draw_line(x + 5, head_y + 5, x + 5, head_y - 1, COLOR_STICK, 2)
        arcade.draw_line(x - 1, head_y + 1, x - 1, head_y - 4, COLOR_STICK, 2)
        arcade.draw_line(x, head_y - 5, x + 3, head_y - 2, COLOR_STICK, 2)
        arcade.draw_line(x - 9, head_y - 11, x + 10, head_y - 11, COLOR_STICK, 2)

        # Torso
        arcade.draw_line(x, torso_top + 2, x, torso_bottom, COLOR_STICK, 2)

        # Backpack on the left side of the body
        bag_left = x - 33
        bag_right = x - 5
        bag_top = y + 6
        bag_bottom = y - 20
        arcade.draw_lrbt_rectangle_filled(bag_left, bag_right, bag_bottom, bag_top, COLOR_BAG)
        draw_outline_lrbt(bag_left, bag_right, bag_bottom, bag_top, COLOR_STICK, 2)
        arcade.draw_line(bag_left + 4, bag_bottom + 2, bag_left + 4, bag_top - 3, COLOR_STICK, 1)
        arcade.draw_line(bag_left + 7, bag_top - 4, bag_right - 3, bag_bottom + 3, self.player_accent, 1)
        arcade.draw_line(bag_left + 10, bag_bottom + 1, bag_right - 8, bag_top - 1, COLOR_BAG_HIGHLIGHT, 1)
        arcade.draw_line(x - 6, y + 6, x + 5, y + 1, self.player_accent, 2)

        # Arm holding the backpack
        arcade.draw_line(left_shoulder, torso_top + 2, bag_right - 1, y + 2, COLOR_STICK, 2)
        arcade.draw_line(right_shoulder, torso_top + 2, x + 14, y - 1, COLOR_STICK, 2)

        # Legs in a wide stance
        arcade.draw_line(hip_x, hip_y, x - 20, y - 60, self.player_accent, 2)
        arcade.draw_line(hip_x, hip_y, x + 26, y - 58, self.player_accent, 2)

    def draw_hud(self) -> None:
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 600, 650, (18, 19, 21, 245))
        title = "One Long Day"
        if self.selected_profile:
            title = f"One Long Day - {self.selected_profile.name}"
        arcade.draw_text(title, 18, 620, COLOR_TEXT, 18, bold=True)
        arcade.draw_text(f"Day step {self.scene_index + 1} of {len(SCENES)}", 18, 604, COLOR_MUTED, 10)
        self.draw_meter("Morality", self.patience, 180, COLOR_WARN)
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
        arcade.draw_text(self.location_name(self.current_scene.location), 108, 494, COLOR_MUTED, 12)
        arcade.draw_text(
            self.current_scene.situation,
            108,
            472,
            COLOR_TEXT,
            14,
            width=660,
            multiline=True,
        )
        arcade.draw_text(
            "Calm choices spend morality. If morality runs out, only the harshest option stays available.",
            108,
            402,
            COLOR_MUTED,
            11,
        )

        self.choice_buttons.clear()
        for index, choice in enumerate(self.current_scene.choices):
            left = 108
            right = 792
            top = 336 - index * 90
            bottom = top - 62
            locked = self.choice_locked(index)
            fill = COLOR_LOCKED if locked else self.choice_color(choice)
            arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, fill)
            arcade.draw_lrbt_rectangle_filled(left, right, top - 4, top, (255, 255, 255, 35))
            label = choice.label if not locked else "Morality is empty: this choice is unavailable."
            arcade.draw_text(label, left + 16, bottom + 36, COLOR_TEXT, 12, width=640, multiline=True)
            arcade.draw_text(self.effect_text(choice), left + 16, bottom + 13, (236, 234, 220), 10)
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
        if self.scene_index >= len(SCENES):
            return

        scene = SCENES[self.scene_index]
        building = self.get_building(scene.location)
        near = self.near_building(building)
        text = f"Next: {scene.title} at {building.name}. "
        text += "Press E to enter." if near else "Walk to the highlighted place."
        arcade.draw_lrbt_rectangle_filled(0, SCREEN_WIDTH, 0, 42, (18, 19, 21, 230))
        arcade.draw_text(text, SCREEN_WIDTH / 2, 14, COLOR_TEXT, 13, anchor_x="center")

    def draw_panel(self, left: int, right: int, bottom: int, top: int) -> None:
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, COLOR_PANEL)
        arcade.draw_lrbt_rectangle_filled(left, right, top - 3, top, COLOR_PANEL_BORDER)
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, bottom + 3, (80, 82, 78))

    def begin_game(self, profile_index: int) -> None:
        profile = CHARACTER_PROFILES[profile_index]
        self.selected_profile = profile
        self.player_accent = profile.accent
        self.started = True
        self.player_x = 145
        self.player_y = 493
        self.keys_pressed.clear()
        self.scene_index = 0
        self.current_scene = None
        self.awaiting_continue = False
        self.last_result = ""
        self.game_over = False
        self.ending_text = ""
        self.patience = max(0, min(100, 100 + profile.patience_bonus))
        self.stability = max(0, min(100, 50 + profile.stability_bonus))
        self.grades = max(0, min(100, 50 + profile.grades_bonus))
        self.family = max(0, min(100, 50 + profile.family_bonus))

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

    def location_name(self, key: str) -> str:
        return self.get_building(key).name

    def choice_color(self, choice: Choice) -> tuple[int, int, int]:
        if choice.kind == "patient":
            return (66, 103, 96)
        if choice.kind == "mixed":
            return (107, 103, 75)
        return (125, 67, 62)

    def effect_text(self, choice: Choice) -> str:
        signs = []
        for label, value in [
            ("morality", choice.patience),
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
            [("morality", self.patience), ("stability", self.stability), ("grades", self.grades), ("family trust", self.family)],
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
            Morality {self.patience} | Stability {self.stability} | Grades {self.grades} | Family {self.family}

            Your lowest area was {weakest[0]}. That does not mean you made one bad choice. It means the same choice can cost more when money, time, rest, and support are all limited.

            Average wellbeing: {average:.1f}/100
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
