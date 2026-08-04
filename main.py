"""
EXE Sandbox
==========================================

A Windows-native EXE sandbox with a hyper-styled cyberpunk/terminal GUI.
Launch executables in a monitored environment and watch everything they do
in real-time.
"""
import sys
import os

# Add the parent directory to the path so we can import our modules
# This is necessary when running the script directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """
    Main entry point for the EXE Sandbox application.
    This initializes the Qt application and shows the main window.
    """
    # Import Qt modules inside the function to ensure proper initialization
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont

    # Enable high DPI scaling for modern displays
    # This ensures the UI looks crisp on 4K and Retina screens
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create the Qt application
    # This is the foundation of our GUI - everything else is built on top of it
    app = QApplication(sys.argv)

    # Set the application font to a monospace font for the terminal aesthetic
    # We prefer Cascadia Code or Fira Code for the best look
    font = QFont("Cascadia Code", 10)
    font.setStyleHint(QFont.Monospace)
    app.setFont(font)

    # Set the application name and version
    app.setApplicationName("EXE Sandbox")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Cyberpunk Edition")

    # Import and create the main window
    # We do this after QApplication is created to avoid issues
    from gui.main_window import MainWindow

    # Create the main window
    window = MainWindow()

    # Show the main window
    window.show()

    # Print a startup message to the console
    print("=" * 60)
    print("  EXE SANDBOX - Cyberpunk Monitoring Edition")
    print("=" * 60)
    print("  Ready to sandbox EXEs.")
    print("  Drag and drop an .exe file to get started.")
    print("=" * 60)

    # Run the Qt event loop
    # This is the main loop that handles all GUI events
    # The application will exit when this returns
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
