from __future__ import annotations
import tkinter as tk

try:
    from betterframe import BetterFrame, make_bind_frame
    from betterscrollbar import BetterScrollBarHorizontal
except ImportError:
    from .betterframe import BetterFrame, make_bind_frame
    from .betterscrollbar import BetterScrollBarHorizontal

def round_rectangle(self:tk.Canvas, x1:int, y1:int, x2:int, y2:int, radius:int,
                    **kwargs:dict) -> int:
    # Taken from https://stackoverflow.com/a/44100075/11106801
    points:tuple[int] = (
                         x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius,
                         y1, x2, y1, x2, y1+radius, x2, y1+radius, x2,
                         y2-radius, x2, y2-radius, x2, y2, x2-radius, y2,
                         x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2,
                         x1, y2-radius, x1, y2-radius, x1, y1+radius, x1,
                         y1+radius, x1, y1
                       )
    return self.create_polygon(points, smooth=True, **kwargs)
tk.Canvas.create_round_rectangle = round_rectangle


WIDGET_KWARGS:dict = dict(highlightthickness=0, bd=0, takefocus=False)
NOTCH_BG:str = "#444444"
NOT_DRAG_DIST:int = 10
BUTTON1_TK_STATE:int = 256


class TabNotch(tk.Canvas):
    __slots__ = "text_id", "text", "page", "rrect_id", "width"
    PADX:int = 7

    def __init__(self, master:TabNotches) -> TabNotch:
        super().__init__(master, **WIDGET_KWARGS, height=1, width=1,
                         bg=NOTCH_BG)
        self.text_id:int = super().create_text((0,0), text="", anchor="nw",
                                               fill="white")
        self.rrect_id:int = None
        self.width:int = 0
        self.text:str = None
        super().bind("<Button-1>", lambda e: master.clicked(self), add=True)
        super().bind("<Button-2>", lambda e: master.close(self))

    def rename(self, text:str) -> None:
        if self.text == text:
            return None
        self.text:str = text
        super().itemconfig(self.text_id, text=text)
        x1, y1, x2, y2 = super().bbox(self.text_id)
        width:int = x2-x1
        height:int = y2-y1
        super().moveto(self.text_id, self.PADX, height/2)
        super().config(width=width+2*self.PADX, height=2*height)
        self.width:int = width+2*self.PADX
        if self.rrect_id is not None:
            self.tell_focused()

    def tell_focused(self) -> None:
        if self.rrect_id is not None:
            super().delete(self.rrect_id)
        x1, y1, x2, y2 = super().bbox(self.text_id)
        width:int = x2-x1
        height:int = y2-y1
        points:tuple[int] = (0, 0, width+2*self.PADX, 3*height)
        self.rrect_id:int = super().create_round_rectangle(*points,
                                                           radius=25,
                                                           fill="black")
        super().tag_lower(self.rrect_id)

    def tell_unfocused(self) -> None:
        if self.rrect_id is not None:
            super().delete(self.rrect_id)


