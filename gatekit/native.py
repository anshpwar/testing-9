"""ctypes bindings for build/libgate.{dylib,so}. Structure layouts mirror c/include/gate.h."""
import ctypes
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
_EXT = "dylib" if sys.platform == "darwin" else "so"
LIB_PATH = ROOT / "build" / f"libgate.{_EXT}"

GATE_MAX_HEADERS = 64
ERR_ARG, ERR_SYNTAX, ERR_TOO_LONG, ERR_TOO_MANY = -1, -2, -3, -4


class GateRequest(ctypes.Structure):
    _fields_ = [
        ("method", ctypes.c_char * 8),
        ("path", ctypes.c_char * 128),
        ("version_minor", ctypes.c_int32),
        ("header_count", ctypes.c_int32),
        ("content_length", ctypes.c_int32),
        ("keep_alive", ctypes.c_int32),
    ]


class GateBucket(ctypes.Structure):
    _fields_ = [
        ("capacity_milli", ctypes.c_int64),
        ("tokens_milli", ctypes.c_int64),
        ("refill_per_s_milli", ctypes.c_int64),
        ("last_ts_ms", ctypes.c_int64),
    ]


def _load():
    if not LIB_PATH.exists():
        subprocess.run(["make", "-C", str(ROOT), "-s", "build"], check=True, capture_output=True)
    lib = ctypes.CDLL(str(LIB_PATH))
    lib.gate_parse_request.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(GateRequest)]
    lib.gate_parse_request.restype = ctypes.c_int
    lib.gate_header_get.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
    lib.gate_header_get.restype = ctypes.c_int
    lib.gate_bucket_init.argtypes = [ctypes.POINTER(GateBucket), ctypes.c_int64, ctypes.c_int64, ctypes.c_int64]
    lib.gate_bucket_init.restype = ctypes.c_int
    lib.gate_bucket_take.argtypes = [ctypes.POINTER(GateBucket), ctypes.c_int64, ctypes.c_int64]
    lib.gate_bucket_take.restype = ctypes.c_int
    lib.gate_bucket_retry_after_ms.argtypes = [ctypes.POINTER(GateBucket), ctypes.c_int64]
    lib.gate_bucket_retry_after_ms.restype = ctypes.c_int64
    lib.gate_sizeof_request.restype = ctypes.c_size_t
    lib.gate_sizeof_bucket.restype = ctypes.c_size_t
    return lib


lib = _load()


class ParseError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__({ERR_ARG: "bad argument", ERR_SYNTAX: "syntax error", ERR_TOO_LONG: "line too long",
                          ERR_TOO_MANY: "too many headers"}.get(code, f"error {code}"))


def parse_request(raw):
    """Return (request_dict, consumed_bytes) or (None, 0) when the head is incomplete."""
    req = GateRequest()
    rc = lib.gate_parse_request(raw, len(raw), ctypes.byref(req))
    if rc < 0:
        raise ParseError(rc)
    if rc == 0:
        return None, 0
    return ({"method": req.method.decode(), "path": req.path.decode(), "version_minor": req.version_minor,
             "header_count": req.header_count, "content_length": req.content_length,
             "keep_alive": bool(req.keep_alive)}, rc)


def header(raw, name):
    buf = ctypes.create_string_buffer(512)
    rc = lib.gate_header_get(raw, len(raw), name.encode(), buf, len(buf))
    if rc < 0:
        raise ParseError(rc)
    return buf.value.decode() if rc else None


class Bucket:
    def __init__(self, capacity, refill_per_s, now_ms):
        self._b = GateBucket()
        rc = lib.gate_bucket_init(ctypes.byref(self._b), capacity, refill_per_s, now_ms)
        if rc < 0:
            raise ValueError("invalid bucket parameters")

    def take(self, now_ms, cost=1):
        rc = lib.gate_bucket_take(ctypes.byref(self._b), cost, now_ms)
        if rc < 0:
            raise ValueError("invalid take")
        return bool(rc)

    def retry_after_ms(self, cost=1):
        return lib.gate_bucket_retry_after_ms(ctypes.byref(self._b), cost)
