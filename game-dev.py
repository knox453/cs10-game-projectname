import arcade

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "The Daily Grind - Paper Prototype"

# Game States
STATE_WALKING = 0
STATE_CONVERSATION = 1
STATE_GAME_OVER = 2

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Game Stats
        self.patience = 10
        self.max_patience = 10
        self.state = STATE_CONVERSATION # Start at the school gate

        # Conversation logic
        self.current_npc = "Mr. Henderson"
        self.dialogue_text = "Late again? And no essay? What do you have to say?"
        self.options = ["[1] Apologize (-3 Pat)", "[2] Ignore (-1 Pat)", "[3] Snap (+4 Pat)"]
        self.feedback_message = ""

    def setup(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        arcade.start_render()

    # --- 1. Draw the Background (Based on your sketches) ---
        # School building
        arcade.draw_rectangle_filled(600, 400, 300, 400, arcade.color.GRAY)
        arcade.draw_triangle_filled(450, 600, 750, 600, 600, 700, arcade.color.DARK_RED)

        # Road
        arcade.draw_rectangle_filled(400, 50, 800, 100, arcade.color.BLACK_OLIVE)

    # --- 2. Draw UI / Patience Bar ---
        arcade.draw_text(f"Patience:", 20, 560, arcade.color.BLACK, 14)
        # Background of bar
        arcade.draw_rectangle_outline(180, 570, 200, 20, arcade.color.BLACK, 2)
        # Filling the bar
        bar_width = (self.patience / self.max_patience) * 200
        if bar_width > 0:
            arcade.draw_rectangle_filled(80 + (bar_width / 2), 570, bar_width, 16, arcade.color.CRIMSON)

    # --- 3. Draw Conversation Box ---
        if self.state == STATE_CONVERSATION:
            # Dialogue box
            arcade.draw_rectangle_filled(400, 150, 760, 150, arcade.color.WHITE_SMOKE)
            arcade.draw_rectangle_outline(400, 150, 760, 150, arcade.color.BLACK, 3)

            # NPC Name and Text
            arcade.draw_text(f"{self.current_npc}:", 40, 200, arcade.color.DARK_BLUE_GRAY, 16, bold=True)
            arcade.draw_text(self.dialogue_text, 40, 175, arcade.color.BLACK, 14)

            # Draw Options
            for i, option in enumerate(self.options):
                arcade.draw_text(option, 40, 130 - (i * 25), arcade.color.BLACK, 12)

        # Feedback message
        arcade.draw_text(self.feedback_message, 40, 250, arcade.color.RED, 14, italic=True)

    def on_key_press(self, key, modifiers):
        if self.state == STATE_CONVERSATION:
            # If patience is 0, only snapping is allowed
            if self.patience <= 0:
                if key == arcade.key.KEY_3:
                    self.handle_choice(3)
                return

            if key == arcade.key.KEY_1:
                self.handle_choice(1)
            elif key == arcade.key.KEY_2:
                self.handle_choice(2)
            elif key == arcade.key.KEY_3:
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
        if self.patience > 10: self.patience = 10

        # Close conversation after a delay or another key press
        # (For this prototype, we'll just freeze on the choice)

def main():
    game = MyGame()
    game.setup()
    arcade.run()

if __name__ == "__main__":
    main()
