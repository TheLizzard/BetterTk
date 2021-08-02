# Mostly taken from: https://stackoverflow.com/a/30819099/11106801
import tkinter as tk

import ctypes
from ctypes.wintypes import BOOL, HWND, LONG

INT = ctypes.c_int
UINT = ctypes.c_uint
LONG_PTR = ctypes.c_uint

def _errcheck_not_zero(value, func, args):
    if value == 0:
        raise ctypes.WinError()
    return args

GetParent = ctypes.windll.user32.GetParent
GetParent.argtypes = (HWND, )
GetParent.restype = HWND
GetParent.errcheck = _errcheck_not_zero

GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
GetWindowLongPtrW.argtypes = (HWND, INT)
GetWindowLongPtrW.restype = LONG_PTR
GetWindowLongPtrW.errcheck = _errcheck_not_zero

SetWindowLongPtrW = ctypes.windll.user32.SetWindowLongPtrW
SetWindowLongPtrW.argtypes = (HWND, INT, LONG_PTR)
SetWindowLongPtrW.restype = LONG_PTR
SetWindowLongPtrW.errcheck = _errcheck_not_zero

GWL_EXSTYLE = -20
WS_EX_APPWINDOW = 0x00040000
WS_EX_TOOLWINDOW = 0x00000080


class NoTitlebarTk(tk.Tk):
    def __init__(self, master=None):
        if master is not None:
            raise NotImplementedError("`master` must be `None` for now.")
        """
        if master is None:
            self.root = tk.Tk()
        elif isinstance(master, tk.Misc):
            self.root = tk.Toplevel(master)
        else:
            raise ValueError("Invalid `master` argument. It must be " \
                             "`None` or a class that inherits from `tk.Misc`")
        """
        super().__init__()
        self.locked = False
        self._fullscreen = False
        self.map_binding = super().bind("<Map>", self._overrideredirect)

    def _overrideredirect(self, event:tk.Event=None) -> None:
        if self.locked:
            return None
        self.locked = True
        if self.map_binding is not None:
            super().unbind("<Map>", self.map_binding)
            self.map_binding = None
        super().overrideredirect(True)
        super().update_idletasks()
        self.hwnd = GetParent(super().winfo_id())
        style = GetWindowLongPtrW(self.hwnd, GWL_EXSTYLE)
        style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
        res = SetWindowLongPtrW(self.hwnd, GWL_EXSTYLE, style)

        # re-assert the new window style
        super().withdraw()
        super().after(10, self.deiconify)
        super().after(20, self.focus_force)
        self.locked = False

    def overrideredirect(self, boolean:bool=None) -> None:
        raise RuntimeError("This window must stay as `overrideredirect`")
    wm_overrideredirect = overrideredirect

    def attributes(self, *args) -> None:
        if (len(args) == 2) and (args[0] == "-fullscreen"):
            value = args[1]
            if isinstance(value, str):
                value = value.lower() in ("1", "true")
            if bool(value):
                return self.fullscreen()
            return self.notfullscreen()
        return super().attributes(*args)
    wm_attributes = attributes

    def iconify(self) -> None:
        super().overrideredirect(False)
        super().iconify()
        super().update()
        self.map_binding = super().bind("<Map>", self._overrideredirect)

    def fullscreen(self) -> None:
        if self._fullscreen:
            return None
        self._fullscreen = True
        super().overrideredirect(False)
        super().attributes("-fullscreen", True)

    def notfullscreen(self) -> None:
        if not self._fullscreen:
            return None
        self._fullscreen = False
        super().attributes("-fullscreen", False)
        self._overrideredirect()
        self.map_binding = super().bind("<Map>", self._overrideredirect)

    def toggle_fullscreen(self) -> None:
        if self._fullscreen:
            self.notfullscreen()
        else:
            self.fullscreen()


if __name__ == "__main__":
    root = NoTitlebarTk()
    root.title("AppWindow Test")
    root.geometry("400x400")

    button = tk.Button(root, text="Exit", command=root.destroy)
    button.pack()

    button = tk.Button(root, text="Minimise", command=root.iconify)
    button.pack()

    button = tk.Button(root, text="Fullscreen", command=root.toggle_fullscreen)
    button.pack()

    root.mainloop()
