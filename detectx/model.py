from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass(frozen=True)
class Detection:
    xyxy: Tuple[float, float, float, float]
    conf: float
    cls_id: int
    cls_name: str


class YoloV8Detector:
    def __init__(self, model_path: str, conf: float = 0.25, iou: float = 0.45, device: str = "cpu"):
        from ultralytics import YOLO  # type: ignore

        self._model = YOLO(model_path)
        self._conf = float(conf)
        self._iou = float(iou)
        self._device = str(device)

    def infer_bgr(self, bgr: np.ndarray) -> List[Detection]:
        # Convert BGR->RGB for Ultralytics
        rgb = bgr[:, :, ::-1].copy()

        results = self._model.predict(
            source=rgb,
            conf=self._conf,
            iou=self._iou,
            device=self._device,
            verbose=False,
        )

        dets: List[Detection] = []
        if not results:
            return dets

        r0 = results[0]
        names = r0.names if hasattr(r0, "names") else {}

        if getattr(r0, "boxes", None) is None or len(r0.boxes) == 0:
            return dets

        boxes = r0.boxes
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        clss = boxes.cls.cpu().numpy().astype(int)

        for (x1, y1, x2, y2), c, k in zip(xyxy, confs, clss):
            name = str(names.get(int(k), str(int(k))))
            dets.append(
                Detection(
                    xyxy=(float(x1), float(y1), float(x2), float(y2)),
                    conf=float(c),
                    cls_id=int(k),
                    cls_name=name,
                )
            )
        return dets
