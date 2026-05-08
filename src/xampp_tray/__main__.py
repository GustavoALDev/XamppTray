import sys


def main() -> None:
    from xampp_tray.app import TrayApp

    try:
        TrayApp().run()
    except KeyboardInterrupt:
        print("\nEncerrando o XAMPP Tray App.")
        sys.exit(0)


if __name__ == "__main__":
    main()
