import cv2
import time


def captureImageCCTV(CAMERA, path):

    # if length = one it's laptop camera so convert it to integer
    if len(CAMERA) == 1:
        CAMERA = int(CAMERA)

    # open camera
    cap = cv2.VideoCapture(CAMERA, cv2.CAP_DSHOW)

    # wait camera
    # if CAMERA == 0:
    #     time.sleep(5)

    # Check if camera opened successfully
    # if (cap.isOpened() == False): 
    #     print("Unable to read camera feed")
    #     return False

    result, frame = cap.read()

    if result:
        cv2.imwrite(path, frame)

    # When everything done, release the video capture and video write objects
    # cap.release()

    # Closes all the frames
    # cv2.destroyAllWindows() 

    return path
