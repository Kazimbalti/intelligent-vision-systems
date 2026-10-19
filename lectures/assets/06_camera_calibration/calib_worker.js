/* Webcam Calibration Studio - worker.
 * Runs the real OpenCV-Python (cv2 4.10, via Pyodide/WebAssembly) off the main thread, so the video stays smooth.
 * Every OpenCV call here is the same call students write in Lab 6.
 */
importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js");

let py = null;

const PY = `
import cv2, numpy as np, json

S = {"obj": [], "img": [], "size": None, "K": None, "D": None, "nx": 9, "ny": 6, "square": 25.0}
CRIT = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

def board_points(nx, ny, square):
    objp = np.zeros((nx * ny, 3), np.float32)
    objp[:, :2] = np.mgrid[0:nx, 0:ny].T.reshape(-1, 2) * square
    return objp

def gray_of(buf, w, h):
    b = buf.to_bytes() if hasattr(buf, "to_bytes") else bytes(buf)
    return np.frombuffer(b, np.uint8).reshape(h, w)

def detect(buf, w, h, nx, ny, fast):
    g = gray_of(buf, w, h)
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE
    if fast:
        flags |= cv2.CALIB_CB_FAST_CHECK
    ok, c = cv2.findChessboardCorners(g, (nx, ny), flags)
    return json.dumps(c.reshape(-1).tolist() if ok else None)

def capture(buf, w, h, nx, ny):
    g = gray_of(buf, w, h)
    ok, c = cv2.findChessboardCorners(g, (nx, ny), cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE)
    if not ok:
        return json.dumps(None)
    c = cv2.cornerSubPix(g, c.reshape(-1, 1, 2), (11, 11), (-1, -1), CRIT).reshape(-1, 1, 2)
    if S["size"] is not None and S["size"] != (w, h):
        return json.dumps({"error": "size"})
    S["size"] = (w, h); S["nx"], S["ny"] = nx, ny
    S["img"].append(c)
    return json.dumps({"corners": c.reshape(-1).tolist(), "n": len(S["img"])})

def remove_view(i):
    del S["img"][i]
    if not S["img"]:
        S["size"] = None
    return len(S["img"])

def reset():
    S["img"].clear(); S["size"] = None; S["K"] = None; S["D"] = None
    return 0

def calibrate(square, model):
    S["square"] = square
    objp = board_points(S["nx"], S["ny"], square)
    obj = [objp] * len(S["img"])
    flags = cv2.CALIB_RATIONAL_MODEL if model == "rational" else 0
    rms, K, D, rv, tv, std_in, std_ex, per_view = cv2.calibrateCameraExtended(obj, S["img"], S["size"], None, None, flags=flags)
    S["K"], S["D"] = K, D
    w, h = S["size"]
    names = ["fx", "fy", "cx", "cy", "k1", "k2", "p1", "p2", "k3"]
    std = {n: float(s) for n, s in zip(names, std_in.ravel()[:9])}
    dist_mm = [float(np.linalg.norm(t)) for t in tv]
    return json.dumps({"rms": float(rms), "K": K.tolist(), "D": D.ravel().tolist(), "per_view": per_view.ravel().tolist(),
                       "std": std, "size": [w, h], "n": len(S["img"]), "dist_mm": dist_mm,
                       "hfov": float(2 * np.degrees(np.arctan(w / 2 / K[0, 0]))), "vfov": float(2 * np.degrees(np.arctan(h / 2 / K[1, 1])))})

def set_calibration(K, D, w, h):
    S["K"] = np.array(K, float).reshape(3, 3); S["D"] = np.array(D, float).reshape(1, -1); S["size"] = (int(w), int(h))
    return 1

def maps(w, h, alpha):
    # undistortion lookup for a w x h view (K is scaled if the view size differs from the calibration size)
    K = S["K"].copy(); cw, ch = S["size"]
    K[0] *= w / cw; K[1] *= h / ch
    newK, roi = cv2.getOptimalNewCameraMatrix(K, S["D"], (w, h), alpha, (w, h))
    mx, my = cv2.initUndistortRectifyMap(K, S["D"], None, newK, (w, h), cv2.CV_32FC1)
    return mx.tobytes() + my.tobytes()

def pose(buf, w, h, nx, ny):
    if S["K"] is None:
        return json.dumps(None)
    g = gray_of(buf, w, h)
    ok, c = cv2.findChessboardCorners(g, (nx, ny), cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)
    if not ok:
        return json.dumps(None)
    c = cv2.cornerSubPix(g, c.reshape(-1, 1, 2), (5, 5), (-1, -1), CRIT)
    K = S["K"].copy(); cw, ch = S["size"]
    K[0] *= w / cw; K[1] *= h / ch
    objp = board_points(nx, ny, S["square"])
    ok, rvec, tvec = cv2.solvePnP(objp, c, K, S["D"])
    centre = objp.mean(0)
    R, _ = cv2.Rodrigues(rvec)
    pc = R @ centre + tvec.ravel()
    L = 3 * S["square"]
    axes = np.float32([[0, 0, 0], [L, 0, 0], [0, L, 0], [0, 0, -L]])
    ax, _ = cv2.projectPoints(axes, rvec, tvec, K, S["D"])
    tilt = float(np.degrees(np.arccos(abs(R[2, 2]))))
    return json.dumps({"t": tvec.ravel().tolist(), "centre": pc.tolist(), "dist": float(np.linalg.norm(pc)), "tilt": tilt,
                       "axes": ax.reshape(-1).tolist(), "corners": c.reshape(-1).tolist()})

def yaml_text():
    fs = cv2.FileStorage(".yaml", cv2.FILE_STORAGE_WRITE | cv2.FILE_STORAGE_MEMORY)
    w, h = S["size"]
    fs.write("image_width", w); fs.write("image_height", h)
    fs.write("camera_matrix", S["K"]); fs.write("distortion_coefficients", S["D"])
    fs.write("square_size_mm", S["square"]); fs.write("board_inner_corners", np.array([S["nx"], S["ny"]], np.int32))
    return fs.releaseAndGetString()
`;

