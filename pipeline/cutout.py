# python3.12 cutout.py in.jpg out.png [width] — вырезка человека (mediapipe selfie segmentation) → PNG с альфой
import sys, cv2, numpy as np, mediapipe as mp
src, dst = sys.argv[1:3]; W = int(sys.argv[3]) if len(sys.argv) > 3 else 1400
im = cv2.imread(src); h, w = im.shape[:2]; im = cv2.resize(im, (W, int(h * W / w)))
with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0) as s:
    m = s.process(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)).segmentation_mask
m = cv2.GaussianBlur(np.clip((m - 0.35) / 0.3, 0, 1), (5, 5), 0)
out = np.dstack([im, (m * 255).astype(np.uint8)])
ys, xs = np.where(m > 0.5); out = out[max(0, ys.min() - 20):, :]
cv2.imwrite(dst, out)
