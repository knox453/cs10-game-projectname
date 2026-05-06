import sys
import time

def slow_print(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)
    print()

class GameState:
    def __init__(self):
        self.patience = 10
        self.max_patience = 10
        self.suspended = False
        self.failed_class = False
        self.kicked_out = False

    def display_status(self):
        bar = "▮" * self.patience + "▯" * (self.max_patience - self.patience)
        print(f"\n--- STATUS ---")
        print(f"PATIENCE: [{bar}] ({self.patience}/{self.max_patience})")
        print("--------------\n")

    def clamp_patience(self):
        if self.patience > self.max_patience:
            self.patience = self.max_patience
        if self.patience < 0:
            self.patience = 0

def play_game():
    state = GameState()

    slow_print("--- THE DAILY GRIND: A PAPER PROTOTYPE ---")
    slow_print("You wake up tired. The walk to school is long.")

    # --- SCENE 1: SCHOOL ---
    state.display_status()
    slow_print("Mr. Henderson is at the door. He looks annoyed.")
    slow_print("Henderson: 'Late again? And no essay? What do you have to say?'")

    # Mechanic: If patience is 0, player is forced into the worst option
    if state.patience <= 0:
        slow_print("!! You've lost your cool. You can only lash out. !!")
        choice = "C"
    else:
        print("A) Apologize and promise it by lunch (-3 Patience)")
        print("B) Ignore him and walk to your desk (-1 Patience, fail assignment)")
        print("C) Curse him out and tell him to get off your back (+4 Patience)")
        choice = input("Choose A, B, or C: ").upper()

    if choice == "A":
        state.patience -= 3
        slow_print("Henderson: 'Fine. Lunchtime. Don't be late.'")
    elif choice == "B":
        state.patience -= 1
        state.failed_class = True
        slow_print("You walk past. Henderson sighs and marks a '0' in his book.")
    else:
        state.patience += 4
        state.suspended = True
        slow_print("Henderson: 'Office. NOW. Don't come back until Monday.'")

    state.clamp_patience()

    # --- SCENE 2: THE GAS STATION ---
    state.display_status()
    if state.suspended:
        slow_print("You're walking home early because of the suspension.")
    else:
        slow_print("School is finally over. You're walking past the 7-11.")

    slow_print("The Crew is outside. Marcus waves you over.")
    slow_print("Marcus: 'Yo, come chill with us for a bit. You look stressed.'")

    if state.patience <= 0:
        slow_print("!! You're too exhausted to deal with Mom. You head to the crew. !!")
        choice = "B"
    else:
        print("A) Go home to Mom. (Mom happy, -5 Patience)")
        print("B) Hang out with the guys. (Feel better, +6 Patience, Mom will be furious)")
        choice = input("Choose A or B: ").upper()

    if choice == "A":
        state.patience -= 5
        slow_print("You go home. Your mom smiles, but the silence of the house is heavy.")
    else:
        state.patience += 6
        slow_print("You laugh and talk for an hour. You feel like a person again.")
        slow_print("But when you get home, your Mom is waiting at the door...")
        if state.suspended:
            state.kicked_out = True
        else:
            slow_print("Mom: 'I told you to stay away from them! Get in your room!'")

    state.clamp_patience()

    # --- ENDING ---
    print("\n=== DAY END ===")
    if state.kicked_out:
        print("RESULT: Your mom found out about the suspension and the crew. She kicked you out.")
    elif state.failed_class:
        print("RESULT: You stayed out of trouble, but you're failing school.")
    else:
        print("RESULT: You survived the day, but the cycle repeats tomorrow.")

    state.display_status()

if __name__ == "__main__":
    play_game()
