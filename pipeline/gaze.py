#!/usr/bin/env python3.12
"""Карта взгляда: где ведущий смотрит не в камеру.

gaze.py <proxy.mp4> <out.json> [--offset СЕК]
proxy.mp4 — лёгкая копия записи (5 кадров/с, 640 px), offset — с какой секунды исходника она начинается.
Выход: {"fps":5,"samples":[[t, yaw, pitch, iris_x, iris_y, ok]], "away":[[t0,t1],...]}
Правило «мимо камеры»: голова повёрнута/наклонена или зрачки ушли от своего обычного положения
дольше 0,5 с. «Обычное» положение берётся как медиана по всей записи (ведущий почти всё время смотрит в камеру).
Нужен python3.12 + mediapipe==0.10.14 (там модели встроены, интернет не нужен).
"""
import sys, json, cv2, numpy as np, mediapipe as mp

src, out = sys.argv[1], sys.argv[2]
offset = float(sys.argv[sys.argv.index('--offset') + 1]) if '--offset' in sys.argv else 0.0
fm = mp.solutions.face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS) or 5
S = []; i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    t = offset + i / fps; i += 1
    r = fm.process(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    if not r.multi_face_landmarks:
        S.append([round(t, 2), 0, 0, 0, 0, 0]); continue
    L = r.multi_face_landmarks[0].landmark
    P = lambda k: np.array([L[k].x, L[k].y])
    # голова: нос относительно середины глаз и рта
    le, re, nose, mouth = (P(33) + P(133)) / 2, (P(362) + P(263)) / 2, P(1), (P(61) + P(291)) / 2
    eye_mid = (le + re) / 2; ew = np.linalg.norm(re - le) + 1e-6
    yaw = (nose[0] - eye_mid[0]) / ew
    pitch = (nose[1] - eye_mid[1]) / (np.linalg.norm(mouth - eye_mid) + 1e-6)
    # зрачки внутри глаз (468 — левый зрачок, 473 — правый)
    def ratio(c, a, b, top, bot):
        w = P(b) - P(a); h = P(bot) - P(top)
        return (np.dot(P(c) - P(a), w) / (np.dot(w, w) + 1e-9), np.dot(P(c) - P(top), h) / (np.dot(h, h) + 1e-9))
    lx, ly = ratio(468, 33, 133, 159, 145); rx, ry = ratio(473, 362, 263, 386, 374)
    S.append([round(t, 2), round(float(yaw), 4), round(float(pitch), 4), round(float((lx + rx) / 2), 4), round(float((ly + ry) / 2), 4), 1])

A = np.array(S, dtype=float)
okm = A[:, 5] == 1
med = np.median(A[okm, 1:5], axis=0); mad = np.median(np.abs(A[okm, 1:5] - med), axis=0) + 1e-4
z = np.zeros(len(A))
z[okm] = np.max(np.abs(A[okm, 1:5] - med) / (mad * np.array([6, 6, 5, 5])), axis=1)
bad = (~okm) | (z > 1.0)
# сгладить и собрать интервалы ≥ 0,5 с
away = []; start = None
for k, b in enumerate(bad):
    t = A[k, 0]
    if b and start is None: start = t
    if not b and start is not None:
        if t - start >= 0.5: away.append([round(start, 2), round(t, 2)])
        start = None
if start is not None and A[-1, 0] - start >= 0.5: away.append([round(start, 2), round(float(A[-1, 0]) + 1 / fps, 2)])
json.dump({'fps': fps, 'median': med.round(4).tolist(), 'samples': S, 'away': away}, open(out, 'w'))
print('кадров', len(S), 'без лица', int((~okm).sum()), 'интервалов мимо камеры', len(away))
for a in away: print(f'  {a[0]:.1f}–{a[1]:.1f} ({a[1]-a[0]:.1f} с)')
