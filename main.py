from desktop_app.application import QuickNoteApp
from desktop_app.database import initialize_database


def main() -> None:
    initialize_database()
    app = QuickNoteApp()
    app.mainloop()


if __name__ == "__main__":
    main()
