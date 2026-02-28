# OpenCV Image Processing Expert

Use this expert for computer vision preprocessing, feature extraction, and measurement workflows using OpenCV (cv2).

## When to use this expert
- The task involves loading, transforming, or analyzing images (resize, crop, filter, threshold, segment).
- Color space conversion, morphological operations, or contour extraction is needed.
- The user needs to detect edges, keypoints, or objects in images.
- Camera calibration, image stitching, or geometric transformations are requested.

## Execution behavior

1. Load and validate the image: use `cv2.imread(path, flags)` and immediately check that the result is not `None`. Log the shape `(height, width, channels)` and dtype. Be aware that OpenCV loads images in BGR order, not RGB.
2. Convert color spaces in the correct order: BGR to RGB for display/matplotlib, BGR to GRAY for processing, BGR to HSV for color-based segmentation. Always use `cv2.cvtColor` with the correct conversion code (e.g., `cv2.COLOR_BGR2RGB`).
3. Apply preprocessing steps in a logical sequence: resize (if needed for consistency), denoise (`cv2.GaussianBlur`, `cv2.fastNlMeansDenoising`), contrast enhancement (`cv2.equalizeHist` or CLAHE), then task-specific operations.
4. For segmentation, choose the appropriate method: simple thresholding (`cv2.threshold`) for bimodal histograms, adaptive thresholding for uneven lighting, Otsu's method when the threshold should be auto-selected, or color-range masking in HSV space.
5. Apply morphological operations to clean binary masks: `cv2.morphologyEx` with `MORPH_OPEN` to remove small noise, `MORPH_CLOSE` to fill small holes, `MORPH_DILATE`/`MORPH_ERODE` for boundary adjustment. Select kernel size based on feature scale.
6. Extract contours with `cv2.findContours` using the appropriate retrieval mode: `RETR_EXTERNAL` for outermost contours only, `RETR_TREE` for full hierarchy. Filter contours by area, aspect ratio, or solidity to remove spurious detections.
7. Compute measurements: `cv2.contourArea`, `cv2.arcLength`, `cv2.boundingRect`, `cv2.minEnclosingCircle`, `cv2.moments` for centroid calculation. Convert pixel measurements to physical units using a known scale factor when available.
8. Save processed outputs with `cv2.imwrite` and register them as artifacts. Preserve originals and processed versions separately with descriptive filenames.

## Decision tree
- If detecting edges -> use Canny edge detection. Apply Gaussian blur first to reduce noise edges. Tune the low and high thresholds (typical ratio 1:2 or 1:3).
- If segmenting by color -> convert to HSV, define hue/saturation/value ranges with `cv2.inRange`, and apply morphological cleanup. HSV is more robust to lighting variation than RGB.
- If the image has uneven illumination -> use adaptive thresholding (`cv2.adaptiveThreshold`) or CLAHE (`cv2.createCLAHE`) instead of global operations.
- If aligning or registering images -> use feature matching (ORB, SIFT) with `cv2.findHomography` and `cv2.warpPerspective`. Use RANSAC for robust estimation.
- If measuring objects -> calibrate first (or use a known reference object in the scene), then convert pixel distances to physical units.
- If processing a batch of images -> verify that all images have the same dimensions and channels, or resize to a common size before batch operations.

## Anti-patterns
- NEVER display images loaded by OpenCV directly in matplotlib without converting BGR to RGB. The colors will be swapped (blue faces, orange skies).
- NEVER apply morphological operations with a kernel size of 1x1. It is a no-op that wastes computation.
- NEVER use `cv2.resize` with interpolation `INTER_NEAREST` for downscaling photographic images. Use `INTER_AREA` for shrinking and `INTER_LINEAR` or `INTER_CUBIC` for enlarging.
- NEVER assume `cv2.imread` succeeded without checking for `None`. Missing or corrupt files return `None` silently.
- NEVER apply edge detection or contour finding on a color image directly. Convert to grayscale first.
- NEVER hard-code threshold values without inspecting the histogram. Thresholds that work on one image may fail on another with different lighting.

## Common mistakes
- Confusing `(height, width)` with `(width, height)`. OpenCV uses `(rows, cols)` which is `(height, width)`, but functions like `cv2.resize` expect `(width, height)` as the `dsize` argument.
- Forgetting that `cv2.findContours` modifies the input image in older OpenCV versions. Always pass a copy of the binary mask.
- Using `cv2.GaussianBlur` with an even kernel size, which raises an error. Kernel sizes must be odd (3, 5, 7, ...).
- Applying CLAHE to a color image channel-by-channel in RGB, which distorts colors. Convert to LAB, apply CLAHE to the L channel only, then convert back.
- Not accounting for JPEG compression artifacts when doing fine-grained analysis. Use PNG or TIFF for lossless intermediate storage.
- Setting contour area filters too aggressively, silently dropping valid small objects. Always visualize filtered contours to verify.

## Output contract
- Preserve original and processed images as separate files. Never overwrite the input.
- Record parameter values for each transform step (kernel sizes, thresholds, interpolation methods) in metadata.
- Include quality checks: flag low-contrast inputs, saturated regions, or images with unexpected dimensions.
- Report detection results (contour count, areas, centroids) in a structured table or dict.
- When detection confidence is weak (few contours, low contrast), report the limitation explicitly.
- Save intermediate pipeline stages (grayscale, thresholded, morphed) when debugging or when the user requests pipeline transparency.
- State the OpenCV version and whether the processing was done in 8-bit or floating-point precision.

## Composability hints
- Before this expert -> use the **Data Cleaning Expert** if image metadata (filenames, labels) needs normalization before batch processing.
- After this expert -> use the **PyTorch Training Expert** to feed preprocessed images into a neural network for classification or detection.
- After this expert -> use the **Visualization Expert** to create annotated figure panels comparing original and processed images.
- After this expert -> use the **PDF Creation Expert** to embed image analysis results in a report.
- Related -> the **SciPy Signal Expert** for frequency-domain image analysis or advanced filtering operations.
