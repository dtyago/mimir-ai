import cv2
from mtcnn.mtcnn import MTCNN
import numpy as np


def load_image(filename):
    """Load an image from a file path."""
    img = cv2.imread(filename)
    if img is None:
        raise ValueError(f"Could not load image from {filename}. Please ensure the file is a valid image format.")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def normalize(img):
    """Normalize the given image array."""
    mean, std = img.mean(), img.std()
    return (img - mean) / std


def detect_faces_with_mtcnn(img):
    """Detect faces in an image using MTCNN."""
    detector = MTCNN()
    bounding_boxes = []
    detected_faces = detector.detect_faces(img)
    for detected_face in detected_faces:
        bounding_boxes.append(detected_face["box"])
    return bounding_boxes


# Crops out parts of an image based on a list of bounding
# boxes. The cropped faces are also resized to 160x160 in
# preparation for passing it to FaceNet to compute the
# face embeddings.
#
def crop_faces_to_160x160(img, bounding_boxes):
    """Crop faces from an image based on detections."""
    cropped_faces = []

    for (x,y,w,h) in bounding_boxes:
        cropped_face = img[y:y+h, x:x+w]
        normalize(cropped_face)
        cropped_face = cv2.resize(cropped_face, (160, 160), interpolation=cv2.INTER_CUBIC)
        cropped_faces.append(cropped_face)

    return np.array(cropped_faces)


# Extract cropped user face image
#
def get_user_cropped_image_from_photo(filename):

    # Load the image.
    #...#
    img = load_image(filename)


    # Detect faces and extract all bounding boxes
    #...#
    bounding_boxes = detect_faces_with_mtcnn(img)


    # Crop out the faces from the image
    #...#
    cropped_faces = crop_faces_to_160x160(img, bounding_boxes)

    if cropped_faces.shape[0] == 0:
        return


    # Take the image of only the first detected face
    #...#
    cropped_face = cropped_faces[0:1, :, :, :]


    # Get the face embeddings using FaceNet and return
    # the results.
    #...#
    return cropped_face[0]


