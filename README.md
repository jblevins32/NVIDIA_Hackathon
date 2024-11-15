# NVIDIA Hackathon - Context-Aware 3D Referring Expression Resolution using a Robotic LLM Agent
This project investigates robot task completion using 3D referring expressions. Inspired by [**Transcrib3D**](https://ripl.github.io/Transcrib3D/), the project substitutes pre-taken 3D LiDAR of a room for <u>robotic exploration in an unknown environment</u>.

## Features
- **Object Detection:** Utilizes YOLO with open-vocabulary capabilities for object identification.
- **2D LiDAR Localization:** Maps YOLO-detected object positions in the robot's environment.
- **LLM Integration:** Processes textual descriptions of scenes using LLama for reasoning and decision-making, eliminating the need for multi-modal architectures or sensor fusion.
- **Complex Query Resolution:** Solves advanced referring expressions query for context-aware scene understanding.

## How It Works
1. **Exploration:** The robot navigates the scene, collecting data on detected objects and their positions.
2. **Data Storage:** Scene data (objects and global positions) and relevant features are logged in a structured text format for processing.
3. **Reasoning Agent:** Large language model filters the scene data for objects relevant to the query and solves the referring expression.

## Technologies Used
**YOLO:** For real-time object detection.
**2D LiDAR:** For precise localization of detected objects.
**LLM:** Llama3.2 as the reasoning agent (**LangChain**) for complex text-based problem solving.
**ROS2:** For robotic system integration and control.
**Python:** For scripting and pipeline development.

# File Structure:
- `src`: Source code
  - `YOLO`: You only look once model for object tracking
    - `imgs`: images to process
    - `models`: YOLO models (.pth files)
    - `output_data`: Generated output data
    - `get_data.py`: Function for parsing data from YOLO results to readable txt file
    - `yolo_world.py`: Main script for inference, data collection, and visualization
  - `Other sub folder`:
  - `Other sub folder`:
  - `Other sub folder`:
