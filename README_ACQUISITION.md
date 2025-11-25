# Automated Camera Acquisition

This system allows you to schedule automatic screenshots of the monitoring cameras.

## Option 1: Cloud Automation (Recommended)

This project is configured with **GitHub Actions** to run the acquisition automatically without needing your computer to be on.

1.  **Push your changes** to GitHub.
2.  Ensure **GitHub Actions** are enabled in your repository settings.
3.  The system will check every 30 minutes for upcoming acquisitions listed in `acquisitions.json`.
4.  When a scheduled time arrives, it will take the screenshot and **commit it back to the repository** in the `captures/` folder.

To add a new acquisition:
1.  Edit `acquisitions.json` locally or on GitHub.
2.  Commit and push.
3.  Wait for the scheduled time.

## Option 2: Local Execution

If you prefer to run it on your own computer:

1.  **Install Python**:
    Download and install it from [python.org](https://www.python.org/downloads/).
    *Make sure to check "Add Python to PATH" during installation.*

2.  **Install Dependencies**:
    Open a terminal (Command Prompt or PowerShell) in this folder and run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Script**:
    ```bash
    python capture.py
    ```
    The script will wait until the specified times and save screenshots in the `captures/` folder.
    **Note:** Your computer must be ON and the script running at the scheduled time.

## Configuration

Edit `acquisitions.json` to add the times you want to capture.
Format:
```json
[
    {
        "timestamp": "2025-11-26 00:17:46",
        "camera": "Camera 1",
        "url": "https://www.youtube-nocookie.com/embed/YSlMTkpyEbw?autoplay=1&mute=1&rel=0&controls=0&modestbranding=1"
    }
]
```

## Notes

- The script uses the "embed" URL for YouTube to get a full-window video view.
- It runs in "headless" mode (no visible browser window).

