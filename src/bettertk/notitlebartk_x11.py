# Mostly taken from: https://www.tonyobryan.com//index.php?article=9
# Inspired by: https://github.com/EDCD/EDMarketConnector/blob/main/theme.py
import tkinter as tk
import ctypes

# Defining types
CHAR = ctypes.c_char
UCHAR = ctypes.c_ubyte
BOOL = ctypes.c_bool
INT = ctypes.c_int
UINT = ctypes.c_uint
LONG = ctypes.c_long
PTR = ctypes.c_void_p

CHAR_PTR = ctypes.POINTER(CHAR)
UINT_PTR = ctypes.POINTER(UINT)
ULONG = ctypes.c_ulong

class HINTS(ctypes.Structure):
    _fields_ = (("flags", ULONG),
                ("functions", ULONG),
                ("decorations", ULONG),
                ("inputMode", LONG),
                ("status", ULONG))

DISPLAY = PTR
ATOM = LONG
WINDOW = LONG
WINDOW_PTR = ctypes.POINTER(WINDOW)
HINTS_PTR = ctypes.POINTER(HINTS)

def _errcheck_not_zero(value, func, args):
    if value == 0:
        args_str = ", ".join(map(str, args))
        raise OSError(f"{func.__name__}({args_str}) => {value}")
    return args

def string_to_c(data:str) -> CHAR_PTR:
    return ctypes.create_string_buffer(data.encode())

libx11 = ctypes.cdll.LoadLibrary("libX11.so.6")

# Constants
PropModeReplace = 0
XA_ATOM = 4

# Defining functions
XInternAtom = libx11.XInternAtom
XInternAtom.argtypes = (PTR, CHAR_PTR, BOOL)
XInternAtom.restype = ATOM
XInternAtom.errcheck = _errcheck_not_zero

XOpenDisplay = libx11.XOpenDisplay
XOpenDisplay.argtypes = (CHAR_PTR, )
XOpenDisplay.restype = DISPLAY
XOpenDisplay.errcheck = _errcheck_not_zero

XChangeProperty = libx11.XChangeProperty
XChangeProperty.argtypes = (DISPLAY, WINDOW, ATOM, ATOM, INT, INT, HINTS_PTR, INT)
XChangeProperty.restype = INT
XChangeProperty.errcheck = _errcheck_not_zero

XQueryTree = libx11.XQueryTree
XQueryTree.argtypes = (DISPLAY, WINDOW, WINDOW_PTR, WINDOW_PTR, WINDOW_PTR, UINT_PTR)
XQueryTree.restype = INT
XQueryTree.errcheck = _errcheck_not_zero

XFlush = libx11.XFlush
XFlush.argtypes = (DISPLAY, )
XFlush.restype = INT
XFlush.errcheck = _errcheck_not_zero


class NoTitlebarTk:
    def __init__(self, master=None, **kwargs):
        if master is None:
            self.root = tk.Tk(**kwargs)
        elif isinstance(master, tk.Misc):
            self.root = tk.Toplevel(master, **kwargs)
        else:
            raise ValueError("Invalid `master` argument. It must be " \
                             "`None` or a tkinter widget")

        self.locked:bool = False
        self._fullscreen:bool = False

        for method_name in dir(self.root):
            method = getattr(self.root, method_name)
            if (method_name not in dir(self)) and (method_name[-2:] != "__"):
                setattr(self, method_name, method)

        self._overrideredirect()

    def _overrideredirect(self) -> None:
        if self.locked:
            return None
        self.locked:bool = True
        # This is needed:
        self.root.update_idletasks()
        # Get the handle of the window
        handle:int = self.root.winfo_id()

        # Get the default display
        display = XOpenDisplay(None)

        # Get the parent of the window
        parent = WINDOW()
        XQueryTree(display, handle, ctypes.byref(WINDOW()),
                   ctypes.byref(parent), ctypes.byref(WINDOW()),
                   ctypes.byref(UINT()))

        # Change the motif hints of the window
        motif_hints = XInternAtom(display, string_to_c("_MOTIF_WM_HINTS"), False)
        hints = HINTS(2, 0, 0, 0, 0)
        XChangeProperty(display, parent, motif_hints, XA_ATOM, 32,
                        PropModeReplace, ctypes.byref(hints), 5)
        # Flush the changes
        XFlush(display)

    def overrideredirect(self, boolean:bool=None) -> None:
        raise RuntimeError("This window must stay as `overrideredirect`")
    wm_overrideredirect = overrideredirect

    def attributes(self, *args) -> None:
        if len(args) == 2:
            if args[0] == "-type":
                raise RuntimeError("You will mess up the work I did.")
            elif args[0] == "-fullscreen":
                value = args[1]
                if isinstance(value, str):
                    value = value.lower() in ("1", "true")
                if value:
                    return self.fullscreen()
                return self.notfullscreen()
        return self.root.attributes(*args)
    wm_attributes = attributes

    def fullscreen(self) -> None:
        if self._fullscreen:
            return None
        self._fullscreen:bool = True
        self.root.attributes("-fullscreen", True)

    def notfullscreen(self) -> None:
        if not self._fullscreen:
            return None
        self._fullscreen:bool = False
        self.root.attributes("-fullscreen", False)

    def toggle_fullscreen(self) -> None:
        if self._fullscreen:
            self.notfullscreen()
        else:
            self.fullscreen()


