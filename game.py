/    def draw_scene(self) -> None:
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
