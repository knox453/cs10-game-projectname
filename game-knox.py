import arcade


def rect_filled(cx, cy, width, height, color):
    try:
        return arcade.draw_rectangle_filled(cx, cy, width, height, color)
    except AttributeError:
        left = cx - width / 2
        right = cx + width / 2
        top = cy + height / 2
        bottom = cy - height / 2
        try:
            return arcade.draw_lrtb_rectangle_filled(left, right, top, bottom, color)
        except AttributeError:
            points = [(left, bottom), (left, top), (right, top), (right, bottom)]
            try:
                return arcade.draw_polygon_filled(points, color)
            except AttributeError:
                try:
                    arcade.draw_triangle_filled(left, bottom, left, top, right, top, color)
                    arcade.draw_triangle_filled(left, bottom, right, top, right, bottom, color)
                except Exception:
                    pass


def rect_outline(cx, cy, width, height, color, border_width=1):
    try:
        return arcade.draw_rectangle_outline(cx, cy, width, height, color, border_width)
    except AttributeError:
        left = cx - width / 2
        right = cx + width / 2
        top = cy + height / 2
        bottom = cy - height / 2
        try:
            return arcade.draw_lrtb_rectangle_outline(left, right, top, bottom, color, border_width)
        except AttributeError:
            points = [(left, bottom), (left, top), (right, top), (right, bottom)]
            try:
                return arcade.draw_polygon_outline(points, color)
            except AttributeError:
                try:
                    arcade.draw_line(left, bottom, left, top, color, border_width)
                    arcade.draw_line(left, top, right, top, color, border_width)
                    arcade.draw_line(right, top, right, bottom, color, border_width)
                    arcade.draw_line(right, bottom, left, bottom, color, border_width)
                except Exception:
                    pass


def clamp(value, low, high):
    return max(low, min(high, value))


def draw_pixel_rect(cx, cy, width, height, color):
    rect_filled(round(cx), round(cy), round(width), round(height), color)


def draw_pixel_art(origin_x, origin_y, scale, pattern, palette):
    rows = len(pattern)
    cols = max(len(row) for row in pattern)
    start_x = origin_x - (cols * scale) / 2 + scale / 2
    start_y = origin_y + (rows * scale) / 2 - scale / 2

    for row_index, row in enumerate(pattern):
        for col_index, cell in enumerate(row):
            color = palette.get(cell)
            if color is None:
                continue
            x = start_x + col_index * scale
            y = start_y - row_index * scale
            draw_pixel_rect(x, y, scale, scale, color)


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "The Daily Grind"
WORLD_WIDTH = 2400
WORLD_HEIGHT = 800

STATE_WALKING = 0
STATE_CONVERSATION = 1
STATE_WIN = 2
STATE_GAME_OVER = 3

MOVE_SPEED = 220
PLAYER_SIZE = 28
GATE_X = 660
GATE_Y = 150
GATE_RADIUS = 90

CHOICE_KEYS = {
    1: {arcade.key.KEY_1, arcade.key.NUM_1},
    2: {arcade.key.KEY_2, arcade.key.NUM_2},
    3: {arcade.key.KEY_3, arcade.key.NUM_3},
}

MOVE_LEFT_KEYS = {arcade.key.LEFT, arcade.key.A}
MOVE_RIGHT_KEYS = {arcade.key.RIGHT, arcade.key.D}
MOVE_UP_KEYS = {arcade.key.UP, arcade.key.W}
MOVE_DOWN_KEYS = {arcade.key.DOWN, arcade.key.S}
INTERACT_KEYS = {arcade.key.E}
RESTART_KEYS = {arcade.key.R}

PLAYER_PATTERN = [
    "....HH....",
    "...HSSH...",
    "..HSSSSH..",
    "..HSSSSH..",
    "...CCCC...",
    "..CCCCCCH.",
    "..CPPPPC..",
    "...P..P...",
    "..WW..WW..",
    ".BBBBBBBB.",
]