class TabNotches(BetterFrame):
    __slots__ = "add_notch", "length", "notebook", "notches", "tmp_notch", \
                "notch_dragging", "dragging", "dragx"

    def __init__(self, notebook:Notebook) -> TabNotches:
        self.notebook:Notebook = notebook
        super().__init__(notebook, bg=NOTCH_BG, hscroll=True, vscroll=False,
                         HScrollBarClass=BetterScrollBarHorizontal,
                         hscrolltop=True, scrollbar_kwargs=dict(width=4))
        self.add_notch:TabNotch = TabNotch(self)
        self.add_notch.grid(row=1, column=1)
        self.add_notch.rename("+")
        self.h_scrollbar.hide:bool = True
        self.notches:list[TabNotch] = []
        self.notch_dragging:bool = None
        self.dragging:bool = False
        height:int = self.add_notch.winfo_reqheight()
        super().resize(height=height)
        self.tmp_notch:tk.Frame = tk.Frame(self, bg=NOTCH_BG, height=height,
                                           highlightthickness=0, bd=0)

        make_bind_frame(self)
        self.bind("<ButtonPress-1>", self.start_dragging, add=True)
        self.bind_all("<Motion>", self.drag, add=True)
        self.bind_all("<ButtonRelease-1>", self.end_dragging, add=True)

    def add(self) -> TabNotch:
        notch:TabNotch = TabNotch(self)
        notch.grid(row=1, column=len(self.notches))
        self.add_notch.grid(row=1, column=len(self.notches)+1)
        self.notches.append(notch)
        return notch

    def clicked(self, notch:TabNotch) -> None:
        if notch == self.add_notch:
            self.notebook.event_generate("<<Tab-Create>>")
        else:
            notch.page.focus()

    def close(self, notch:TabNotch) -> None:
        if notch != self.add_notch:
            notch.page.close()

    def start_dragging(self, event:tk.Event) -> None:
        if not isinstance(event.widget, TabNotch):
            return None
        if event.widget == self.add_notch:
            return None
        self.notch_dragging:TabNotch = event.widget
        self.dragx:int = event.x # event.x_root - event.widget.winfo_rootx()
        return "break"

    def end_dragging(self, event:tk.Event=None) -> str:
        if self.notch_dragging is not None:
            self.tmp_notch.grid_forget()
            self.notch_dragging.grid(row=1, column=self.tmp_notch.idx)
            self.notches[self.tmp_notch.idx] = self.notch_dragging
        self.notch_dragging:TabNotch = None
        self.dragging:bool = False
        return "break"

    def drag(self, event:tk.Event) -> str:
        if self.notch_dragging is None:
            return None
        if not (event.state & BUTTON1_TK_STATE):
            self.end_dragging()
            return None
        if not self.dragging:
            if abs(event.x-self.dragx) < NOT_DRAG_DIST:
                return None
            self.dragging:bool = True
            width:int = self.notch_dragging.winfo_width()
            self.tmp_notch.width=width
            self.tmp_notch.config(width=width)
            idx:int = self.notches.index(self.notch_dragging)
            self.tmp_notch.grid(row=1, column=idx)
            self.tmp_notch.idx:int = idx
            tk.Misc.lift(self.notch_dragging)
            self.notches[idx] = self.tmp_notch

        x:int = event.x_root - super().winfo_rootx()
        idx:int = self.calculate_idx(x-self.dragx)
        self._reshiffle(idx)
        self.notch_dragging.place(x=x-self.dragx, y=0)
        return "break"

    def calculate_idx(self, x:int) -> int:
        total_width:int = 0
        for idx, notch in enumerate(self.notches):
            total_width += notch.width>>1
            if x < total_width:
                return idx
            total_width += (notch.width>>1) + (notch.width&1)
        return len(self.notches)-1

    def _reshiffle(self, idx:int) -> None:
        if idx == self.tmp_notch.idx:
            return None
        self.notches.pop(self.tmp_notch.idx)
        self.notches.insert(idx, self.tmp_notch)
        for i in tuple(range(idx, self.tmp_notch.idx+1)) + \
                 tuple(range(self.tmp_notch.idx, idx+1)):
            self.notches[i].grid(row=1, column=i)
        self.tmp_notch.idx:int = idx


class NotebookPage:
    __slots__ = "notebook", "frame", "notch"

    def __init__(self, notebook:Notebook, frame:tk.Frame, notch:TabNotch):
        self.notebook:Notebook = notebook
        self.notch:TabNotch = notch
        self.frame:tk.Misc = frame

    def add_frame(self, frame:tk.Frame) -> NotebookPage:
        frame.pack(in_=self.frame, fill="both", expand=True)
        #frame.bind("<Control-Key><Tab>", self.notebook.switch_next_tab)
        frame.bind("<Control-Tab>", self.notebook.switch_next_tab)
        frame.bind("<Control-ISO_Left_Tab>", self.notebook.switch_prev_tab)
        return self

    def rename(self, title:str) -> NotebookPage:
        self.notch.rename(title)
        return self

    def close(self) -> None:
        self.notebook.tab_destroy(self)

    def _close(self) -> None:
        self.notch.destroy()
        self.frame.destroy()

    def focus(self) -> NotebookPage:
        self.notebook._tab_switch_to(self)
        return self


