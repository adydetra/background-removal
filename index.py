import cv2
import time
import numpy as np
import sys
import threading

class LoadingSpinner:
    """Class to display an animated loading spinner."""
    def __init__(self, message="Loading"):
        self.spinner_chars = ['|', '/', '-', '\\']
        self.message = message
        self.is_spinning = False
        self.thread = None
        self.idx = 0
    
    def spin(self):
        """Animation loop for the spinner."""
        while self.is_spinning:
            sys.stdout.write(f'\r{self.message}... {self.spinner_chars[self.idx % len(self.spinner_chars)]}')
            sys.stdout.flush()
            self.idx += 1
            time.sleep(0.1)
    
    def start(self):
        """Start the spinner animation."""
        self.is_spinning = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
    
    def stop(self, final_message="Done!"):
        """Stop the spinner and display final message."""
        self.is_spinning = False
        if self.thread:
            self.thread.join()
        sys.stdout.write(f'\r{self.message}... {final_message}\n')
        sys.stdout.flush()

def resize_to_match(dst, target_img):
    """Resize dst to match target_img dimensions."""
    if dst is None or target_img is None:
        return None
    height, width = target_img.shape[:2]
    return cv2.resize(dst, (width, height), interpolation=cv2.INTER_AREA)

def create_foreground_mask(current_frame, reference_frame, threshold=13.0, gray_threshold=10):
    """Create a binary mask separating foreground from background."""
    diff1 = cv2.subtract(current_frame, reference_frame)
    diff2 = cv2.subtract(reference_frame, current_frame)
    diff = diff1 + diff2
    diff[abs(diff) < threshold] = 0
    
    gray = cv2.cvtColor(diff.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    gray[np.abs(gray) < gray_threshold] = 0
    
    fgmask = gray.astype(np.uint8)
    fgmask[fgmask > 0] = 255
    return fgmask

def scan_available_cameras(max_cameras=5):
    """Scan for available camera indices."""
    available_cameras = []
    print("\nScanning for available cameras...")
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                # Determine if camera is usable
                status_emoji = "✅" if fps > 0 else "❌"
                status_text = "" if fps > 0 else " (Unavailable)"
                
                available_cameras.append({
                    'index': i,
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'usable': fps > 0
                })
                print(f"  {status_emoji} Camera {i}: {width}x{height} @ {fps:.2f}fps{status_text}")
        cap.release()
    
    if not available_cameras:
        print("No cameras found!")
    
    return available_cameras

def select_camera(available_cameras):
    """Prompt the user to pick a camera or go back."""
    if not available_cameras:
        return None, False

    print("\nSelect Camera:")
    print("  0. Back")
    for idx, cam in enumerate(available_cameras, start=1):
        status_emoji = "✅" if cam['usable'] else "❌"
        status_text = "" if cam['usable'] else " (Unavailable)"
        print(f"  {idx}. {status_emoji} Camera {cam['index']} ({cam['width']}x{cam['height']} @ {cam['fps']:.2f}fps){status_text}")

    max_choice = len(available_cameras)
    while True:
        choice = input(f"Enter choice (0-{max_choice}): ").strip()
        try:
            choice_int = int(choice)
        except ValueError:
            print("Invalid input. Try again.")
            continue

        if choice_int == 0:
            return None, True
        if 1 <= choice_int <= max_choice:
            selected_cam = available_cameras[choice_int - 1]
            # Warn user if selecting unavailable camera
            if not selected_cam['usable']:
                confirm = input("⚠️  This camera may not work properly. Continue anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Please select another camera.")
                    continue
            return selected_cam['index'], False

        print("Invalid camera selection. Try again.")

def select_resolution():
    """Prompt the user to select a resolution."""
    while True:
        print("\n" + "="*50)
        print("Background Removal - Configuration")
        print("="*50)
        print("\nSelect Resolution:")
        print("  1. 640x480 (VGA)")
        print("  2. 1280x720 (HD)")
        print("  3. 1920x1080 (Full HD)")
        print("  4. Custom")

        choice = input("Enter choice (1-4): ").strip()
        if choice == '1':
            return 640, 480
        if choice == '2':
            return 1280, 720
        if choice == '3':
            return 1920, 1080
        if choice == '4':
            try:
                width = int(input("Enter width: ").strip())
                height = int(input("Enter height: ").strip())
            except ValueError:
                print("Invalid input. Try again.")
                continue

            if width > 0 and height > 0:
                return width, height

            print("Invalid dimensions. Try again.")
            continue

        print("Invalid choice. Try again.")

def select_fps():
    """Prompt the user to select FPS, allowing back navigation."""
    while True:
        print("\nSelect FPS:")
        print("  0. Back")
        print("  1. 30 fps")
        print("  2. 60 fps")
        print("  3. Custom")

        choice = input("Enter choice (0-3): ").strip()
        if choice == '0':
            return None
        if choice == '1':
            return 30
        if choice == '2':
            return 60
        if choice == '3':
            try:
                fps = int(input("Enter FPS: ").strip())
            except ValueError:
                print("Invalid input. Try again.")
                continue

            if fps > 0:
                return fps
            print("Invalid FPS. Try again.")
            continue

        print("Invalid choice. Try again.")

def main():
    video = None

    while video is None:
        desired_width, desired_height = select_resolution()

        while True:
            desired_fps = select_fps()
            if desired_fps is None:
                print("\nReturning to resolution selection...\n")
                break

            while True:
                available_cameras = scan_available_cameras()

                if not available_cameras:
                    print("\nError: No cameras found. Exiting.")
                    return

                camera_index, go_back = select_camera(available_cameras)
                if go_back:
                    print("\nReturning to FPS selection...\n")
                    break

                print(f"\nInitializing camera {camera_index}...")
                
                # [1/4] Opening camera device with spinner
                spinner = LoadingSpinner("  [1/4] Opening camera device")
                spinner.start()
                video = cv2.VideoCapture(camera_index)
                time.sleep(0.5)  # Simulate loading time
                
                if not video.isOpened():
                    spinner.stop("Failed!")
                    print("Error: Cannot open selected camera. Choose another camera.")
                    video.release()
                    video = None
                    continue
                spinner.stop("Done!")

                # [2/4] Configuring resolution with spinner
                spinner = LoadingSpinner("  [2/4] Configuring resolution")
                spinner.start()
                video.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
                video.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)
                time.sleep(0.3)
                spinner.stop("Done!")
                
                # [3/4] Configuring frame rate with spinner
                spinner = LoadingSpinner("  [3/4] Configuring frame rate")
                spinner.start()
                video.set(cv2.CAP_PROP_FPS, desired_fps)
                time.sleep(0.3)
                spinner.stop("Done!")

                # [4/4] Verifying camera settings with spinner
                spinner = LoadingSpinner("  [4/4] Verifying camera settings")
                spinner.start()
                actual_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                actual_fps = video.get(cv2.CAP_PROP_FPS)
                time.sleep(0.3)
                spinner.stop("Done!")
                
                print(f"\nCamera active at {actual_width}x{actual_height} @ {actual_fps:.2f}fps")
                break

            if video is not None:
                break

        if video is not None:
            break

    print("\nLoading background video...")
    spinner = LoadingSpinner("  Loading video.mp4")
    spinner.start()
    background_video = cv2.VideoCapture("video.mp4")
    time.sleep(0.5)
    
    if not background_video.isOpened():
        spinner.stop("Failed!")
        print("Error: Cannot open video.mp4")
        video.release()
        return
    spinner.stop("Done!")
    print("Background video loaded successfully!")
    
    print("\nPreparing background removal...")
    spinner = LoadingSpinner("  Reading initial frame")
    spinner.start()
    success, ref_img = video.read()
    time.sleep(0.3)
    
    if not success or ref_img is None:
        spinner.stop("Failed!")
        print("Error: Cannot read from camera")
        video.release()
        background_video.release()
        return
    spinner.stop("Done!")
    
    print(f"  Frame size: {ref_img.shape[1]}x{ref_img.shape[0]}")
    print("\n" + "="*50)
    print("Background auto-captured. Stay still for 2 seconds...")
    print("="*50)
    
    # Auto-capture background after a short delay
    time.sleep(2)
    success, ref_img = video.read()
    if not success or ref_img is None:
        print("Error: Cannot capture background frame")
        video.release()
        background_video.release()
        return
    
    print("Background captured! You can move now.")
    print("Press 'r' to recapture background, 'q' or ESC to quit")
    
    capture_background = True

    while True:
        # Read frames from both sources
        success, img = video.read()
        success2, bg = background_video.read()
        
        # Validate webcam frame
        if not success or img is None:
            print("Warning: Cannot read from camera")
            break
        
        # Loop background video if it ends
        if not success2 or bg is None:
            background_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success2, bg = background_video.read()
            if not success2 or bg is None:
                print("Error: Cannot read background video")
                break
        
        # Resize background to match webcam frame
        bg = resize_to_match(bg, img)
        if bg is None:
            continue
        
        # Create foreground mask
        fgmask = create_foreground_mask(img, ref_img)
        fgmask_inv = cv2.bitwise_not(fgmask)
        
        # Extract foreground and background using masks
        fgimg = cv2.bitwise_and(img, img, mask=fgmask)
        bgimg = cv2.bitwise_and(bg, bg, mask=fgmask_inv)
        
        # Combine foreground and background
        result = cv2.add(bgimg, fgimg)
        
        # Display result
        cv2.imshow('Background Removal', result)
        
        # Handle keyboard input
        key = cv2.waitKey(30) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            break
        elif key == ord('r'):  # Recapture background
            print("Recapturing background... Stay still for 2 seconds...")
            time.sleep(2)
            success_temp, ref_img = video.read()
            if success_temp and ref_img is not None:
                print("Background recaptured! You can move now.")
            else:
                print("Warning: Failed to recapture background")
    
    # Cleanup
    cv2.destroyAllWindows()
    video.release()
    background_video.release()

if __name__ == "__main__":
    main()