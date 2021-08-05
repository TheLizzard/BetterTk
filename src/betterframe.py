import tkinter as tk


FIT_WIDTH = "fit_width"
FIT_HEIGHT = "fit_height"
ALWAYS_FIT_WIDTH = "always_fit_width"   # Not implemented yet
ALWAYS_FIT_HEIGHT = "always_fit_height" # Not implemented yet


class BetterFrame(tk.Frame):
    """
    Also known as `ScrollableFrame`
    There is no way to scroll <tkinter.Frame> so we are
    going to create a canvas and place the frame there.
    Scrolling the canvas will give the illution of scrolling
    the frame
    Partly taken from:
        https://blog.tecladocode.com/tkinter-scrollable-frames/
        https://stackoverflow.com/a/17457843/11106801

    master_frame---------------------------------------------------------
    | dummy_canvas-----------------------------------------  y_scroll--  |
    | | self---------------------------------------------  | |         | |
    | | |                                                | | |         | |
    | | |                                                | | |         | |
    | | |                                                | | |         | |
    | |  ------------------------------------------------  | |         | |
    |  ----------------------------------------------------   ---------  |
    | x_scroll---------------------------------------------              |
    | |                                                    |             |
    |  ----------------------------------------------------              |
     --------------------------------------------------------------------
    """
    def __init__(self, master=None, scroll_speed:int=2, hscroll:bool=False,
                 vscroll:bool=True, bd:int=0, scrollbar_kwargs={},
                 HScrollBarClass=tk.Scrollbar, bg="white",
                 VScrollBarClass=tk.Scrollbar, **kwargs):
        assert isinstance(scroll_speed, int), "`scroll_speed` must be an int"
        self.scroll_speed = scroll_speed

        self.master_frame = tk.Frame(master, bd=bd, bg=bg)
        self.master_frame.grid_rowconfigure(0, weight=1)
        self.master_frame.grid_columnconfigure(0, weight=1)
        self.dummy_canvas = tk.Canvas(self.master_frame, highlightthickness=0,
                                      bd=0, bg=bg, **kwargs)
        super().__init__(self.dummy_canvas)

        # Create the 2 scrollbars
        if vscroll:
            self.v_scrollbar = VScrollBarClass(self.master_frame,
                                               orient="vertical",
                                               command=self.dummy_canvas.yview,
                                               **scrollbar_kwargs)
            self.v_scrollbar.grid(row=0, column=1, sticky="news")
            self.dummy_canvas.configure(yscrollcommand=self.v_scrollbar.set)
        if hscroll:
            self.h_scrollbar = HScrollBarClass(self.master_frame,
                                               orient="horizontal",
                                               command=self.dummy_canvas.xview,
                                               **scrollbar_kwargs)
            self.h_scrollbar.grid(row=1, column=0, sticky="news")
            self.dummy_canvas.configure(xscrollcommand=self.h_scrollbar.set)

        # Bind to the mousewheel scrolling
        self.dummy_canvas.bind_all("<MouseWheel>", self.scrolling_windows,
                                   add=True)
        self.dummy_canvas.bind_all("<Button-4>", self.scrolling_linux, add=True)
        self.dummy_canvas.bind_all("<Button-5>", self.scrolling_linux, add=True)
        self.bind("<Configure>", self.scrollbar_scrolling, add=True)

        # Place `self` inside `dummy_canvas`
        self.dummy_canvas.create_window((0, 0), window=self, anchor="nw")
        # Place `dummy_canvas` inside `master_frame`
        self.dummy_canvas.grid(row=0, column=0, sticky="news")

        self.pack = self.master_frame.pack
        self.grid = self.master_frame.grid
        self.place = self.master_frame.place
        self.pack_forget = self.master_frame.pack_forget
        self.grid_forget = self.master_frame.grid_forget
        self.place_forget = self.master_frame.place_forget

    def scrolling_windows(self, event:tk.Event) -> None:
        assert event.delta != 0, "On Windows, `event.delta` should never be 0"
        y_steps = int(-event.delta/abs(event.delta)*self.scroll_speed)
        self.dummy_canvas.yview_scroll(y_steps, "units")

    def scrolling_linux(self, event:tk.Event) -> None:
        y_steps = self.scroll_speed
        if event.num == 4:
            y_steps *= -1
        self.dummy_canvas.yview_scroll(y_steps, "units")

    def scrollbar_scrolling(self, event:tk.Event) -> None:
        region = list(self.dummy_canvas.bbox("all"))
        region[2] = max(self.dummy_canvas.winfo_width(), region[2])
        region[3] = max(self.dummy_canvas.winfo_height(), region[3])
        self.dummy_canvas.configure(scrollregion=region)

    def resize(self, fit:str=None, height:int=None, width:int=None) -> None:
        """
        Resizes the frame to fit the widgets inside. You must either
        specify (the `fit`) or (the `height` or/and the `width`) parameter.

        Parameters:
            fit:str       `fit` can be either `FIT_WIDTH` or `FIT_HEIGHT`.
                          `FIT_WIDTH` makes sure that the frame's width can
                           fit all of the widgets. `FIT_HEIGHT` is simmilar
            height:int     specifies the height of the frame in pixels
            width:int      specifies the width of the frame in pixels

        If you specify the `fit` argument, the `width` and `height` arguments
        are ignored.

        To do:
            ALWAYS_FIT_WIDTH
            ALWAYS_FIT_HEIGHT
        """
        if fit is None:
            if height is not None:
                self.dummy_canvas.config(height=height)
            if width is not None:
                self.dummy_canvas.config(width=width)
        else:
            if fit == FIT_WIDTH:
                super().update()
                self.dummy_canvas.config(width=super().winfo_width())
            elif fit == FIT_HEIGHT:
                super().update()
                self.dummy_canvas.config(height=super().winfo_height())
            else:
                raise ValueError("Unknow value for the `fit` parameter.")
    fit = resize


# Example 1
if __name__ == "__main__":
    root = tk.Tk()
    frame = BetterFrame(root, width=300, height=200, hscroll=True, vscroll=True)
    frame.pack()

    # Add the widgets in the main diagonal to see the horizontal and
    # vertical scrolling
    for i in range(51):
        label = tk.Label(frame, text=i, anchor="w")
        label.grid(row=i, column=i)

    root.mainloop()


# Example 2
if __name__ == "__main__":
    root = tk.Tk()
    frame = BetterFrame(root, height=200, hscroll=False, vscroll=True)
    frame.pack()

    for i in range(51):
        label = tk.Label(frame, text=f"Label number {i}")
        label.pack(anchor="w")

    # Force the frame to resize to fit all of the widgets:
    frame.resize(FIT_WIDTH)

    root.mainloop()
