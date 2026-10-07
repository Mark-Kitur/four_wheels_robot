import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

import cv2
import os
from ultralytics import YOLO
from ament_index_python.packages import get_package_share_directory

class ImageProcessingNode(Node):
    def __init__(self):
        super().__init__('image_processing_node')
        
        self.br = CvBridge()
        
        # Subscriber to raw camera stream
        self.subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.image_callback,
            10
        )
        
        # Publisher for processed image with bounding boxes
        self.publisher_ = self.create_publisher(
            Image,
            '/camera/image_detections',
            10
        )

        # Load YOLO model
        package_share = get_package_share_directory('four_wheels_robot')
        model_path = os.path.join(package_share, 'AI_model', 'agv_detector.pt')
        self.get_logger().info(f"Loading YOLO model from: {model_path}")
        self.model = YOLO(model_path)

    def image_callback(self, msg):
        try:
            # Convert incoming ROS Image to OpenCV BGR matrix
            cv_image = self.br.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as e:
            self.get_logger().error(f"CvBridge conversion failed: {e}")
            return

        # 1. Run inference
        results = self.model(cv_image, verbose=False)

        # 2. Draw bounding boxes automatically on the frame (returns BGR numpy array)
        annotated_frame = results[0].plot()

        # 3. Render directly in an OpenCV window (Optional for local testing)
        cv2.imshow("YOLO Detections", annotated_frame)
        cv2.waitKey(1)

        # 4. Convert annotated frame back to ROS Image message and publish
        try:
            out_msg = self.br.cv2_to_imgmsg(annotated_frame, encoding="bgr8")
            out_msg.header = msg.header  # Preserve timestamp and frame_id
            self.publisher_.publish(out_msg)
        except CvBridgeError as e:
            self.get_logger().error(f"Failed to publish annotated image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = ImageProcessingNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()