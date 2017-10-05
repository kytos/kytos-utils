"""Translate cli commands to non-cli code."""
import subprocess


class ControllerAPI:
    """Handle KytosController comamnds."""

    @staticmethod
    def start():
        """Start KytosController."""
        subprocess.run(["kytosd"])

    @staticmethod
    def status():
        """Display KytosController status."""
        subprocess.run(["kytosd", 'status'])

    @staticmethod
    def stop():
        """Start KytosController."""
        subprocess.run(["kytosd", 'stop'])
