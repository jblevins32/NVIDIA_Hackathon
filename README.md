# NVIDIA Hackathon
This project seeks to...
# File Structure:
- `src`: Source code
  - `YOLO`: You only look once model for object tracking
    - `imgs`: images to process
    - `models`: YOLO models (.pth files)
    - `output_data`: Generated output data
    - `get_data.py`: Function for parsing data from YOLO results to readable txt file
    - `yolo_world.py`: Main script for inference, data collection, and visualization
