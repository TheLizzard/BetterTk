# Mostly taken from: https://www.tonyobryan.com//index.php?article=9
# Inspired by: https://github.com/EDCD/EDMarketConnector/blob/main/theme.py
from __future__ import annotations
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

def errcheck_not_zero(value, func, args):
    if value == 0:
        args_str = ", ".join(map(str, args))
        raise OSError(f"{func.__name__}({args_str}) => {value}")
    return args

def errcheck_zero(value, func, args):
    if value != 0:
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
XInternAtom.errcheck = errcheck_not_zero

XOpenDisplay = libx11.XOpenDisplay
XOpenDisplay.argtypes = (CHAR_PTR, )
XOpenDisplay.restype = DISPLAY
XOpenDisplay.errcheck = errcheck_not_zero

XChangeProperty = libx11.XChangeProperty
XChangeProperty.argtypes = (DISPLAY, WINDOW, ATOM, ATOM, INT, INT, HINTS_PTR, INT)
XChangeProperty.restype = INT
XChangeProperty.errcheck = errcheck_not_zero

XQueryTree = libx11.XQueryTree
XQueryTree.argtypes = (DISPLAY, WINDOW, WINDOW_PTR, WINDOW_PTR, WINDOW_PTR, UINT_PTR)
XQueryTree.restype = INT
XQueryTree.errcheck = errcheck_not_zero

XFlush = libx11.XFlush
XFlush.argtypes = (DISPLAY, )
XFlush.restype = INT
XFlush.errcheck = errcheck_not_zero

XCloseDisplay = libx11.XCloseDisplay
XCloseDisplay.argtypes = (DISPLAY, )
XCloseDisplay.restype = INT
XCloseDisplay.errcheck = errcheck_zero


_default_root:NoTitlebarTk = None


class NoTitlebarTk:
    def __init__(self, master=None, **kwargs):
        # Figure out the master.
        global _default_root
        if master is None:
            if _default_root is None:
                _default_root = self
            else:
                master = _default_root
                #raise NotImplementedError("You can't have 2 `tk.Tk`s right " \ \
                #                          "now. I am trying to fix that.")
            self.root = tk.Tk(**kwargs)
        elif isinstance(master, (tk.Misc, NoTitlebarTk)):
            self.root = tk.Toplevel(master, **kwargs)
        else:
            raise ValueError("Invalid `master` argument. It must be " \
                             "`None` or a tkinter widget")

        self._fullscreen:bool = False
        self._maximised:bool = False

        dir_self:list = dir(self)
        for method_name in dir(self.root):
            if method_name[-2:] == "__":
                continue
            method = getattr(self.root, method_name)
            if method_name not in dir_self:
                setattr(self, method_name, method)

        self._overrideredirect()

    def _overrideredirect(self) -> None:
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
        hints = HINTS()
        hints.flags = 2 # Specify that we're changing the window decorations.
        hints.decorations = False
        XChangeProperty(display, parent, motif_hints, XA_ATOM, 32,
                        PropModeReplace, ctypes.byref(hints), 5)
        # Flush the changes
        XFlush(display)
        XCloseDisplay(display)

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
        self.notmaximised()
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

    def maximised(self) -> None:
        if self._maximised:
            return None
        self._maximised:bool = True
        self.notfullscreen()
        self.root.attributes("-zoomed", True)

    def notmaximised(self) -> None:
        if not self._maximised:
            return None
        self._maximised:bool = False
        self.root.attributes("-zoomed", False)

    def toggle_maximised(self) -> None:
        if self._maximised:
            self.notmaximised()
        else:
            self.maximised()

    def destroy(self) -> None:
        global _default_root
        if _default_root == self:
            _default_root = None
        self.root.destroy()


# Example 1
if __name__ == "__main__a":
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
if __name__ == "__main__a":
    root = NoTitlebarTk()
    root.geometry("150x150")
    child = NoTitlebarTk(root)
    child.geometry("150x150")

    tk.Label(child, text="Child").pack(fill="x")
    tk.Button(child, text="Exit", command=child.destroy).pack(fill="x")
    tk.Button(child, text="Minimise", command=child.iconify).pack(fill="x")
    tk.Button(child, text="Fullscreen", command=child.toggle_fullscreen).pack(fill="x")

    tk.Label(root, text="Master").pack(fill="x")
    tk.Button(root, text="Exit", command=root.destroy).pack(fill="x")
    tk.Button(root, text="Minimise", command=root.iconify).pack(fill="x")
    tk.Button(root, text="Fullscreen", command=root.toggle_fullscreen).pack(fill="x")

    root.mainloop()


# Test
if __name__ == "__main__a":
    from time import sleep
    for i in range(1000):
        root = NoTitlebarTk()
        root.geometry("10x10+0+0")
        for j in range(1000):
            root.update()
        root.destroy()

        if i % 20 == 0:
            print(f"Passed {i}th test")


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
XRootWindow.errcheck = errcheck_not_zero

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
XCreateSimpleWindow.errcheck = errcheck_not_zero

XMapWindow = libx11.XMapWindow
XMapWindow.argtypes = (DISPLAY, WINDOW)
XMapWindow.restype = INT
XMapWindow.errcheck = errcheck_not_zero

XNextEvent = libx11.XNextEvent
XNextEvent.argtypes = (DISPLAY, EVENT_PTR)
XNextEvent.restype = INT
XNextEvent.errcheck = errcheck_not_zero


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
