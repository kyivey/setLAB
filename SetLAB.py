import os
import signal
import subprocess
import sys
from PyQt5.QtWidgets import (
    QApplication, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, 
    QMessageBox, QHBoxLayout, QSizePolicy, QSpacerItem, QFileDialog
)
from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QMovie

base_path = os.path.dirname(os.path.abspath(__file__))
bash_script = os.path.join(base_path, "getSong.sh")

class DownloadApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up layout
        layout = QVBoxLayout()
        url_layout = QHBoxLayout()
        download_layout = QHBoxLayout()

        # URL input
        self.url_label = QLabel("Enter the URL:")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste the URL here...")

        # Folder selection button
        self.folder_button = QPushButton("Choose Folder")
        self.folder_button.clicked.connect(self.select_folder)
        
        # Label to show the selected folder
        self.output_directory = os.path.expanduser("~/Downloads")  # default
        self.folder_label = QLabel(self.output_directory)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.folder_button)
        url_layout.addWidget(self.folder_label)

        # Spinner animation
        self.spinner_label = QLabel()
        self.spinner_movie = QMovie(os.path.join(base_path, "spinner.gif"))  # Replace with your spinner GIF file
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.setFixedSize(50, 50)  # Adjust size to match your spinner
        self.spinner_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.spinner_label.setVisible(False)  # Initially hidden

        # url_layout.addWidget(self.spinner_label)
        url_layout.setSpacing(10)
        # url_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        layout.addLayout(url_layout)

        # Download button
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setFixedSize(200, 50)  # Adjust size to match your spinner
        self.download_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # Stop button (cancels a running/hung download)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.setFixedSize(100, 50)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("QPushButton:enabled { color: #c62828; font-weight: bold; }")
        self.stopped = False

        download_layout.addWidget(self.download_button)
        download_layout.addWidget(self.stop_button)
        download_layout.addWidget(self.spinner_label)
        download_layout.setContentsMargins(0, 0, 0, 0)
        download_layout.setSpacing(10)

        download_layout.setAlignment(self.download_button, Qt.AlignCenter)
        download_layout.setAlignment(self.spinner_label, Qt.AlignCenter)

        layout.addLayout(download_layout)
        layout.setAlignment(download_layout, Qt.AlignHCenter)


        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        # Set main layout
        self.setLayout(layout)
        self.setWindowTitle("SetLAB")
        self.resize(800, 300)

        # QProcess to run the Bash script
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.readyReadStandardError.connect(self.read_output)
        self.process.finished.connect(self.on_finished)
        self.process.errorOccurred.connect(self.on_error)

    def select_folder(self):
        # Open the folder dialog
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder",
                                                  self.output_directory)

        if folder:
            # If a folder is selected, update the label with the folder path
            self.folder_label.setText(folder)
            self.output_directory = folder  # Store the selected directory

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid URL.")
            return

        # Clear previous log
        self.log_output.clear()

        # Start the spinner animation
        self.spinner_label.setVisible(True)
        self.spinner_movie.start()

        # Start the process
        self.stopped = False
        self.download_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Run through bash so the script's executable bit doesn't matter
        self.process.start("/bin/bash", [bash_script, url, self.output_directory])

    def read_output(self):
        # Read the output from the script
        output = self.process.readAllStandardOutput().data().decode()
        error_output = self.process.readAllStandardError().data().decode()

        # Append output to the log
        if output:
            self.log_output.append(output.strip())
        if error_output:
            
            self.log_output.append(f"Error: {error_output.strip()}")


    def _descendants(self, pid):
        """All child/grandchild PIDs of pid (bash -> python yt-dlp -> deno/ffmpeg)."""
        try:
            out = subprocess.run(["pgrep", "-P", str(pid)],
                                 capture_output=True, text=True).stdout
        except OSError:
            return []
        kids = [int(p) for p in out.split()]
        result = []
        for k in kids:
            result += self._descendants(k) + [k]
        return result

    def _kill_process_tree(self):
        pid = int(self.process.processId())
        if pid <= 0:
            return
        for p in self._descendants(pid):
            try:
                os.kill(p, signal.SIGKILL)
            except ProcessLookupError:
                pass
        self.process.kill()

    def stop_download(self):
        if self.process.state() == QProcess.NotRunning:
            return
        self.stopped = True
        self.log_output.append("Stopping download...")
        self._kill_process_tree()

    def closeEvent(self, event):
        # Don't leave yt-dlp running in the background when the window closes
        if self.process.state() != QProcess.NotRunning:
            self.stopped = True
            self._kill_process_tree()
            self.process.waitForFinished(2000)
        event.accept()

    def _reset_buttons(self):
        self.download_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def on_error(self, error):
        # Only FailedToStart skips the finished signal; handle it here
        if error == QProcess.FailedToStart:
            self._reset_buttons()
            self.spinner_movie.stop()
            self.spinner_label.setVisible(False)
            self.log_output.append(f"Error: could not start {bash_script}: "
                                   f"{self.process.errorString()}")
            QMessageBox.warning(self, "Download failed",
                                "Could not start the download script. See the log for details.")

    def on_finished(self, exit_code, exit_status):
        # Stop the spinner animation
        self.spinner_movie.stop()
        self.spinner_label.setVisible(False)
        self._reset_buttons()

        if self.stopped:
            self.log_output.append("Download stopped.")
            return

        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.log_output.append("Download completed.")
            self.url_input.clear()
            QMessageBox.information(self, "Done", "The download has completed successfully!")
        else:
            self.log_output.append(f"Download failed (exit code {exit_code}).")
            QMessageBox.warning(self, "Download failed",
                                "The download failed. See the log for details.")


# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloadApp()
    window.show()
    sys.exit(app.exec_())
