import cv2
import sys
import os
from pathlib import Path
import logging
from video_camera import VideoCamera
from video_processor import VideoProcessor
sys.path.append(str(Path(__file__).parent.parent))
from detect import VehicleDetector
from datetime import datetime

def process_video(source, save_output=False):
    """
    Process video from given source (camera or file).
    
    Args:
        source: Camera index (int) or video file path (str)
        save_output: Whether to save the processed video
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize video processor and detector
    processor = VideoProcessor()
    detector = VehicleDetector()
    
    # Download YOLOv8 model if needed
    detector.download_model()
    
    # Add basic processors
    processor.add_processor(processor.add_timestamp)
    
    try:
        # Start video capture
        with VideoCamera(source=source) as camera:
            logger.info("Video source opened successfully")
            video_info = camera.get_video_info()
            logger.info(f"Video info: {video_info}")
            
            # Initialize video writer if saving output
            output_writer = None
            if save_output:
                output_dir = Path("output_videos")
                output_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir / f"processed_{timestamp}.mp4"
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                output_writer = cv2.VideoWriter(
                    str(output_path),
                    fourcc,
                    video_info['fps'],
                    (video_info['width'], video_info['height'])
                )
                logger.info(f"Saving output to: {output_path}")
            
            frame_count = 0
            while True:
                # Get frame from source
                success, frame, frame_count = camera.get_frame()
                
                if not success:
                    logger.info("End of video stream")
                    break
                
                # Add frame counter
                frame = processor.add_frame_counter(frame, frame_count)
                
                # Perform vehicle detection
                processed_frame, detections = detector.detect(frame)
                
                # Get and display vehicle counts
                counts = detector.get_vehicle_count(detections)
                if counts:
                    y_pos = 110
                    for vehicle_type, count in counts.items():
                        text = f"{vehicle_type}: {count}"
                        cv2.putText(processed_frame, text, (10, y_pos), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        y_pos += 40
                
                # Save output if requested
                if output_writer:
                    output_writer.write(processed_frame)
                
                # Display frame
                cv2.imshow('Traffic Monitoring', processed_frame)
                
                # Save frame periodically (every 30 frames)
                if frame_count % 30 == 0:
                    if isinstance(source, str):  # Only save frames for video files
                        saved_path = camera.save_frame(processed_frame)
                        logger.info(f"Saved frame to: {saved_path}")
                    if counts:
                        logger.info(f"Detected vehicles: {counts}")
                
                # Break loop on 'q' press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
    except Exception as e:
        logger.error(f"Error during video processing: {str(e)}")
        
    finally:
        # Cleanup
        cv2.destroyAllWindows()
        if output_writer:
            output_writer.release()

def main():
    while True:
        print("\nTraffic Detection System")
        print("1. Live Camera Stream")
        print("2. Process Video File")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            # Live camera stream
            print("\nStarting live camera stream...")
            print("Press 'q' to quit")
            process_video(0)
            
        elif choice == "2":
            # Video file processing
            video_path = input("\nEnter video path (or press Enter for default 'Test_Videos/v2.mp4'): ")
            if not video_path:
                video_path = "Test_Videos/v2.mp4"
            
            save_output = input("Save processed video? (y/n): ").lower() == 'y'
            
            if not os.path.exists(video_path):
                print(f"Error: Video file not found at {video_path}")
                continue
                
            print(f"\nProcessing video: {video_path}")
            print("Press 'q' to quit")
            process_video(video_path, save_output)
            
        elif choice == "3":
            print("\nExiting...")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main() 