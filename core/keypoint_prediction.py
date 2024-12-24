import cv2
import numpy as np
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

def load_model(model_path):
    """
    Load the YOLO model from the specified path.
    
    Args:
        model_path (str): Path to the model weights file
        
    Returns:
        YOLO: Loaded model object
        
    Raises:
        RuntimeError: If model loading fails
    """
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        logger.error(f"Failed to load model from {model_path}: {e}")
        raise RuntimeError(f"Model loading failed: {e}")

def predict_keypoints(model, image_path):
    """
    Predict keypoints on the given image using the loaded model.
    
    Args:
        model: Loaded YOLO model
        image_path (str): Path to the input image
        
    Returns:
        tuple: (keypoints, bbox, bbox_n) - Lists containing keypoints and bounding box coordinates
        
    Raises:
        ValueError: If image cannot be read or no predictions are made
        RuntimeError: For other prediction failures
    """
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from path: {image_path}")
        
        # Make prediction
        results = model(image)
        if not results or len(results) == 0:
            raise ValueError("Model returned no results")
        
        # Extract keypoints and bounding boxes
        if not hasattr(results[0], 'keypoints') or len(results[0].keypoints.xy) == 0:
            raise ValueError("No keypoints detected in the image")
        
        keypoints = results[0].keypoints.xy.tolist()
        
        # Extract bounding boxes if available
        bbox = []
        bbox_n = []
        if len(results[0].boxes) > 0:
            bbox = results[0].boxes.xyxy.tolist()[0]
            bbox_n = results[0].boxes.xywhn.tolist()[0]
        
        return keypoints, bbox, bbox_n
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise RuntimeError(f"Prediction failed: {e}")

def correct_keypoints(full_keypoints, image):
    """
    Apply corrections and adjustments to the predicted keypoints.
    
    Args:
        full_keypoints (list): List of predicted keypoint coordinates
        image (numpy.ndarray): Input image
        
    Returns:
        list: Corrected keypoint coordinates
        
    Raises:
        ValueError: If keypoints are invalid
        RuntimeError: For other correction failures
    """
    try:
        if not full_keypoints or len(full_keypoints) < 26:
            logger.error(f"Invalid keypoints: received {len(full_keypoints) if full_keypoints else 0} keypoints")
            raise ValueError("Invalid number of keypoints")
        
        # Create a copy to avoid modifying the original
        corrected = [point.copy() for point in full_keypoints]
        
        # Helper function for calculating midpoints
        def safe_midpoint(p1_idx, p2_idx):
            if 0 <= p1_idx < len(corrected) and 0 <= p2_idx < len(corrected):
                return [
                    (corrected[p1_idx][0] + corrected[p2_idx][0]) / 2,
                    (corrected[p1_idx][1] + corrected[p2_idx][1]) / 2
                ]
            raise ValueError(f"Invalid indices for midpoint calculation: {p1_idx}, {p2_idx}")
        
        # Helper function for adding offsets
        def safe_offset(idx, x_offset=0, y_offset=0):
            if 0 <= idx < len(corrected):
                return [
                    corrected[idx][0] + x_offset,
                    corrected[idx][1] + y_offset
                ]
            raise ValueError(f"Invalid index for offset calculation: {idx}")
        
        # Apply corrections
        # Neck point (21) - midpoint between shoulders
        corrected[21] = safe_midpoint(5, 6)
        
        # Upper spine points (19, 20)
        corrected[20] = corrected[19].copy()
        corrected[19] = safe_midpoint(20, 21)
        
        # Extended points
        corrected[22] = safe_offset(9, 0, 10)   # Left ankle extension
        corrected[23] = safe_offset(10, 0, 10)  # Right ankle extension
        corrected[24] = safe_offset(15, 10, 5)  # Left wrist extension
        corrected[25] = safe_offset(16, 10, 5)  # Right wrist extension
        
        # Adjust to image bounds
        corrected = adjust_keypoints(corrected, image)
        
        return corrected
        
    except Exception as e:
        logger.error(f"Keypoint correction failed: {e}")
        raise RuntimeError(f"Keypoint correction failed: {e}")

def adjust_keypoints(keypoints, image, margin=5):
    """
    Adjust keypoints to ensure they fall within image boundaries.
    
    Args:
        keypoints (list): List of keypoint coordinates
        image (numpy.ndarray): Input image
        margin (int): Minimum distance from image edges
        
    Returns:
        list: Adjusted keypoint coordinates
        
    Raises:
        RuntimeError: If adjustment fails
    """
    try:
        height, width = image.shape[:2]
        adjusted = []
        
        for x, y in keypoints:
            # Ensure coordinates are within image bounds
            adj_x = max(margin, min(width - margin, x))
            adj_y = max(margin, min(height - margin, y))
            adjusted.append([adj_x, adj_y])
        
        return adjusted
        
    except Exception as e:
        logger.error(f"Keypoint adjustment failed: {e}")
        raise RuntimeError(f"Keypoint adjustment failed: {e}")