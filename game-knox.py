
python
import os
import arcade

# Helper compatibility wrappers for different arcade versions
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

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "The Daily Grind - Paper Prototype"

STATE_WALKING = 0
STATE_CONVERSATION = 1
STATE_GAME_OVER = 2

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.patience = 10
        self.max_patience = 10
        self.state = STATE_CONVERSATION
        self.current_npc = "Mr. Henderson"
        self.dialogue_text = "Late again? And no essay? What do you have to say?"
        self.options = ["[1] Apologize (-3 Pat)", "[2] Ignore (-1 Pat)", "[3] Snap (+4 Pat)"]
        self.feedback_message = ""

        # Load optional drawing at assets/drawing.jpg
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "drawing.jpg")
        if os.path.exists(assets_path):
            try:
                self.drawing_texture = arcade.load_texture(assets_path)
                self.drawing_path = assets_path
            except Exception:
                self.drawing_texture = None
                self.drawing_path = None
        else:
            self.drawing_texture = None
            self.drawing_path = None

    def setup(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        # ✅ FIX: Use self.clear() instead of arcade.start_render()
        self.clear()

        # Background
        rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                    SCREEN_WIDTH, SCREEN_HEIGHT,
                    arcade.color.SKY_BLUE)

        # Scene
        rect_filled(450, 200, 300, 400, arcade.color.GRAY)
        rect_filled(400, 50, 800, 100, arcade.color.BLACK_OLIVE)

        # UI / Patience bar
        arcade.draw_text("Patience:", 20, 560, arcade.color.BLACK, 14)
        bar_width = (self.patience / self.max_patience) * 200
        if bar_width > 0:
            rect_filled(80 + bar_width / 2, 570, bar_width, 20, arcade.color.CRIMSON)
        rect_outline(80 + 200 / 2, 570, 200, 20, arcade.color.BLACK)

        # Conversation box
        if self.state == STATE_CONVERSATION:
            dialog_cx = 20 + 760 / 2
            dialog_cy = 20 + 150 / 2
            rect_filled(dialog_cx, dialog_cy, 760, 150, arcade.color.WHITE_SMOKE)
            rect_outline(dialog_cx, dialog_cy, 760, 150, arcade.color.BLACK)

            # Draw optional image in the left of the dialogue area
            if getattr(self, "drawing_texture", None):
                img_w = 160
                img_h = 120
                img_x = 120
                img_y = dialog_cy - 10
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

            # Text offset to the right of the image area
            text_x = 40 + 140
            arcade.draw_text(f"{self.current_npc}:", text_x, 140, arcade.color.DARK_BLUE_GRAY, 16, bold=True)
            arcade.draw_text(self.dialogue_text, text_x, 110, arcade.color.BLACK, 14)
            for i, option in enumerate(self.options):
                arcade.draw_text(option, text_x, 80 - (i * 25), arcade.color.BLACK, 12)

        # Feedback
        arcade.draw_text(self.feedback_message, 40, 250, arcade.color.RED, 14, italic=True)

    def on_key_press(self, key, modifiers):
        if self.state == STATE_CONVERSATION:
            if self.patience <= 0:
                if key == arcade.key._3:
                    self.handle_choice(3)
                return

            if key == arcade.key._1:
                self.handle_choice(1)
            elif key == arcade.key._2:
                self.handle_choice(2)
            elif key == arcade.key._3:
                self.handle_choice(3)

    def handle_choice(self, choice):
        if choice == 1:
            self.patience -= 3
            self.feedback_message = "You swallowed your pride. You're exhausted."
        elif choice == 2:
            self.patience -= 1
            self.feedback_message = "You ignored him. He marks a zero in the book."
        elif choice == 3:
            self.patience += 4
            self.feedback_message = "You snapped! You're going to the office."

        # Clamp patience
        if self.patience < 0:
            self.patience = 0
        if self.patience > self.max_patience:
            self.patience = self.max_patience

def main():
    game = MyGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()

