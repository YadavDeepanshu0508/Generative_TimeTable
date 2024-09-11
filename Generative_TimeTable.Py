import json
import os
import secrets
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

# File to save and load the timetable data
TIMETABLE_FILE = "timetable_data.json"

# Define the slot timings
slot_timings = {
    0: "9:00-9:55 AM",
    1: "10:00-10:55 AM",
    2: "11:00-11:55 PM",
    3: "12:00-12:55 PM",
    4: "1:00-1:55 PM",
    5: "2:00-2:55 PM"
}

# Subjects
subs = ["C Programming", "Engineering Maths", "Linux Lab", "Managing Self", "Free", "Physics", "Problem Solving", "Environmental Studies"]

# Load timetable from file or initialize default
def load_timetable():
    try:
        with open(TIMETABLE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            "Batch A": {
                "Monday": ["C Programming", "Linux Lab", "Free", "Lunch", "Managing Self", "Free"],
                "Tuesday": ["Problem Solving", "Engineering Maths", "Environmental Studies", "Lunch", "Engineering Maths", "C Programming"],
                "Wednesday": ["C Programming", "Free", "Engineering Maths", "Lunch", "Free", "Free"],
                "Thursday": ["Problem Solving", "Free", "Physics", "Lunch", "Engineering Maths", "Free"],
                "Friday": ["Environmental Studies", "C Programming", "Free", "Lunch", "Linux Lab", "Problem Solving"]
            }
        }

# Save timetable to file
def save_timetable(timetable):
    with open(TIMETABLE_FILE, "w") as file:
        json.dump(timetable, file)

# Initialize timetable
timetable = load_timetable()

class TimetableApp(App):
    def build(self):
        # Main layout
        main_layout = BoxLayout(orientation='vertical')

        # Batch selection spinner
        self.batch_spinner = Spinner(text='Select Batch', values=list(timetable.keys()))
        main_layout.add_widget(self.batch_spinner)

        # Day selection spinner
        self.day_spinner = Spinner(text='Select Day', values=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
        main_layout.add_widget(self.day_spinner)

        # Slot input
        self.slot_input = TextInput(hint_text='Time Slot (0-5)', multiline=False)
        main_layout.add_widget(self.slot_input)

        # Subject input
        self.subject_input = TextInput(hint_text='Subject', multiline=False)
        main_layout.add_widget(self.subject_input)

        # Buttons for actions
        self.add_button = Button(text="Add Lecture")
        self.add_button.bind(on_press=self.add_extra_class)
        main_layout.add_widget(self.add_button)

        self.delete_button = Button(text="Delete Lecture")
        self.delete_button.bind(on_press=self.delete_extra_class)
        main_layout.add_widget(self.delete_button)

        self.show_button = Button(text="Show Free Slots")
        self.show_button.bind(on_press=self.show_free_slots)
        main_layout.add_widget(self.show_button)

        self.export_button = Button(text="Export Timetable")
        self.export_button.bind(on_press=self.export_timetable)
        main_layout.add_widget(self.export_button)

        self.auto_generate_button = Button(text="Auto Generate Timetable")
        self.auto_generate_button.bind(on_press=self.automatic_generation)
        main_layout.add_widget(self.auto_generate_button)

        # Display timetable in a scrollable view
        self.timetable_display = TextInput(readonly=True, size_hint_y=None, height=400)
        scroll_view = ScrollView(size_hint=(1, None), size=(500, 200))
        scroll_view.add_widget(self.timetable_display)
        main_layout.add_widget(scroll_view)

        # Show initial timetable
        self.show_timetable()

        return main_layout

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()

    def add_extra_class(self, instance):
        try:
            batch = self.batch_spinner.text
            day = self.day_spinner.text
            time_slot = int(self.slot_input.text)
            subject = self.subject_input.text

            if timetable[batch][day][time_slot] == "Free":
                timetable[batch][day][time_slot] = subject
                self.show_popup("Success", f"Added {subject} to {batch} on {day} at slot {time_slot} ({slot_timings[time_slot]})")
                self.show_timetable()
                save_timetable(timetable)
            else:
                self.show_popup("Error", "This slot is not free.")
        except:
            self.show_popup("Error", "Invalid input!")

    def delete_extra_class(self, instance):
        try:
            batch = self.batch_spinner.text
            day = self.day_spinner.text
            time_slot = int(self.slot_input.text)

            if timetable[batch][day][time_slot] not in ["Lunch", "Free"]:
                timetable[batch][day][time_slot] = "Free"
                self.show_popup("Success", f"Removed class from {batch} on {day} at slot {time_slot}")
                self.show_timetable()
                save_timetable(timetable)
            else:
                self.show_popup("Error", "Cannot delete lunch or a free slot.")
        except:
            self.show_popup("Error", "Invalid input!")

    def show_free_slots(self, instance):
        batch = self.batch_spinner.text
        day = self.day_spinner.text
        free_slots = [i for i, slot in enumerate(timetable[batch][day]) if slot == "Free"]
        self.show_popup("Free Slots", f"Free slots: {', '.join(str(slot) for slot in free_slots)}")

    def show_timetable(self):
        timetable_text = ""
        for batch, days in timetable.items():
            timetable_text += f"{batch}:\n"
            for day, classes in days.items():
                timetable_text += f"  {day}:\n"
                for i, subject in enumerate(classes):
                    timetable_text += f"    Slot {i} ({slot_timings[i]}): {subject}\n"
        self.timetable_display.text = timetable_text

    def export_timetable(self, instance):
        # Export timetable to a file
        try:
            with open("timetable.txt", "w") as f:
                for batch, days in timetable.items():
                    f.write(f"{batch}:\n")
                    for day, classes in days.items():
                        f.write(f"  {day}:\n")
                        for i, subject in enumerate(classes):
                            f.write(f"    Slot {i} ({slot_timings[i]}): {subject}\n")
            self.show_popup("Success", "Timetable exported successfully!")
        except Exception as e:
            self.show_popup("Error", f"Failed to export: {str(e)}")

    def automatic_generation(self, instance):
        try:
            auto_batch = "Auto Batch"
            timetable[auto_batch] = {day: [secrets.choice(subs), secrets.choice(subs), secrets.choice(subs), "Lunch", secrets.choice(subs), secrets.choice(subs)] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
            self.batch_spinner.values = list(timetable.keys())
            self.show_popup("Success", "Timetable auto-generated!")
            self.show_timetable()
            save_timetable(timetable)
        except Exception as e:
            self.show_popup("Error", str(e))

# Run the application
if __name__ == "__main__":
    TimetableApp().run()