PLAYER_PALETTE = {
    ".": None,
    "H": arcade.color.BLACK,
    "S": arcade.color.PEACH,
    "C": arcade.color.DARK_BLUE,
    "P": arcade.color.BROWN_NOSE,
    "W": arcade.color.WHITE,
    "B": arcade.color.BLACK,
}


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.world_camera = arcade.Camera2D(window=self)
        self.ui_camera = arcade.Camera2D(
            window=self,
            position=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
        )

        self.keys_down = set()
        self.patience = 10
        self.max_patience = 10
        self.state = STATE_WALKING
        self.feedback_message = ""

        self.player_x = 120
        self.player_y = 130

        self.task_index = 0
        self.tasks = [
            {
                "name": "Pack Backpack",
                "npc": "Your Desk",
                "location": (160, 150),
                "radius": 70,
                "prompt": "Your backpack is open and messy. What do you do first?",
                "options": [
                    "[1] Pack neatly",
                    "[2] Rush it",
                    "[3] Leave a mess",
                ],
                "outcomes": [
                    (1, "You pack everything neatly. Nice start."),
                    (-1, "You rush and forget your charger."),
                    (-2, "You leave a mess and waste time later."),
                ],
            },
            {
                "name": "Eat Breakfast",
                "npc": "Kitchen Table",
                "location": (260, 235),
                "radius": 70,
                "prompt": "You are running late, but breakfast is still on the table.",
                "options": [
                    "[1] Eat up",
                    "[2] Grab a snack",
                    "[3] Skip it",
                ],
                "outcomes": [
                    (1, "You eat breakfast and feel a little steadier."),
                    (0, "You grab a snack for the road."),
                    (-2, "Skipping breakfast makes the morning harder."),
                ],
            },
            {
                "name": "Catch the Bus",
                "npc": "Bus Stop",
                "location": (620, 155),
                "radius": 75,
                "prompt": "The bus is pulling in. How do you handle it?",
                "options": [
                    "[1] Wait patiently",
                    "[2] Sprint for it",
                    "[3] Argue with the driver",
                ],
                "outcomes": [
                    (1, "You wait it out and make it aboard calm."),
                    (-1, "You make it on, but you're winded."),
                    (-2, "The driver is not impressed by the attitude."),
                ],
            },
            {
                "name": "Talk to Teacher",
                "npc": "Mr. Henderson",
                "location": (1660, 150),
                "radius": GATE_RADIUS,
                "prompt": "Late again? And no essay? What do you have to say?",
                "options": [
                    "[1] Apologize",
                    "[2] Ignore",
                    "[3] Snap",
                ],
                "outcomes": [
                    (-2, "You apologize. He sighs, but keeps listening."),
                    (-1, "You stay quiet. That does not help much."),
                    (2, "You snap back. Bad move, but it feels powerful."),
                ],
            },
            {
                "name": "Hall Pass Check",
                "npc": "Hall Monitor",
                "location": (1820, 255),
                "radius": 70,
                "prompt": "Hall pass check. Why are you still outside class?",
                "options": [
                    "[1] Be honest",
                    "[2] Lie",
                    "[3] Rush past",
                ],
                "outcomes": [
                    (-1, "You tell the truth. She points you toward class."),
                    (-2, "Your lie falls apart instantly."),
                    (2, "You sprint past. The monitor is not impressed."),
                ],
            },
            {
                "name": "Turn In Homework",
                "npc": "Ms. Rivera",
                "location": (1940, 320),
                "radius": 80,
                "prompt": "You made it to homeroom. Last chance: finish strong?",
                "options": [
                    "[1] Focus up",
                    "[2] Dodge work",
                    "[3] Defend yourself",
                ],
                "outcomes": [
                    (-1, "You lock in and keep going."),
                    (-2, "You avoid the work and lose more patience."),
                    (1, "You push back, but at least you stay in the fight."),
                ],
            },
        ]
        self.current_npc = ""
        self.dialogue_text = ""
        self.options = []

        self.setup()

    def setup(self):
        self.reset_game()

    def reset_game(self):
        self.patience = 10
        self.state = STATE_WALKING
        self.feedback_message = "Start your day and work through the tasks."
        self.player_x = 140
        self.player_y = 120
        self.task_index = 0
        self.current_npc = ""
        self.dialogue_text = ""
        self.options = []
        self.keys_down.clear()

    def current_task(self):
        if self.task_index < len(self.tasks):
            return self.tasks[self.task_index]
        return None

    def start_conversation(self):
        task = self.current_task()
        if task is None:
            return
        self.state = STATE_CONVERSATION
        self.set_current_encounter_text()
        self.feedback_message = "Press 1, 2, or 3 to respond."

    def set_current_encounter_text(self):
        task = self.current_task()
        if task is None:
            return
        self.current_npc = task["npc"]
        self.dialogue_text = task["prompt"]
        self.options = task["options"]

    def finish_encounter(self, choice):
        task = self.current_task()
        if task is None:
            return
        delta, response = task["outcomes"][choice - 1]
        self.patience = clamp(self.patience + delta, 0, self.max_patience)
        self.feedback_message = response

        if self.patience <= 0:
            self.state = STATE_GAME_OVER
            self.feedback_message = response + " You ran out of patience."
            return

        self.task_index += 1
        if self.task_index >= len(self.tasks):
            self.state = STATE_WIN
            self.feedback_message = "You made it through the whole day. Nice work."
            return

        self.set_current_encounter_text()

    def on_draw(self):
        self.clear()
        self.draw_scene()

        if self.state == STATE_CONVERSATION:
            self.draw_conversation_box()
        else:
            self.draw_hud_text()

        if self.state == STATE_WIN:
            self.draw_center_banner("You Win! Press R to play again.")
        elif self.state == STATE_GAME_OVER:
            self.draw_center_banner("Game Over. Press R to restart.")

    def draw_scene(self):
        self.world_camera.use()
        rect_filled(WORLD_WIDTH / 2, WORLD_HEIGHT / 2, WORLD_WIDTH, WORLD_HEIGHT, arcade.color.SKY_BLUE)
        self.draw_pixel_background()
        self.draw_task_markers()

        if self.state == STATE_WALKING:
            task = self.current_task()
            task_name = task["name"] if task else "Done"
            arcade.draw_text(
                f"Task {self.task_index + 1}/{len(self.tasks)}: {task_name}",
                20,
                570,
                arcade.color.BLACK,
                14,
                bold=True,
            )
            if task and self.distance_to_task(task) <= task["radius"]:
                arcade.draw_text("Press E", task["location"][0] - 30, task["location"][1] + 35, arcade.color.DARK_GREEN, 14, bold=True)

        self.draw_player()

    def draw_pixel_background(self):
        # yard and road
        rect_filled(400, 52, 800, 104, arcade.color.DARK_OLIVE_GREEN)
        rect_filled(400, 90, 800, 18, arcade.color.OLIVE_DRAB)
        rect_filled(395, 150, 790, 26, arcade.color.DIM_GRAY)

        # house
        rect_filled(150, 230, 170, 130, arcade.color.SLATE_GRAY)
        rect_filled(150, 305, 190, 54, arcade.color.DARK_RED)
        rect_outline(150, 230, 170, 130, arcade.color.BLACK, 3)
        rect_outline(150, 305, 190, 54, arcade.color.BLACK, 3)
        rect_filled(150, 195, 42, 58, arcade.color.BROWN_NOSE)
        rect_outline(150, 195, 42, 58, arcade.color.BLACK, 2)
        rect_filled(110, 245, 30, 24, arcade.color.LIGHT_BLUE)
        rect_filled(190, 245, 30, 24, arcade.color.LIGHT_BLUE)
        rect_outline(110, 245, 30, 24, arcade.color.BLACK, 2)
        rect_outline(190, 245, 30, 24, arcade.color.BLACK, 2)

        # school building
        rect_filled(575, 290, 340, 250, arcade.color.SLATE_GRAY)
        rect_filled(575, 430, 360, 84, arcade.color.DARK_RED)
        rect_outline(575, 290, 340, 250, arcade.color.BLACK, 3)
        rect_outline(575, 430, 360, 84, arcade.color.BLACK, 3)

        # windows and door
        for wx in (510, 575, 640):
            for wy in (345, 300):
                rect_filled(wx, wy, 34, 34, arcade.color.LIGHT_BLUE)
                rect_outline(wx, wy, 34, 34, arcade.color.BLACK, 2)
        rect_filled(575, 205, 64, 92, arcade.color.BROWN_NOSE)
        rect_outline(575, 205, 64, 92, arcade.color.BLACK, 2)
        rect_filled(575, 250, 14, 14, arcade.color.BLACK)

        # gate and path
        rect_filled(GATE_X, GATE_Y - 10, 110, 16, arcade.color.BROWN_NOSE)
        rect_outline(GATE_X, GATE_Y - 10, 110, 16, arcade.color.BLACK, 2)
        rect_filled(620, 120, 120, 28, arcade.color.DIM_GRAY)
        rect_filled(730, 120, 110, 28, arcade.color.DIM_GRAY)
        rect_filled(280, 140, 70, 24, arcade.color.DARK_BLUE)
        rect_outline(280, 140, 70, 24, arcade.color.BLACK, 2)
        arcade.draw_text("BUS", 258, 132, arcade.color.WHITE, 14, bold=True)

        # cloud blocks
        for cx, cy in ((120, 520), (180, 500), (650, 530), (710, 505)):
            rect_filled(cx, cy, 34, 18, arcade.color.WHITE)

        arcade.draw_text("The Daily Grind", 22, 515, arcade.color.BLACK, 20, bold=True)

    def draw_task_markers(self):
        if self.state == STATE_WIN:
            return
        for index, task in enumerate(self.tasks):
            x, y = task["location"]
            if index < self.task_index:
                marker_color = arcade.color.DARK_GREEN
            elif index == self.task_index:
                marker_color = arcade.color.GOLD
            else:
                marker_color = arcade.color.LIGHT_GRAY
            rect_filled(x, y + 46, 18, 18, marker_color)
            rect_outline(x, y + 46, 18, 18, arcade.color.BLACK, 2)
            arcade.draw_text(task["name"], x, y + 60, arcade.color.BLACK, 9, anchor_x="center")

    def draw_player(self):
        draw_pixel_art(self.player_x, self.player_y + 3, 9, PLAYER_PATTERN, PLAYER_PALETTE)
        rect_outline(self.player_x, self.player_y + 5, 82, 96, arcade.color.WHITE, 1)

    def draw_hud_text(self):
        arcade.draw_text("Patience:", 20, 560, arcade.color.BLACK, 14)
        bar_width = (self.patience / self.max_patience) * 200
        if bar_width > 0:
            rect_filled(80 + bar_width / 2, 570, bar_width, 20, arcade.color.CRIMSON)
        rect_outline(180, 570, 200, 20, arcade.color.BLACK, 2)
        arcade.draw_text(f"{self.patience}/{self.max_patience}", 195, 560, arcade.color.BLACK, 12)

        arcade.draw_text(self.feedback_message, 20, 525, arcade.color.DARK_RED, 14, italic=True)
        arcade.draw_text(
            "Move: Arrow Keys or WASD   Interact: E   Restart: R",
            20,
            20,
            arcade.color.BLACK,
            12,
        )
        arcade.draw_text(
            f"Patience: {self.patience}/{self.max_patience}",
            640,
            20,
            arcade.color.BLACK,
            12,
            anchor_x="left",
        )

    def draw_conversation_box(self):
        dialog_cx = SCREEN_WIDTH / 2
        dialog_cy = 115
        rect_filled(dialog_cx, dialog_cy, 760, 180, arcade.color.WHITE_SMOKE)
        rect_outline(dialog_cx, dialog_cy, 760, 180, arcade.color.BLACK, 2)

        # NPC portrait as chunky pixel art
        self.draw_npc_portrait(112, 115)

        text_x = 200
        arcade.draw_text(self.current_npc, text_x, 230, arcade.color.DARK_BLUE_GRAY, 16, bold=True)
        arcade.draw_text(
            self.dialogue_text,
            text_x,
            185,
            arcade.color.BLACK,
            14,
            width=500,
            multiline=True,
        )

        for i, option in enumerate(self.options):
            arcade.draw_text(option, text_x, 145 - (i * 24), arcade.color.BLACK, 12)

        arcade.draw_text(
            f"Patience: {self.patience}/{self.max_patience}",
            620,
            230,
            arcade.color.BLACK,
            12,
            bold=True,
        )
        arcade.draw_text(
            self.feedback_message,
            20,
            295,
            arcade.color.DARK_RED,
            14,
            italic=True,
        )

    def draw_npc_portrait(self, cx, cy):
        portrait = [
            "...HHHH...",
            "..HSSSSH..",
            ".HSSSSSSH.",
            ".HSSHHSSH.",
            ".HSSSSSSH.",
            "..HCCCCH..",
            "..HCCCCH..",
            "...HHHH...",
        ]
        palette = {
            ".": None,
            "H": arcade.color.BLACK,
            "S": arcade.color.PEACH,
            "C": arcade.color.DARK_BLUE,
        }
        draw_pixel_art(cx, cy, 10, portrait, palette)

    def draw_center_banner(self, text):
        rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 520, 120, arcade.color.WHITE_SMOKE)
        rect_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, 520, 120, arcade.color.BLACK, 3)
        arcade.draw_text(
            text,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 10,
            arcade.color.BLACK,
            18,
            anchor_x="center",
        )

    def distance_to_gate(self):
        return ((self.player_x - GATE_X) ** 2 + (self.player_y - GATE_Y) ** 2) ** 0.5

    def distance_to_task(self, task):
        x, y = task["location"]
        return ((self.player_x - x) ** 2 + (self.player_y - y) ** 2) ** 0.5

    def on_update(self, delta_time):
        if self.state != STATE_WALKING:
            return

        dx = 0
        dy = 0
        if any(key in self.keys_down for key in MOVE_LEFT_KEYS):
            dx -= 1
        if any(key in self.keys_down for key in MOVE_RIGHT_KEYS):
            dx += 1
        if any(key in self.keys_down for key in MOVE_UP_KEYS):
            dy += 1
        if any(key in self.keys_down for key in MOVE_DOWN_KEYS):
            dy -= 1

        if dx or dy:
            self.player_x += dx * MOVE_SPEED * delta_time
            self.player_y += dy * MOVE_SPEED * delta_time
            self.player_x = clamp(self.player_x, PLAYER_SIZE / 2, SCREEN_WIDTH - PLAYER_SIZE / 2)
            self.player_y = clamp(self.player_y, PLAYER_SIZE / 2 + 100, SCREEN_HEIGHT - PLAYER_SIZE / 2)

    def on_key_press(self, key, modifiers):
        self.keys_down.add(key)

        if key in RESTART_KEYS and self.state in {STATE_WIN, STATE_GAME_OVER}:
            self.reset_game()
            return

        if self.state == STATE_WALKING:
            task = self.current_task()
            if key in INTERACT_KEYS and task and self.distance_to_task(task) <= task["radius"]:
                self.start_conversation()
            return

        if self.state == STATE_CONVERSATION:
            for choice, keys in CHOICE_KEYS.items():
                if key in keys:
                    self.finish_encounter(choice)
                    return

    def on_key_release(self, key, modifiers):
        self.keys_down.discard(key)


def main():
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
