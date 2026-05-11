import os
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


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "The Daily Grind"

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


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.keys_down = set()
        self.patience = 10
        self.max_patience = 10
        self.state = STATE_WALKING
        self.feedback_message = ""
        self.message_timer = 0.0

        self.player_x = 120
        self.player_y = 130
        self.player_color = arcade.color.DARK_BLUE

        self.current_turn = 0
        self.encounters = [
            {
                "npc": "Mr. Henderson",
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
                "npc": "Hall Monitor",
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
                "npc": "Ms. Rivera",
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

        assets_path = os.path.join(os.path.dirname(__file__), "assets", "drawing.jpg")
        self.drawing_texture = None
        self.drawing_path = None
        if os.path.exists(assets_path):
            try:
                self.drawing_texture = arcade.load_texture(assets_path)
                self.drawing_path = assets_path
            except Exception:
                self.drawing_texture = None
                self.drawing_path = None

        self.setup()

    def setup(self):
        self.reset_game()

    def reset_game(self):
        self.patience = 10
        self.state = STATE_WALKING
        self.feedback_message = "Walk to the school gate and press E."
        self.message_timer = 0.0
        self.player_x = 120
        self.player_y = 130
        self.current_turn = 0
        self.current_npc = ""
        self.dialogue_text = ""
        self.options = []
        self.keys_down.clear()

    def start_conversation(self):
        self.state = STATE_CONVERSATION
        self.current_turn = 0
        self.set_current_encounter_text()
        self.feedback_message = "Press 1, 2, or 3 to respond."
        self.message_timer = 0.0

    def set_current_encounter_text(self):
        encounter = self.encounters[self.current_turn]
        self.current_npc = encounter["npc"]
        self.dialogue_text = encounter["prompt"]
        self.options = encounter["options"]

    def finish_encounter(self, choice):
        encounter = self.encounters[self.current_turn]
        delta, response = encounter["outcomes"][choice - 1]
        self.patience = clamp(self.patience + delta, 0, self.max_patience)
        self.feedback_message = response
        self.message_timer = 0.0

        if self.patience <= 0:
            self.state = STATE_GAME_OVER
            self.feedback_message = response + " You ran out of patience."
            return

        self.current_turn += 1
        if self.current_turn >= len(self.encounters):
            self.state = STATE_WIN
            self.feedback_message = "You made it through the morning. Nice work."
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
        rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.SKY_BLUE)
        rect_filled(580, 280, 360, 280, arcade.color.GRAY)
        rect_filled(580, 430, 380, 90, arcade.color.DARK_RED)
        rect_filled(400, 50, SCREEN_WIDTH, 100, arcade.color.BLACK_OLIVE)
        rect_filled(GATE_X, GATE_Y, 90, 20, arcade.color.BROWN_NOSE)
        rect_outline(GATE_X, GATE_Y, 90, 40, arcade.color.BLACK, 2)

        arcade.draw_text("School", 500, 520, arcade.color.WHITE, 24, bold=True)

        if self.state == STATE_WALKING:
            arcade.draw_text("Walk to the gate. Press E to talk.", 20, 570, arcade.color.BLACK, 14)
            if self.distance_to_gate() <= GATE_RADIUS:
                arcade.draw_text("Press E", GATE_X - 30, GATE_Y + 35, arcade.color.DARK_GREEN, 14, bold=True)

        self.draw_player()

    def draw_player(self):
        rect_filled(self.player_x, self.player_y, PLAYER_SIZE, PLAYER_SIZE * 1.2, self.player_color)
        rect_outline(self.player_x, self.player_y, PLAYER_SIZE, PLAYER_SIZE * 1.2, arcade.color.WHITE, 2)

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

    def draw_conversation_box(self):
        dialog_cx = SCREEN_WIDTH / 2
        dialog_cy = 115
        rect_filled(dialog_cx, dialog_cy, 760, 180, arcade.color.WHITE_SMOKE)
        rect_outline(dialog_cx, dialog_cy, 760, 180, arcade.color.BLACK, 2)

        if self.drawing_texture:
            img_x = 120
            img_y = dialog_cy + 8
            img_w = 150
            img_h = 110
            try:
                arcade.draw_texture_rectangle(img_x, img_y, img_w, img_h, self.drawing_texture)
            except AttributeError:
                try:
                    sprite = arcade.Sprite(self.drawing_path)
                    sprite.center_x = img_x
                    sprite.center_y = img_y
                    sprite.width = img_w
                    sprite.height = img_h
                    sprite.draw()
                except Exception:
                    pass

        text_x = 220
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
            300,
            arcade.color.DARK_RED,
            14,
            italic=True,
        )

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
            if key in INTERACT_KEYS and self.distance_to_gate() <= GATE_RADIUS:
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
