# NVIDIA Hackathon
This project seeks to...
# File Structure:
- `src`: Source code
  - `YOLO`: You only look once model for object tracking
    - `imgs`: images to process or saved images are all stored here
    - `models`: YOLO models (.pth files)
    - `output_data`: Generated output data
    - `get_data.py`: Function for parsing data from YOLO results to readable txt file
    - `yolo_publisher.py`: None. May delete.
    - `yolo_subscriber.py`: Subscriber node to run YOLO tracking (runs yolo_world_ROS.py)
    - `yolo_world.py`: Main script for general inference, data collection, and visualization
    - `yolo_world_ROS.py`: Main script for ROS implementation for inference and data collection
  - `Other sub folder`:
  - `Other sub folder`:
  - `Other sub folder`:
- `environment.yaml`: environment for running the code. Not sure if we need this.
