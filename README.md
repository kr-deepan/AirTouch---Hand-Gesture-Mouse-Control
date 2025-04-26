# ✨ AirTouch - Hand Gesture Mouse Control

**AirTouch** lets you control your computer’s mouse using natural hand gestures detected via your webcam. It's built using **MediaPipe**, **OpenCV**, and **PyAutoGUI** to deliver smooth, real-time motion tracking with intuitive controls.

---

## 📹 Demo

https://user-images.githubusercontent.com/your-demo-link-here.gif  
*(Add a screen recording or GIF showing the usage of AirTouch)*

---

## 🚀 Features

- Move your mouse cursor by waving your **index finger**
- **Left Click** by pinching **thumb + middle finger**
- **Right Click** with a **thumb + ring finger pinch**
- **Click & Drag** with a long **thumb + middle finger pinch**
- Smoothing using Exponential Moving Average (EMA)
- Adaptive dead zone for natural control
- Threaded frame capture for better performance

---

## 🛠️ Requirements

- Python 3.7 or higher
- A webcam (built-in or USB)

### Install Dependencies

```bash
pip install opencv-python mediapipe pyautogui numpy

