# ...existing code...
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
        return arcade.draw_lrtb_rectangle_filled(left, right, top, bottom, color)

def rect_outline(cx, cy, width, height, color, border_width=1):
    try:
        return arcade.draw_rectangle_outline(cx, cy, width, height, color, border_width)
    except AttributeError:
        left = cx - width / 2
        right = cx + width / 2
        top = cy + height / 2
        bottom = cy - height / 2
        return arcade.draw_lrtb_rectangle_outline(left, right, top, bottom, color, border_width)
# ...existing code...

    def on_draw(self):
        # Ensure we call the proper render start for the arcade/pyglet version
        try:
            # arcade 2.x uses start_render()
            arcade.start_render()
        except AttributeError:
            # arcade 3.x+ uses clear()
            self.clear()

        # Draw a guaranteed visible background (in case set_background_color didn't take effect)
-        arcade.draw_rectangle_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
-                                     SCREEN_WIDTH, SCREEN_HEIGHT,
-                                     arcade.color.SKY_BLUE)
+        rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
+                    SCREEN_WIDTH, SCREEN_HEIGHT,
+                    arcade.color.SKY_BLUE)

        # --- 1. Draw the Background (Updated Names) ---
-        arcade.draw_rectangle_filled(450, 200, 300, 400, arcade.color.GRAY)
-        arcade.draw_rectangle_filled(400, 50, 800, 100, arcade.color.BLACK_OLIVE)
+        rect_filled(450, 200, 300, 400, arcade.color.GRAY)
+        rect_filled(400, 50, 800, 100, arcade.color.BLACK_OLIVE)

        # --- 2. Draw UI / Patience Bar ---
        arcade.draw_text("Patience:", 20, 560, arcade.color.BLACK, 14)
        bar_width = (self.patience / self.max_patience) * 200
        if bar_width > 0:
            rect_filled(80 + bar_width / 2, 570, bar_width, 20, arcade.color.CRIMSON)
+        rect_outline(80 + 200 / 2, 570, 200, 20, arcade.color.BLACK)

        # --- 3. Draw Conversation Box ---
        if self.state == STATE_CONVERSATION:
            rect_filled(20 + 760 / 2, 20 + 150 / 2, 760, 150, arcade.color.WHITE_SMOKE)
            rect_outline(20 + 760 / 2, 20 + 150 / 2, 760, 150, arcade.color.BLACK)
            arcade.draw_text(f"{self.current_npc}:", 40, 140, arcade.color.DARK_BLUE_GRAY, 16, bold=True)
            arcade.draw_text(self.dialogue_text, 40, 110, arcade.color.BLACK, 14)
            for i, option in enumerate(self.options):
                arcade.draw_text(option, 40, 80 - (i * 25), arcade.color.BLACK, 12)

        arcade.draw_text(self.feedback_message, 40, 250, arcade.color.RED, 14, italic=True)
# ...existing code...

    def on_key_press(self, key, modifiers):
        if self.state == STATE_CONVERSATION:
            # If patience is 0, only snapping is allowed
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
        if self.patience < 0: self.patience = 0
        if self.patience > self.max_patience: self.patience = self.max_patience

        # Close conversation after a delay or another key press
        # (For this prototype, we'll just freeze on the choice)

def main():
    game = MyGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
# ...existing code...
