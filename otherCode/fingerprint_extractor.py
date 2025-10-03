import cv2
import numpy as np
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
import os
import json

IMAGE_PATH = 'fingerprint.jpg'

def find_minutiae(skeleton_image):
    skeleton_image = skeleton_image // 255
    minutiae = []
    rows, cols = skeleton_image.shape
    
    kernel = np.array([[1, 1, 1],
                       [1, 10, 1],
                       [1, 1, 1]], dtype=np.uint8)

    neighbor_count = cv2.filter2D(skeleton_image, -1, kernel, borderType=cv2.BORDER_CONSTANT)
    
    ridge_pixels = np.where(skeleton_image == 1)
    
    for r, c in zip(*ridge_pixels):
        cn = neighbor_count[r, c] - 10
        
        if cn == 1:
            minutiae.append({'r': int(r), 'c': int(c), 'type': 'ending'})
        elif cn == 3:
            minutiae.append({'r': int(r), 'c': int(c), 'type': 'bifurcation'})
            
    return minutiae

def preprocess_and_extract(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not load image at {image_path}")
        return None, None

    binary_image = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 11, 2)

    kernel = np.ones((3, 3), np.uint8)
    cleaned_image = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel, iterations=1)

    skeleton = skeletonize(cleaned_image / 255).astype(np.uint8) * 255

    minutiae_template = find_minutiae(skeleton)
    
    processed_images = {
        'original': img,
        'binary': cleaned_image,
        'skeleton': skeleton
    }
    
    return minutiae_template, processed_images

def visualize_results(images, template):
    output_image = cv2.cvtColor(images['original'], cv2.COLOR_GRAY2BGR)
    
    for m in template:
        c, r = m['c'], m['r']
        if m['type'] == 'ending':
            cv2.circle(output_image, (c, r), 5, (255, 0, 0), 2)
        elif m['type'] == 'bifurcation':
            cv2.circle(output_image, (c, r), 5, (0, 0, 255), 2)
    
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    
    axes[0].imshow(images['original'], cmap='gray')
    axes[0].set_title('1. Original Image')
    axes[0].axis('off')
    
    axes[1].imshow(images['binary'], cmap='gray')
    axes[1].set_title('2. Binarized & Cleaned')
    axes[1].axis('off')
    
    axes[2].imshow(images['skeleton'], cmap='gray')
    axes[2].set_title('3. Thinned Skeleton')
    axes[2].axis('off')
    
    axes[3].imshow(cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB))
    axes[3].set_title(f"4. Minutiae Detected ({len(template)} points)")
    axes[3].axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    if not os.path.exists(IMAGE_PATH):
        print(f"\n--- ERROR ---")
        print(f"File not found: '{IMAGE_PATH}'")
    else:
        print("--- Starting Fingerprint Feature Extraction ---")
        
        template, processed_images = preprocess_and_extract(IMAGE_PATH)
        
        if template:
            print(f"Extraction successful. Total minutiae points found: {len(template)}")
            
            print("\n--- Generated Template (first 5 points) ---")
            for point in template[:5]:
                print(point)
            
            template_json = json.dumps(template, indent=2)
            
            visualize_results(processed_images, template)