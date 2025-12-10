import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mphands = mp.solutions.hands

cap = cv2.VideoCapture(0)
hands = mphands.Hands()

while True:
    data, image = cap.read()
    
    # Görüntüyü aynala ve RGB'ye çevir
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    
    # El tespiti yap
    results = hands.process(image)
    
    # Tekrar BGR'ye çevir (OpenCV için)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # El landmarkları varsa çiz
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mphands.HAND_CONNECTIONS
            )
    
    cv2.imshow('Handtracker', image)
    
    # ESC tuşu ile çık
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
