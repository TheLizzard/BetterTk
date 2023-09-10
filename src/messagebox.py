from __future__ import annotations
from PIL import ImageTk
import tkinter as tk

try:
    from . import BetterTk
    from .terminaltk.sprites import creator
except ImportError:
    from __init__ import BetterTk
    from terminaltk.sprites import creator


FRAME_KWARGS = dict(bd=0, highlightthickness=0, bg="black")
BUTTON_KWARGS = dict(fg="white", activeforeground="white", bg="black",
                     activebackground="black")

ICONS = creator.SpritesCache(256, 256>>2, 220)


class Popup(BetterTk):
    __slots__ = "root", "image", "tk_image"

    def __init__(self, master:tk.Misc, title:str, icon:str=None):
        super().__init__(master)
        super().title(title)
        self.minimise_button.hide()
        super().resizable(False, False)
        super().protocol("WM_DELETE_WINDOW", self._destroy)
        self.image:Image.Image = self.get_image(icon)
        self.tk_image = ImageTk.PhotoImage(self.image, master=self)
        self.root.iconphoto(False, self.tk_image)
        super().bind("<Escape>", lambda e: self._destroy())
        super().focus_set()
        try:
            super().grab_set()
        except tk.TclError:
            pass

    def get_image(self, icon_name:str) -> Image.Image:
        icon:Image.Image|None = ICONS[icon_name]
        assert icon is not None, f"Unknown icon_name: {icon_name!r}"
        return icon

    def _destroy(self) -> None:
        super().quit()
        super().destroy()

    def mainloop(self) -> YesNoQuestion:
        super().mainloop()
        return self


class Tell(Popup):
    __slots__ = ()

    def __init__(self, master:tk.Misc, title:str, message:str, icon:str=None):
        super().__init__(master, title=title, icon=icon)
        super().bind("<Return>", lambda e: self._destroy())

        left_frame = tk.Frame(self, **FRAME_KWARGS)
        left_frame.pack(side="left", fill="y", expand=True)
        right_frame = tk.Frame(self, **FRAME_KWARGS)
        right_frame.pack(side="right", fill="y", expand=True)

        width, height = self.image.size
        icon = tk.Canvas(left_frame, **FRAME_KWARGS, width=width, height=height)
        icon.pack(side="left", padx=(15, 0))
        icon.create_image(0, 0, anchor="nw", image=self.tk_image)

        text = tk.Label(right_frame, text=message, bg="black", fg="white")
        text.pack(side="top", padx=15, pady=(15, 20))

        ok = tk.Button(right_frame, text="Ok", **BUTTON_KWARGS,
                       width=10, command=self._destroy)
        ok.pack(side="bottom", anchor="e", padx=(0, 15), pady=(0, 20))


class YesNoQuestion(Popup):
    __slots__ = "result"

    def __init__(self, master:tk.Misc, title:str, message:str, icon:str=None):
        self.result:bool = None
        super().__init__(master, title=title, icon=icon)
        super().bind("<Return>", lambda e: self.yes_clicked())

        right_frame = tk.Frame(self, **FRAME_KWARGS)
        right_frame.pack(side="right", fill="both", expand=True)

        b_frame = tk.Frame(right_frame, **FRAME_KWARGS)
        b_frame.pack(side="bottom", anchor="e", expand=True)

        width, height = self.image.size
        icon = tk.Canvas(self, **FRAME_KWARGS, width=width, height=height)
        icon.pack(side="left", padx=(15, 0))
        icon.create_image(0, 0, anchor="nw", image=self.tk_image)

        text = tk.Label(right_frame, text=message, bg="black", fg="white")
        text.pack(side="top", padx=15, pady=15)

        yes = tk.Button(b_frame, text="Yes", **BUTTON_KWARGS,
                        width=7, command=self.yes_clicked)
        no = tk.Button(b_frame, text="No", **BUTTON_KWARGS,
                       width=7, command=self.no_clicked)
        yes.pack(side="left", anchor="e", padx=5, pady=(5, 20))
        no.pack(side="left", anchor="e", padx=15, pady=(5, 20))

    def yes_clicked(self) -> None:
        self.result:bool = True
        self._destroy()

    def no_clicked(self) -> None:
        self.result:bool = False
        self._destroy()

    def get(self) -> None:
        return self.result


def askyesno(master:tk.Misc, **kwargs) -> bool|None:
    return YesNoQuestion(master, **kwargs).mainloop().get()

def tell(master:tk.Misc, **kwargs) -> None:
    Tell(master, **kwargs).mainloop()


if __name__ == "__main__":
    def tksleep(time:int) -> None:
        root.after(time*1000, root.quit)
        root.mainloop()

    root = tk.Tk()
    root.withdraw()

    msg:str = 'Are you sure you want to delete "Hi.txt"?'
    result = tell(root, title="Delete file?", message=msg, icon="warning")
    print(result)

    msg:str = 'Are you sure you want to delete "Hi.txt"?'
    result = tell(root, title="Delete file?", message=msg, icon="warning")
    print(result)