async function init() {
  py = await loadPyodide();
  await py.loadPackage(["numpy", "opencv-python"]);
  py.runPython(PY);
  return py.runPython("cv2.__version__");
}

function call(name, ...args) {
  const f = py.globals.get(name);
  const out = f(...args);
  f.destroy();
  return out;
}

self.onmessage = async (ev) => {
  const m = ev.data;
  try {
    if (m.cmd === "init") {
      const v = await init();
      self.postMessage({ id: m.id, ok: true, version: v });
    } else if (m.cmd === "detect") {
      const r = call("detect", m.gray, m.w, m.h, m.nx, m.ny, true);
      self.postMessage({ id: m.id, ok: true, corners: JSON.parse(r), w: m.w, h: m.h });
    } else if (m.cmd === "capture") {
      const r = call("capture", m.gray, m.w, m.h, m.nx, m.ny);
      self.postMessage({ id: m.id, ok: true, result: JSON.parse(r) });
    } else if (m.cmd === "calibrate") {
      const r = call("calibrate", m.square, m.model || "standard");
      self.postMessage({ id: m.id, ok: true, result: JSON.parse(r) });
    } else if (m.cmd === "set") {
      call("set_calibration", py.toPy(m.K), py.toPy(m.D), m.w, m.h);
      self.postMessage({ id: m.id, ok: true });
    } else if (m.cmd === "maps") {
      const b = call("maps", m.w, m.h, m.alpha);
      const pb = b.getBuffer("u8"); const u8 = pb.data.slice(); pb.release(); b.destroy();
      const all = new Float32Array(u8.buffer, 0, u8.byteLength / 4);
      const n = m.w * m.h;
      const mx = all.slice(0, n), my = all.slice(n, 2 * n);
      self.postMessage({ id: m.id, ok: true, mx, my, w: m.w, h: m.h }, [mx.buffer, my.buffer]);
    } else if (m.cmd === "pose") {
      const r = call("pose", m.gray, m.w, m.h, m.nx, m.ny);
      self.postMessage({ id: m.id, ok: true, pose: JSON.parse(r) });
    } else if (m.cmd === "remove") {
      const n = call("remove_view", m.index);
      self.postMessage({ id: m.id, ok: true, n });
    } else if (m.cmd === "reset") {
      call("reset");
      self.postMessage({ id: m.id, ok: true });
    } else if (m.cmd === "yaml") {
      const r = call("yaml_text");
      self.postMessage({ id: m.id, ok: true, text: r });
    }
  } catch (e) {
    self.postMessage({ id: m.id, ok: false, error: String(e) });
  }
};
