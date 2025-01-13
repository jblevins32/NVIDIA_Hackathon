from ultralytics import YOLO
import torch
from get_data import GetData
import numpy as np

class yolo():
    '''
    This class:
    1) Instaniates YOLO model
    2) Runs the images over the model
    3) Outputs data
    4) Outputs images with bboxes (commented out right now)
    '''
    
    def __init__(self): 
        '''
        Initialize variables and model
        '''
        
        # Initialize list and object for gathering bbox data
        self.ID_list = torch.tensor([])
        self.data_obj = GetData()
        
        # Load the YOLOv8 model
        self.model = YOLO('src/YOLO/models/yolov8s-worldv2.pt')

    def YOLOrun(self, img):
        '''
        Run the yolo model on the incoming image and get the data    
        '''
        # Run the model on a list JPG images. Live feed will replace this list and loop
        results = self.model.track(img)
        self.ID_list = self.data_obj.AddGetData(results = results, ID_list= self.ID_list)

        # Save results
        np.savetxt('src/YOLO/output_data/bbox_data.txt', self.ID_list, fmt='%f')
