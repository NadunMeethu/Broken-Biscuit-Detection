import cv2
import numpy as np
import os

# This gets the location of this Python file inside the src folder
base_dir = os.path.dirname(os.path.abspath(__file__))

project_dir = os.path.dirname(base_dir)

# These are the folders where input images are taken and output images are saved
input_folder = os.path.join(project_dir, "inputs")
output_folder = os.path.join(project_dir, "output_images")

os.makedirs(output_folder, exist_ok=True)

# This gets all image files from the input folder
image_files = [
    f for f in os.listdir(input_folder)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

print("Images found:", image_files)

# This loop runs the detection process for every image in the input folder
for file_name in image_files:
    image_path = os.path.join(input_folder, file_name)
    output_path = os.path.join(output_folder, "result_" + file_name)

   
    image = cv2.imread(image_path)

    
    if image is None:
        print("Could not read:", file_name)
        continue

    
    output = image.copy()

    # Convert BGR image to HSV colour space
    # HSV helps to separate biscuit colour from the white background
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    
    lower = np.array([5, 50, 50])
    upper = np.array([50, 255, 255])

   
    mask = cv2.inRange(hsv, lower, upper)

    # Use morphological operations to remove small noise and fill small gaps
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Find the outer contours of the detected biscuit regions
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Check each detected contour one by one
    for cnt in contours:

        area = cv2.contourArea(cnt)

        if area < 3000:
            continue

        # Calculate the perimeter of the contour
        perimeter = cv2.arcLength(cnt, True)

        if perimeter == 0:
            continue

        circularity = (4 * np.pi * area) / (perimeter * perimeter)

        
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)
        vertices = len(approx)

        x, y, w, h = cv2.boundingRect(cnt)

        
        aspect_ratio = float(w) / h

        # By default, detected objects are considered broken
        label = "Broken Biscuit"
        color = (0, 0, 255)

        # Circle detection part
        
        if circularity > 0.67 and vertices > 6:
            if circularity > 0.78:
                label = "Intact Biscuit (Circle)"
                color = (0, 255, 0)
            else:
                label = "Broken Biscuit (Circle)"
                color = (0, 0, 255)

        # Square detection part
        
        elif 3 <= vertices <= 6:
            if area > 15000 and 0.75 < aspect_ratio < 1.35 and vertices == 4:
                label = "Intact Biscuit (Square)"
                color = (0, 255, 0)
            else:
                label = "Broken Biscuit (Square)"
                color = (0, 0, 255)

        # Draw the detected biscuit contour on the output image
        cv2.drawContours(output, [cnt], -1, color, 2)

        # Draw a rectangle around the detected biscuit
        cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)

  
        cv2.putText(
            output,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            color,
            5
        )

    # Save the final annotated image into the output folder
    cv2.imwrite(output_path, output)
    print("Processed:", file_name)

print("All images processed.")