# Example 1
if __name__ == "__main__":
    root = NoTitlebarTk()
    root.title("AppWindow Test")
    root.geometry("100x100")

    button = tk.Button(root, text="Exit", command=root.destroy)
    button.pack(fill="x")

    button = tk.Button(root, text="Minimise", command=root.iconify)
    button.pack(fill="x")

    button = tk.Button(root, text="Fullscreen", command=root.toggle_fullscreen)
    button.pack(fill="x")

    root.mainloop()


# Example 2
if __name__ == "__main__":
    root = tk.Tk()
    child = NoTitlebarTk(root) # A toplevel
    child.title("AppWindow Test")
    child.geometry("100x100")

    button = tk.Button(child, text="Exit", command=child.destroy)
    button.pack(fill="x")

    button = tk.Button(child, text="Minimise", command=child.iconify)
    button.pack(fill="x")

    button = tk.Button(child, text="Fullscreen", command=child.toggle_fullscreen)
    button.pack(fill="x")

    root.mainloop()


"""
UCHAR_PTR = ctypes.POINTER(UCHAR)


def uchar_ptr(data:tuple[int]) -> PTR:
    data = (UCHAR * len(data))(*data)
    return data

class EVENT(ctypes.Structure):
    _fields_ = [("no idea what this is", LONG*24)]
EVENT_PTR = ctypes.POINTER(EVENT)


XDefaultScreen = libx11.XDefaultScreen
XDefaultScreen.argtypes = (DISPLAY, )
XDefaultScreen.restype = SCREEN

XRootWindow = libx11.XRootWindow
XRootWindow.argtypes = (DISPLAY, SCREEN)
XRootWindow.restype = WINDOW
XRootWindow.errcheck = _errcheck_not_zero

XBlackPixel = libx11.XBlackPixel
XBlackPixel.argtypes = (DISPLAY, SCREEN)
XBlackPixel.restype = ULONG

XWhitePixel = libx11.XWhitePixel
XWhitePixel.argtypes = (DISPLAY, SCREEN)
XWhitePixel.restype = ULONG

XCreateSimpleWindow = libx11.XCreateSimpleWindow
XCreateSimpleWindow.argtypes = (DISPLAY, WINDOW, INT, INT, UINT, UINT, UINT,
                                ULONG)
XCreateSimpleWindow.restype = SCREEN
XCreateSimpleWindow.errcheck = _errcheck_not_zero

XMapWindow = libx11.XMapWindow
XMapWindow.argtypes = (DISPLAY, WINDOW)
XMapWindow.restype = INT
XMapWindow.errcheck = _errcheck_not_zero

XNextEvent = libx11.XNextEvent
XNextEvent.argtypes = (DISPLAY, EVENT_PTR)
XNextEvent.restype = INT
XNextEvent.errcheck = _errcheck_not_zero


root = tk.Tk()
root.update_idletasks()
handle = root.winfo_id()

display = XOpenDisplay(None)

parent = WINDOW()
XQueryTree(display, handle, ctypes.byref(WINDOW()), ctypes.byref(parent),
           ctypes.byref(WINDOW()), ctypes.byref(UINT()))

motif_hints = XInternAtom(display, string_to_c("_MOTIF_WM_HINTS"), False)
hints = uchar_ptr((2, 0, 0, 0, 0))
XChangeProperty(display, parent, motif_hints, XA_ATOM, 32, PropModeReplace,
                hints, 5)

XFlush(display)
"""
