from skimage.morphology import skeletonize
import matplotlib.pyplot as plt
from utils import segmentation
from utils import orientation
import numpy as np
import cv2
from utils import frequency

def visualize_full_process(original, intermediate_img, skeleton, minutiae_template):
    overlay_image = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    for minutia in minutiae_template:
        r, c = minutia['r'], minutia['c']
        m_type = minutia['type']
        color = (0, 255, 0)
        if m_type == 'ending':
            color = (255, 0, 0)
        elif m_type == 'bifurcation':
            color = (0, 0, 255)
        cv2.circle(overlay_image, (c, r), radius=5, color=color, thickness=2)
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    axes[0].imshow(original, cmap='gray')
    axes[0].set_title('1. Original Image')
    axes[0].axis('off')
    axes[1].imshow(intermediate_img, cmap='gray')
    axes[1].set_title('2. Processed (Normalized/Binarized)')
    axes[1].axis('off')
    axes[2].imshow(skeleton, cmap='gray')
    axes[2].set_title('3. Thinned Skeleton')
    axes[2].axis('off')
    axes[3].imshow(cv2.cvtColor(overlay_image, cv2.COLOR_BGR2RGB))
    axes[3].set_title(f"4. Minutiae Detected ({len(minutiae_template)} points)")
    axes[3].axis('off')
    
    plt.suptitle("Fingerprint Processing Pipeline (Close this window to continue)")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show() 


def preprocess_and_extract(image_path):
    """Main pipeline to process an image and extract features."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    w=16
    segmented_img, normalized_img, mask = segmentation.create_segmented_and_variance_images(img, w, 0.2)    
    
    #Orientation field calculation and visualization
    print("Calculating orientation field...")
    angles = orientation.calculate_angles(normalized_img, W=w, smoth=True)
    print("Visualizing orientation field...")
    orientation_image = orientation.visualize_angles(segmented_img, mask, angles, W=w)
    cv2.imshow('Orientation Field', orientation_image)
    cv2.waitKey(0) 
    cv2.destroyAllWindows()
    window_name = 'Orientation Field (Resizable)'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    target_height = 400
    h, w, _ = orientation_image.shape
    scale = target_height / h
    new_width = int(w * scale)
    new_height = int(h * scale)
    resized_orientation_image = cv2.resize(orientation_image, (new_width, new_height), interpolation=cv2.INTER_NEAREST)
    cv2.imshow(window_name, resized_orientation_image)
    print("Press any key in the 'Orientation Field' window to continue...")
    cv2.waitKey(0) 
    cv2.destroyAllWindows()
    
    #Ridge Frequency Estimation (NEWLY ADDED)
    print("Estimating ridge frequency...")
    frequency_map = frequency.ridge_freq(normalized_img, mask, angles, w, kernel_size=5, minWaveLength=5, maxWaveLength=15)
    min_freq = np.min(frequency_map)
    max_freq = np.max(frequency_map)
    print(f"Frequency Map Stats: Min={min_freq:.4f}, Max={max_freq:.4f}, Mean={np.mean(frequency_map):.4f}")
    if max_freq == min_freq:
        print("Warning: Frequency map is uniform. It will appear as a single color (likely black).")
        visual_frequency_map = np.full(frequency_map.shape, int(max_freq * 255), dtype=np.uint8)
    else:
        visual_frequency_map = ((frequency_map - min_freq) / (max_freq - min_freq)) * 255
        visual_frequency_map = visual_frequency_map.astype(np.uint8)

    cv2.imshow('Ridge Frequency Map', visual_frequency_map)
    print("Press any key in the 'Ridge Frequency Map' window to continue...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    

    
    binary_image = cv2.adaptiveThreshold(normalized_img.astype(np.uint8), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 11, 2)
    skeleton = skeletonize(binary_image / 255).astype(np.uint8) * 255 
    minutiae_template = find_minutiae(skeleton)
    print("Displaying processing steps... Close the plot window to continue.")
    visualize_full_process(img, binary_image, skeleton, minutiae_template)
    return minutiae_template

def find_minutiae(skeleton_image):
    """Finds minutiae points and converts coordinates to standard Python integers."""
    skeleton_image = skeleton_image // 255
    minutiae = []
    kernel = np.array([[1, 1, 1], [1, 10, 1], [1, 1, 1]], dtype=np.uint8)
    neighbor_count = cv2.filter2D(skeleton_image, -1, kernel, borderType=cv2.BORDER_CONSTANT)
    ridge_pixels = np.where(skeleton_image == 1)
    
    for r, c in zip(*ridge_pixels):
        cn = neighbor_count[r, c] - 10
        py_r, py_c = int(r), int(c)

        if cn == 1:
            minutiae.append({'r': py_r, 'c': py_c, 'type': 'ending'})
        elif cn == 3:
            minutiae.append({'r': py_r, 'c': py_c, 'type': 'bifurcation'})
            
    return minutiae


def compare_templates(candidate_template, stored_template, threshold=5):
    if not candidate_template or not stored_template:
        return 0.0
    print("candidate:", candidate_template)
    print("stored_template:", stored_template)
    matched_points = 0
    for m_cand in candidate_template:
        for m_stored in stored_template:
            dist = np.sqrt((m_cand['r'] - m_stored['r'])**2 + (m_cand['c'] - m_stored['c'])**2)
            if dist < threshold and m_cand['type'] == m_stored['type']:
                matched_points += 1
                break
    
    if len(candidate_template) == 0:
        return 0.0
        
    match_score = (matched_points / len(candidate_template)) * 100
    return match_score