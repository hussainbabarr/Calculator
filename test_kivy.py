from kivy.app import App
from kivy.uix.label import Label


class KivyTestApp(App):
    def build(self):
        return Label(text="Kivy Working")


if __name__ == "__main__":
    KivyTestApp().run()
