import json
import time
import os
import argparse
import sys
from datetime import datetime
import dateparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configuration
ACQUISITIONS_FILE = 'acquisitions.json'
OUTPUT_DIR = 'captures'

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # Initialize the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def load_acquisitions():
    with open(ACQUISITIONS_FILE, 'r') as f:
        data = json.load(f)
    
    # Parse timestamps and sort
    tasks = []
    for item in data:
        dt = dateparser.parse(item['timestamp'])
        if dt:
            tasks.append({
                'time': dt,
                'url': item['url'],
                'camera': item.get('camera', 'Unknown')
            })
    
    # Sort by time
    tasks.sort(key=lambda x: x['time'])
    return tasks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ci', action='store_true', help='Run in CI mode (exit after checking/running tasks)')
    parser.add_argument('--window', type=int, default=60, help='Lookahead window in minutes for CI mode')
    args = parser.parse_args()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Loaded acquisitions from {ACQUISITIONS_FILE}")
    
    while True:
        tasks = load_acquisitions()
        now = datetime.now()
        
        # Filter for future tasks
        if args.ci:
            # In CI mode, look for tasks in the near future OR recently missed (last 10 mins)
            # Window: [now - 10m, now + args.window]
            window_start = now.timestamp() - 600
            window_end = now.timestamp() + (args.window * 60)
            
            active_tasks = []
            for t in tasks:
                ts = t['time'].timestamp()
                if window_start <= ts <= window_end:
                    active_tasks.append(t)
            
            if not active_tasks:
                print(f"No tasks found in the next {args.window} minutes (or recent past). Exiting CI.")
                sys.exit(0)
                
            future_tasks = active_tasks # Process these
        else:
            future_tasks = [t for t in tasks if t['time'] > now]
        
        if not future_tasks:
            print("No future acquisitions scheduled. Waiting 60 seconds for new tasks...")
            time.sleep(60)
            continue
            
        next_task = future_tasks[0]
        wait_seconds = (next_task['time'] - now).total_seconds()
        
        print(f"Next acquisition: {next_task['camera']} at {next_task['time']}")
        
        # If the wait is long, sleep in short bursts to allow for updates or cancellation
        # But in CI mode, we just wait.
        if not args.ci and wait_seconds > 60:
            print(f"Waiting... ({wait_seconds:.0f}s remaining)")
            time.sleep(60)
            continue
        
        print(f"Waiting for {wait_seconds:.1f} seconds...")
        if wait_seconds > 0:
            time.sleep(wait_seconds)
            
        # Double check time (in case we woke up slightly early)
        # But for simplicity, we proceed.
        
        print(f"Acquiring {next_task['camera']}...")
        try:
            driver = setup_driver()
            driver.get(next_task['url'])
            
            # Wait a bit for the video to load/buffer
            time.sleep(10) 
            
            filename = f"{OUTPUT_DIR}/{next_task['camera'].replace(' ', '_')}_{next_task['time'].strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(filename)
            print(f"Saved screenshot to {filename}")
            
            driver.quit()
        except Exception as e:
            print(f"Error acquiring {next_task['camera']}: {e}")
            
        if args.ci:
            # In CI, after processing the immediate task, we check if there are more in the window
            # For simplicity, let's just loop. The next iteration will pick up the next task or exit.
            pass

if __name__ == "__main__":
    main()
