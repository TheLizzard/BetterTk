# Partially taken from: https://stackoverflow.com/a/2400467/11106801
from ctypes.wintypes import BOOL, HWND, LONG
import tkinter as tk
import ctypes

# Defining types
INT = ctypes.c_int
UINT = ctypes.c_uint
LONG_PTR = ctypes.c_long

def _errcheck_not_zero(value, func, args):
    if value == 0:
        raise ctypes.WinError()
    return args

# Defining functions
GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
GetWindowLongPtrW.argtypes = (HWND, INT)
GetWindowLongPtrW.restype = LONG_PTR
GetWindowLongPtrW.errcheck = _errcheck_not_zero

SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW
SetWindowLongPtrW.argtypes = (HWND, INT, LONG_PTR)
SetWindowLongPtrW.restype = LONG_PTR
SetWindowLongPtrW.errcheck = _errcheck_not_zero

SetWindowPos = ctypes.windll.user32.SetWindowPos
SetWindowPos.argtypes = (HWND, HWND, INT, INT, INT, INT, UINT)
SetWindowPos.restype = BOOL
SetWindowPos.errcheck = _errcheck_not_zero

def get_handle(root:tk.Tk) -> int:
    root.update_idletasks()
    # This gets the window's parent same as `ctypes.windll.user32.GetParent`
    return GetWindowLongPtrW(root.winfo_id(), GWLP_HWNDPARENT)


# Constants
GWL_STYLE = -16
GWLP_HWNDPARENT = -8
WS_CAPTION = 0x00C00000
WS_THICKFRAME = 0x00040000
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOZORDER = 0x0004


class NoTitlebarTk:
    def __init__(self, master=None, **kwargs):
        if master is None:
            self.root = tk.Tk(**kwargs)
        elif isinstance(master, tk.Misc):
            self.root = tk.Toplevel(master, **kwargs)
        else:
            raise ValueError("Invalid `master` argument. It must be " \
                             "`None` or a tkinter widget")

        self._fullscreen:bool = False

        for method_name in dir(self.root):
            method = getattr(self.root, method_name)
            if (method_name not in dir(self)) and (method_name[-2:] != "__"):
                setattr(self, method_name, method)

        self._overrideredirect()

    def _overrideredirect(self) -> None:
        self.hwnd:int = get_handle(self.root)
        style:int = GetWindowLongPtrW(self.hwnd, GWL_STYLE)
        style &= ~(WS_CAPTION | WS_THICKFRAME)
        SetWindowLongPtrW(self.hwnd, GWL_STYLE, style)

    def overrideredirect(self, boolean:bool=None) -> None:
        raise RuntimeError("This window must stay as `overrideredirect`")
    wm_overrideredirect = overrideredirect

    def attributes(self, *args) -> None:
        if (len(args) == 2) and (args[0] == "-fullscreen"):
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
    maximised = fullscreen

    def notfullscreen(self) -> None:
        if not self._fullscreen:
            return None
        self._fullscreen:bool = False
        self.root.attributes("-fullscreen", False)
        self._overrideredirect()
    notmaximised = notfullscreen

    def toggle_fullscreen(self) -> None:
        if self._fullscreen:
            self.notfullscreen()
        else:
            self.fullscreen()
    toggle_maximised = toggle_fullscreen

    @property
    def _maximised(self) -> bool:
        """
        There is no difference between fullscreen and maximised window
        on Windows as far as I am aware.
        """
        return self._fullscreen

    def geometry(self, geometry:str=None) -> str:
        if geometry is None:
            return self.root.geometry()

        x = y = width = height = 0
        flags = SWP_NOZORDER
        if "+" in geometry:
            geometry, x, y = geometry.split("+")
            x, y = int(x), int(y)
        else:
            flags |= SWP_NOMOVE
        if "x" in geometry:
            width, height = geometry.split("x")
            width, height = int(width), int(height)
        else:
            flags |= SWP_NOSIZE
        SetWindowPos(self.hwnd, 0, x, y, width, height, flags)


class Draggable(NoTitlebarTk):
    def __init__(self):
        super().__init__()
        self._offsetx = 0
        self._offsety = 0
        self.bind("<Button-1>" ,self.clickwin)
        self.bind("<B1-Motion>", self.dragwin)

    def dragwin(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f"+{x}+{y}")

    def clickwin(self,event):
        self._offsetx = self.winfo_pointerx() - self.winfo_rootx()
        self._offsety = self.winfo_pointery() - self.winfo_rooty()


# Example 1
if __name__ == "__main__":
    root = Draggable()
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
    root = tk.Tk()
    child = Draggable(root) # A toplevel
    child.title("AppWindow Test")
    child.geometry("100x100")

    button = tk.Button(child, text="Exit", command=child.destroy)
    button.pack(fill="x")

    button = tk.Button(child, text="Minimise", command=child.iconify)
    button.pack(fill="x")

    button = tk.Button(child, text="Fullscreen", command=child.toggle_fullscreen)
    button.pack(fill="x")

    root.mainloop()