class Notebook(tk.Frame):
    __slots__ = "pages", "next_id", "curr_page", "notches", "bottom", \
                "on_try_close"

    def __init__(self, master:tk.Misc) -> Notebook:
        self.pages:list[NotebookPage] = []
        self.curr_page:NotebookPage = None
        self.on_try_close = None

        super().__init__(master, **WIDGET_KWARGS, bg="black")
        self.notches:TabNotches = TabNotches(self)
        self.notches.pack(fill="both")
        self.bottom:tk.Frame = tk.Frame(self, **WIDGET_KWARGS, bg="black")
        self.bottom.pack(fill="both", expand=True)

    def tab_create(self) -> NotebookPage:
        notch:TabNotch = self.notches.add()
        notch.rename("Untitled")
        frame:tk.Frame = tk.Frame(self.bottom, **WIDGET_KWARGS, bg="black")
        page:NotebookPage = NotebookPage(self, frame=frame, notch=notch)
        notch.page:NotebookPage = page
        self.pages.append(page)
        return page

    def iter_pages(self) -> Iterator[NotebookPage]:
        for notch in self.notches.notches:
            yield notch.page

    def _tab_switch_to(self, page:NotebookPage) -> None:
        if page == self.curr_page:
            return None
        if self.curr_page is not None:
            self.curr_page.notch.tell_unfocused()
            self.curr_page.frame.pack_forget()
        if page is not None:
            page.frame.pack(fill="both", expand=True)
            page.notch.tell_focused()
        self.curr_page:NotebookPage = page
        super().event_generate("<<Tab-Switched>>")

    def switch_prev_tab(self, event:tk.Event=None) -> None:
        page:NotebookPage = self._switch_next_prev_tab(strides=-1, default=-1)
        if page == self.curr_page:
            page:NotebookPage = None
        self._tab_switch_to(page)

    def switch_next_tab(self, event:tk.Event=None) -> None:
        page:NotebookPage = self._switch_next_prev_tab(strides=+1, default=0)
        if page == self.curr_page:
            page:NotebookPage = None
        self._tab_switch_to(page)

    def _switch_next_prev_tab(self, strides:int, default:int) -> NotebookPage:
        if self.curr_page is None:
            if len(self.pages) == 0:
                return None
            return self.pages[default]
        else:
            idx:int = self.pages.index(self.curr_page) + strides
            return self.pages[idx%len(self.pages)]

    def tab_destroy(self, page:NotebookPage) -> None:
        if self.on_try_close is not None:
            res:bool = self.on_try_close(page)
            if res:
                return None
        if self.curr_page == page:
            self.switch_prev_tab()
        assert self.curr_page != page, "SanityCheck"
        assert self.curr_page in self.pages+[None], "SanityCheck"
        page._close()
        self.pages.remove(page)


if __name__ == "__main__":
    page_to_text = {}

    def add_tab() -> None:
        t = tk.Text(notebook, bg="black", fg="white", insertbackground="white",
                    takefocus=False, highlightthickness=0, bd=0)
        t.insert("end", len(notebook.pages)+1)
        page = notebook.tab_create()
        page_to_text[page] = t
        page.rename(title=f"Tab number {len(notebook.pages)}")
        page.add_frame(t).focus()

    def selected(e) -> None:
        if notebook.curr_page is None:
            return None
        page_to_text[notebook.curr_page].focus_set()

    def on_try_close(page) -> bool:
        for i, p in enumerate(page_to_text.keys()):
            if p == page:
                if i%2:
                    return True
                else:
                    page_to_text.pop(page)
                    return False

    root = tk.Tk()
    notebook = Notebook(root)
    notebook.pack(fill="both", expand=True)
    notebook.on_try_close = on_try_close

    notebook.bind("<<Tab-Create>>", lambda e: add_tab())
    notebook.bind("<<Tab-Switched>>", selected)

    add_tab()
    add_tab()
    add_tab()
    add_tab()
    add_tab()

    nb = notebook
    nts = nb.notches