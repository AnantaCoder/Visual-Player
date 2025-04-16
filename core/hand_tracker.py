import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.7, tracing_confidence=0.7):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracing_confidence
        )

        self.draw_utils = mp.solutions.drawing_utils
        self.hand_connections = mp.solutions.hands.HAND_CONNECTIONS

        
    def process_frame(self,frame):
        rgb_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        finger_count = 0 
        
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                self.draw_utils.draw_landmarks(frame, landmarks, self.hand_connections)
                # set finger count and gestures 
                finger_count = self.count_fingers(landmarks, frame.shape)
                gesture = self.identify_fingers(landmarks,frame.shape)
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.putText(frame, f"Gesture: {gesture}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
        return finger_count, frame
    def count_fingers(self,landmarks,frame_shape):
        h,w, _ = frame_shape
        
        pointers = [(int(lm.x*w),int(lm.y*h)) for lm in landmarks.landmark]
        fingers = []
        if pointers[4][0] > pointers[3][0]:  
            fingers.append(1)
        else:
            fingers.append(0)

        tips = [8, 12, 16, 20]
        lower_joints = [6, 10, 14, 18]

        for tip, joint in zip(tips, lower_joints):
            if pointers[tip][1] < pointers[joint][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        return sum(fingers)
        
    def get_finger_status(self,landmarks, frame_shape):
        h,w,_ = frame_shape
        points = [(int(lm.x*w),int(lm.y*h)) for lm in landmarks.landmark]
        finger_status = {
            "thumb": False,
            "index": False,
            "middle": False,
            "ring": False,
            "pinky": False
        }
        finger_status["thumb"] = points[4][0] > points[3][0]
        
        # Check other fingers
        finger_names = ["index", "middle", "ring", "pinky"]
        finger_tips = [8, 12, 16, 20]
        for name,tip in zip(finger_names,finger_tips):
            finger_status[name] = points[tip][1] < points[tip - 2][1]
            
        return finger_status
    
    def identify_fingers(self,landmarks , frame_shape):
        finger_status = self.get_finger_status(landmarks,frame_shape)
        if all(finger_status.values()):
            return "Open Hand"
        elif not any(finger_status.values()):
            return "Fist"
        elif finger_status["index"] and not any(v for k, v in finger_status.items() if k != "index"):
            return "Pointing"
        elif finger_status["index"] and finger_status["thumb"] and not any(v for k, v in finger_status.items() if k not in ["index", "thumb"]):
            return "Gun"
        elif finger_status["index"] and finger_status["pinky"] and not finger_status["middle"] and not finger_status["ring"]:
            return "Rock Sign"
        elif finger_status["thumb"] and not any(v for k, v in finger_status.items() if k != "thumb"):
            return "Thumbs Up"
        else:
            return "Unknown Gesture"
        
    
if __name__ == "__main__":
    cap = cv2.VideoCapture(0) #for default cam 
    # adjust cap height and width 
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
    # adjust screen automatically while resizing 
    cv2.namedWindow("Hand Tracker",cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Hand Tracker", 1280,720)
    
    tracker = HandTracker()
    while True :
        ret,frame = cap.read()
        if not ret:
            break
        finger_count , frame = tracker.process_frame(frame)
        cv2.imshow("Hand Tracker",frame)
        
        # exit 
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    