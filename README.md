<div align="center">
  <h1><b>🤖 Ai Image Enhancer: AI-Powered Image Enhancement</b></h1>

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.10-orange?logo=tensorflow)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-blue?logo=opencv)
![Pillow](https://img.shields.io/badge/Pillow-9.0+-yellow)
</div>

## Project Overview

ImageEnhancerAI is a web application that leverages a deep learning model to enhance low-quality or blurred images into sharp, high-quality versions. Built with Flask and TensorFlow, it provides a user-friendly interface for uploading images, applying AI-based or traditional enhancements, and downloading the results. The system supports user authentication, profile management, and customizable enhancement settings.
### Demo

https://drive.google.com/file/d/1Ux8zAeNe-au3RlkmcwPuwgek_BGXeD6U/view?usp=drive_link

## Features

- **AI-Powered Image Enhancement**: Utilizes a U-Net-based deep learning model trained on paired blurred/sharp datasets.
- **Fallback Enhancement**: Applies traditional image processing (OpenCV-based denoising and sharpening) when the AI model is unavailable.
- **User Authentication**: Secure user registration and login with session management.
- **Profile Management**: Allows users to update profile pictures and contact information.
- **Customizable Output**: Supports user-defined output sizes and aspect ratio preservation.
- **Responsive Web Interface**: Clean, intuitive design for seamless interaction across devices.

## Technology Stack

### Backend

- **Framework**: Flask
- **Deep Learning**: TensorFlow (U-Net model for image enhancement)
- **Image Processing**: OpenCV, Pillow (PIL)
- **Database**: SQLite
- **Authentication**: Flask-Login, Werkzeug
- **Data Processing**: NumPy

### Frontend

- HTML5, CSS3, JavaScript
- Responsive design for desktop and mobile

## Installation

### Prerequisites

- Python 3.8+
- pip
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/99Ahmadprojects/Ai-Image-Enhancer.git
   cd Ai-Image-Enhancer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the model is placed in the correct directory:

    - Place the trained model (ecom_enhancer.keras) in models/ or provide config.json and model.weights.h5 in models/ecom_enhancer/.
    - If training the model, use the provided Colab notebook and save the model as models/ecom_enhancer.keras.

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`


## Project Structure

```
Ai Image Enhancer/
├── instance/                 # SQLite database (app.db)
├── models/                   # Pretrained models
│   ├── ecom_enhancer.keras   # Single-file Keras model
│   └── ecom_enhancer/        # Directory for config.json and model.weights.h5
├── app.py                    # Flask application
├── templates/                # HTML templates
│   ├── dashboard.html        # Main user interface
│   ├── login.html            # Login page
│   └── register.html         # Registration page
├── static/                   # Static files
│   ├── images/               # Logo and default profile images
│   ├── uploads/              # User-uploaded images and processed outputs
│   └── styles.css            # CSS styles
├── requirements.txt          # Project dependencies
├── README.md                 # Project Documentation
```


## Methodology
### 1. Image Enhancement Pipeline

- AI Model: A U-Net-based deep learning model trained on paired blurred/sharp images to enhance low-quality inputs.
- Fallback Processing: Uses OpenCV for resizing, denoising, and sharpening when the AI model is unavailable or fails.
- Customization: Users can specify output dimensions and choose to preserve the aspect ratio.

### 2. User Authentication and Profile Management

- Authentication: Secure registration and login using Flask-Login and hashed passwords (Werkzeug).
- Profile Settings: Users can upload profile pictures and update contact information, stored in SQLite.


## Implementation Details
### Image Enhancement

- **Preprocessing:** Images are loaded, resized, and normalized for model input.
- **Model Inference:** The U-Net model processes images to produce enhanced outputs in [0,1] range.
- **Fallback Processing:** If the model fails, OpenCV applies bicubic resizing, bilateral filtering, and unsharp masking.
- **Output Handling:** Enhanced images are saved as JPEG (or PNG for transparency) and served via Flask’s static folder.

### Web Interface

- **Dashboard:** Allows image uploads, enhancement settings, and displays results with download links.
- **Responsive Design:** Ensures usability on various devices using CSS and JavaScript.

## Challenges Faced

1. **Model Output Range:**

    Handled varying model output ranges (e.g., [0,255], [-1,1]) by adding normalization in the inference pipeline.


2. **Performance:**

   - Optimized model loading to occur once at startup.
   - Used efficient image processing with OpenCV for fallback enhancement.


3. **File Management:**

    Ensured robust path handling for user uploads and database storage across platforms (Windows/Linux).


4. **User Experience:**

    Implemented clear feedback (flash messages) for enhancement success or failure.



## Results

- **Enhancement Quality:** High-quality outputs from the AI model, with fallback processing for reliability.
- **User Experience:** Intuitive interface with secure authentication and profile management.
- **Performance:** Fast image processing and responsive web interface.

## Team CODEX

- **AI Engineer:** Muhammad Talha Asghar (Team Lead)
- **Web Developer & AI Engineer:** Mir Ahmad Shah
