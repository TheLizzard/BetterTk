from PIL import Image, ImageTk
import tkinter as tk

from sys import platform
USING_WINDOWS = ("win" in platform)


THEME_OPTIONS = ("light", "dark")

# Unchangable settings:
NUMBER_OF_CUSTOM_BUTTONS = 10 # The number of custom buttons allowed at 1 time
MIN_WIDTH = 240 # The minimum width to hide the dummy window
MIN_HEIGHT = 80 # The minimum height to hide the dummy window


__author__ = "TheLizzard"


class BetterTkSettings:
    def __init__(self, theme="dark", use_unicode=False, snap_threshold=200,
                 separator_size=1):
        self.SNAP_THRESHOLD = snap_threshold
        self.SEPARATOR_SIZE = separator_size

        self.USE_UNICODE = use_unicode

        if theme == "dark":
            self.THEME_BG = "black"
            self.THEME_SEP_COLOUR = "grey"
            self.THEME_HIGHLIGHT = "grey"
            self.THEME_ACTIVE_TITLEBAR_BG = "black"
            self.THEME_ACTIVE_TITLEBAR_FG = "white"
            self.THEME_INACTIVE_TITLEBAR_BG = "grey17"
            self.THEME_INACTIVE_TITLEBAR_FG = "white"
        elif theme == "light":
            self.THEME_BG = "#f0f0ed"
            self.THEME_SEP_COLOUR = "grey"
            self.THEME_HIGHLIGHT = "grey"
            self.THEME_ACTIVE_TITLEBAR_BG = "white"
            self.THEME_ACTIVE_TITLEBAR_FG = "black"
            self.THEME_INACTIVE_TITLEBAR_BG = "grey80"
            self.THEME_INACTIVE_TITLEBAR_FG = "black"
        else:
            raise ValueError("Invalid theme option.")

        # Keep track of the number of BetterTk windows attached to this
        self.bettertk_users = 0

    def started_using(self) -> None:
        self.bettertk_users += 1

    def stoped_using(self) -> None:
        self.bettertk_users -= 1

    def config(self, bg=None, separator_colour=None, hightlight_colour=None,
               active_titlebar_bg=None, active_titlebar_fg=None,
               inactive_titlebar_bg=None, inactive_titlebar_fg=None,
               use_unicode=None, snap_threshold=None, separator_size=None):
        """
        Possible settings:
            bg:str                    The window's background colour
            separator_colour:str      The separator's colour that is between
                                      the titlebar and your widgets
            hightlight_colour:str     The colour of the window's edges
            active_titlebar_bg:str
            active_titlebar_fg:str
            inactive_titlebar_bg:str
            inactive_titlebar_fg:str

            use_unicode:bool          If the window should use unicode
                                      characters for the buttons
            snap_threshold:int        Explained in `BetterTkSettings.__doc__`
            separator_size:int        The separator's height that is between
                                      the titlebar and your widgets
                                      (Best to keep it around 1)

        Notes:
            You can't change the settings while there is a BetterTk window
            attached to this object. If you want to change the background of
            the window use `<BetterTk>.config(bg=...)`
        """
        if self.bettertk_users != 0:
            raise Exception("It isn't safe to change the settings while " \
                            "the window is running.")
        if bg is not None:
            self.THEME_BG = bg
        if separator_colour is not None:
            self.THEME_SEP_COLOUR = separator_colour
        if hightlight_colour is not None:
            self.THEME_HIGHLIGHT = hightlight_colour
        if active_titlebar_bg is not None:
            self.THEME_ACTIVE_TITLEBAR_BG = active_titlebar_bg
        if active_titlebar_fg is not None:
            self.THEME_ACTIVE_TITLEBAR_FG = active_titlebar_fg
        if inactive_titlebar_bg is not None:
            self.THEME_INACTIVE_TITLEBAR_BG = inactive_titlebar_bg
        if inactive_titlebar_fg is not None:
            self.THEME_INACTIVE_TITLEBAR_FG = inactive_titlebar_fg
        if use_unicode is not None:
            self.USE_UNICODE = use_unicode
        if snap_threshold is not None:
            self.SNAP_THRESHOLD = snap_threshold
        if separator_size is not None:
            self.SEPARATOR_SIZE = separator_size
    configure = config


DEFAULT_SETTINGS = BetterTkSettings()
DEFAULT_SETTINGS.started_using()


class CustomButton(tk.Button):
    def __init__(self, master, betterroot, name="#", function=None, column=0):
        self.betterroot = betterroot
        if function is None:
            self.callback = lambda: None
        else:
            self.callback = function
        super().__init__(master, text=name, relief="flat",
                         command=lambda: self.callback())
        self.column = column

        active_bg = self.betterroot.settings.THEME_ACTIVE_TITLEBAR_BG
        active_fg = self.betterroot.settings.THEME_ACTIVE_TITLEBAR_FG
        inactive_bg = self.betterroot.settings.THEME_INACTIVE_TITLEBAR_BG
        inactive_fg = self.betterroot.settings.THEME_INACTIVE_TITLEBAR_FG
        super().config(bg=inactive_bg, activebackground=active_bg,
                       fg=inactive_fg, activeforeground=active_fg)

    def show(self, column=None):
        """
        Shows the button on the screen
        """
        if column is None:
            column = self.column
        super().grid(row=1, column=column)

    def hide(self):
        """
        Hides the button from the screen
        """
        super().grid_forget()


class MinimiseButton(tk.Button):
    def __init__(self, master, betterroot, settings):
        self.betterroot = betterroot
        if settings.USE_UNICODE:
            text = "\u2014"
        else:
            text = "_"
        super().__init__(master, text=text, relief="flat",
                         command=self.minimise_window)

    def minimise_window(self):
        """
        Minimises the window
        """
        self.betterroot.dummy_root.iconify()
        self.betterroot.root.withdraw()

    def show(self, column=NUMBER_OF_CUSTOM_BUTTONS+2):
        """
        Shows the button on the screen
        """
        super().grid(row=1, column=column)

    def hide(self):
        """
        Hides the button from the screen
        """
        super().grid_forget()


class FullScreenButton(tk.Button):
    def __init__(self, master, betterroot, settings):
        self.betterroot = betterroot
        if settings.USE_UNICODE:
            text = "\u2610"
        else:
            text = "[]"
        super().__init__(master, text=text, relief="flat",
                         command=self.toggle_fullscreen)

    def toggle_fullscreen(self, event=None):
        """
        Toggles fullscreen.
        """
        # If it is called from double clicking:
        if event is not None:
            # Make sure that we didn't double click something else
            if not self.betterroot.check_parent_titlebar(event):
                return None
        # If it is the title bar toggle fullscreen:
        if self.betterroot.is_full_screen:
            self.notfullscreen()
        else:
            self.fullscreen()

    def fullscreen(self):
        """
        Switches to full screen.
        """
        if self.betterroot.is_full_screen:
            return "error"
        super().config(command=self.notfullscreen)
        if USING_WINDOWS:
            self.betterroot.root.overrideredirect(False)
        else:
            self.betterroot.root.attributes("-type", "normal")
        self.betterroot.root.attributes("-fullscreen", True)
        self.betterroot.is_full_screen = True

    def notfullscreen(self):
        """
        Switches to back to normal (not full) screen.
        """
        if not self.betterroot.is_full_screen:
            return "error"
        # This toggles between the `fullscreen` and `notfullscreen` methods
        super().config(command=self.fullscreen)
        self.betterroot.root.attributes("-fullscreen", False)
        if USING_WINDOWS:
            self.betterroot.root.overrideredirect(True)
        else:
            self.betterroot.root.attributes("-type", "splash")
        self.betterroot.is_full_screen = False

    def show(self, column=NUMBER_OF_CUSTOM_BUTTONS+3):
        """
        Shows the button on the screen
        """
        super().grid(row=1, column=column)

    def hide(self):
        """
        Hides the button from the screen
        """
        super().grid_forget()


class CloseButton(tk.Button):
    def __init__(self, master, betterroot, settings):
        self.betterroot = betterroot
        if settings.USE_UNICODE:
            text = "\u26cc"
        else:
            text = "X"
        super().__init__(master, text=text, relief="flat",
                         command=self.close_window_protocol)

    def close_window_protocol(self):
        """
        Generates a `WM_DELETE_WINDOW` protocol request.
        If unhandled it will automatically go to `root.destroy()`
        """
        self.betterroot.protocol_generate("WM_DELETE_WINDOW")

    def show(self, column=NUMBER_OF_CUSTOM_BUTTONS+4):
        """
        Shows the button on the screen
        """
        super().grid(row=1, column=column)

    def hide(self):
        """
        Hides the button from the screen
        """
        super().grid_forget()


class BetterTk(tk.Frame):
    """
    Attributes:
        disable_north_west_resizing
        *Buttons*
            minimise_button
            fullscreen_button
            close_button
        *List of all buttons*
            buttons: [minimise_button, fullscreen_button, close_button, ...]

    Methods:
        *List of newly defined methods*
            __init__(master:tk.Misk=None,
                     settings:BetterTkSettings=DEFAULT_SETTINGS, **kwargs)
            protocol_generate(protocol:str) -> None
            topmost() -> None
            #custom_buttons#

        *List of methods that act the same was as tkinter.Tk's methods*
            title
            config
            protocol
            geometry
            focus_force
            destroy
            iconbitmap
            resizable
            attributes
            withdraw
            iconify
            deiconify
            maxsize
            minsize
            state
            report_callback_exception


    The buttons:
        minimise_button:
            minimise_window() => None
            show(column) => None
            hide() => None

        fullscreen_button:
            toggle_fullscreen() => None
            fullscreen() => None
            notfullscreen() => None
            show(column) => None
            hide() => None

        close_button:
            close_window_protocol() => None
            show(column) => None
            hide() => None
        buttons: # It is a list of all of the buttons

    The custom_buttons:
        The proper way of using it is:
            ```
            root = BetterTk()

            root.custom_buttons = {"name": "?",
                                   "function": questionmark_pressed,
                                   "column": 0}
            questionmark_button = root.buttons[-1]

            root.custom_buttons = {"name": "\u2263",
                                   "function": three_lines_pressed,
                                   "column": 2}
            threelines_button = root.buttons[-1]
            ```
        You can call:
            show(column) => None
            hide() => None
    """
    def __init__(self, master:tk.Misc=None,
                 settings:BetterTkSettings=DEFAULT_SETTINGS, **kwargs):
        self.settings = settings
        self.settings.started_using()

        if master is None:
            self.root = tk.Tk(**kwargs)
        elif isinstance(master, tk.Misc):
            self.root = tk.Toplevel(master, **kwargs)
        else:
            raise ValueError("Invalid `master` argument. It must be " \
                             "`None` or a class that inherits from `tk.Misc`")
        self.protocols = {"WM_DELETE_WINDOW": self.destroy}
        self.window_destroyed = False
        self.focused_widget = None
        self.is_full_screen = False

        # Create the dummy window
        self.dummy_root = tk.Toplevel(self.root)
        self.dummy_root.bind("<FocusIn>", self.focus_main)
        self.dummy_root.protocol("WM_DELETE_WINDOW", lambda: self.protocol_generate("WM_DELETE_WINDOW"))
        self.root.update()
        self.dummy_root.after(1, self.dummy_root.geometry, "1x1")
        geometry = "+%i+%i" % (self.root.winfo_x(), self.root.winfo_y())
        if USING_WINDOWS:
            self.root.overrideredirect(True)
        else:
            self.root.attributes("-type", "splash")
        self.geometry(geometry)
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.bind("<FocusIn>", self.window_focused)
        self.root.bind("<FocusOut>", self.window_unfocused)

        # Master frame so that I can add a grey border around the window
        self.master_frame = tk.Frame(self.root, highlightthickness=3, bd=0,
                                     highlightbackground=self.settings.THEME_HIGHLIGHT)
        self.master_frame.pack(expand=True, fill="both")
        self.resizable_window = ResizableWindow(self.master_frame, self)

        # The actual <tk.Frame> where you can put your widgets
        super().__init__(self.master_frame, bd=0, bg=self.settings.THEME_BG,
                         cursor="arrow")
        super().pack(expand=True, side="bottom", fill="both")

        # Set up the title bar frame
        self.title_bar = tk.Frame(self.master_frame, bd=0, cursor="arrow")
        self.title_bar.pack(side="top", fill="x")
        self.draggable_window = DraggableWindow(self.title_bar, self)

        # Add a separator
        self.separator = tk.Frame(self.master_frame, bd=0, cursor="arrow",
                                  bg=self.settings.THEME_SEP_COLOUR,
                                  height=self.settings.SEPARATOR_SIZE)
        self.separator.pack(fill="x")

        # For the titlebar frame
        self.title_frame = tk.Frame(self.title_bar, bd=0)
        self.title_frame.pack(expand=True, side="left", anchor="w", padx=5)

        self.buttons_frame = tk.Frame(self.title_bar, bd=0)
        self.buttons_frame.pack(expand=True, side="right", anchor="e")

        self.title_label = tk.Label(self.title_frame, text="Better Tk",
                                    bg=self.settings.THEME_ACTIVE_TITLEBAR_BG,
                                    fg=self.settings.THEME_ACTIVE_TITLEBAR_FG)
        self.title_label.grid(row=1, column=2, sticky="news")
        self.icon_label = None

        self.minimise_button = MinimiseButton(self.buttons_frame, self,
                                              self.settings)
        self.minimise_button.show()
        self.fullscreen_button = FullScreenButton(self.buttons_frame, self,
                                                  self.settings)
        self.fullscreen_button.show()
        self.close_button = CloseButton(self.buttons_frame, self, self.settings)
        self.close_button.show()

        # When the user double clicks on the titlebar
        self.title_bar.bind_all("<Double-Button-1>",
                                self.fullscreen_button.toggle_fullscreen)
        # When the user middle clicks on the titlebar
        self.title_bar.bind_all("<Button-2>", self.snap_to_side)

        self.buttons = [self.minimise_button, self.fullscreen_button,
                        self.close_button]

        bg = self.settings.THEME_ACTIVE_TITLEBAR_BG
        fg = self.settings.THEME_ACTIVE_TITLEBAR_FG
        for button in self.buttons:
            button.config(activebackground=bg, activeforeground=fg)

        self.window_unfocused()

    def snap_to_side(self, event:tk.Event=None) -> None:
        """
        Moves the window to the side that it's close to.
        """
        if (event is not None) and (not self.check_parent_titlebar(event)):
            return None
        rootx, rooty = self.root.winfo_rootx(), self.root.winfo_rooty()
        width = self.master_frame.winfo_width()
        height = self.master_frame.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        geometry = [rootx, rooty]

        if rootx < self.settings.SNAP_THRESHOLD:
            geometry[0] = 0
        if rooty < self.settings.SNAP_THRESHOLD:
            geometry[1] = 0
        if screen_width - (rootx + width) < self.settings.SNAP_THRESHOLD:
            geometry[0] = screen_width - width
        if screen_height - (rooty + height) < self.settings.SNAP_THRESHOLD:
            geometry[1] = screen_height - height
        self.geometry("+%i+%i" % tuple(geometry))

    def focus_main(self, event:tk.Event=None) -> None:
        """
        When the dummy window gets focused it passes the focus to the main
        window. It also focuses the last focused widget.
        """
        self.root.lift()
        self.root.deiconify()
        if self.focused_widget is None:
            self.root.focus_force()
        else:
            self.focused_widget.focus_force()

    def get_focused_widget(self, event:tk.Event=None) -> None:
        """
        Get's the focused widget so that later we can refocus it.
        """
        widget = self.root.focus_get()
        if widget not in (self.root, self.dummy_root, None):
            self.focused_widget = widget

    def window_focused(self, event:tk.Event=None) -> None:
        self.get_focused_widget()
        self.change_titlebar_bg(self.settings.THEME_ACTIVE_TITLEBAR_BG)
        self.change_titlebar_fg(self.settings.THEME_ACTIVE_TITLEBAR_FG)

    def window_unfocused(self, event:tk.Event=None) -> None:
        self.change_titlebar_bg(self.settings.THEME_INACTIVE_TITLEBAR_BG)
        self.change_titlebar_fg(self.settings.THEME_INACTIVE_TITLEBAR_FG)

    def change_titlebar_bg(self, colour:str) -> None:
        """
        Changes the titlebar's background colour.
        """
        items = (self.title_bar, self.buttons_frame, self.title_label)
        items += tuple(self.buttons)
        if self.icon_label is not None:
            items += (self.icon_label, )
        for item in items:
            item.config(background=colour)

    def change_titlebar_fg(self, colour:str) -> None:
        """
        Changes the titlebar's foreground colour.
        """
        items = (self.title_label, )
        items += tuple(self.buttons)
        for item in items:
            item.config(foreground=colour)

    def protocol_generate(self, protocol:str) -> None:
        """
        Generates a protocol.
        """
        try:
            self.protocols[protocol]()
        except KeyError:
            raise tk.TclError(f"Unknown protocol: \"{protocol}\"")

    def check_parent_titlebar(self, event:tk.Event) -> bool:
        # Get the widget that was pressed:
        widget = event.widget
        # Check if it is part of the title bar or something else
        # It checks its parent and its parent's parent and
        # its parent's parent's parent and ... until it finds
        # whether or not the widget clicked on is the title bar.

        while widget != self.root:
            if widget == self.buttons_frame:
                # Don't allow moving the window when buttons are clicked
                return False
            if widget == self.title_bar:
                return True

            # In some very rare cases `widget` can be `None`
            # And widget.master will throw an error
            if widget is None:
                return False
            widget = widget.master
        return False

    @property
    def custom_buttons(self) -> None:
        return self.buttons[3:]

    @custom_buttons.setter
    def custom_buttons(self, value:dict()) -> None:
        self.custom_button = CustomButton(self.buttons_frame, self, **value)
        self.custom_button.show()
        self.buttons.append(self.custom_button)

    @property
    def disable_north_west_resizing(self) -> None:
        return self.resizable_window.disable_north_west_resizing

    @disable_north_west_resizing.setter
    def disable_north_west_resizing(self, value:bool) -> None:
        self.resizable_window.disable_north_west_resizing = value

    # Normal <tk.Tk> methods:
    def title(self, title:str) -> None:
        # Changing the title of the window
        # Note the name will aways be shows and the window can't be resized
        # to cover it up.
        self.title_label.config(text=title)
        self.root.title(title)
        self.dummy_root.title(title)

    def config(self, bg:str=None, **kwargs) -> None:
        if bg is not None:
            super().config(bg=bg)
        self.root.config(**kwargs)

    def protocol(self, protocol:str, function) -> None:
        """
        Binds a function to a protocol.
        """
        self.protocols.update({protocol: function})

    def topmost(self):
        self.attributes("-topmost", True)

    def geometry(self, geometry:str) -> None:
        if not isinstance(geometry, str):
            raise ValueError("The geometry must be a string")
        if geometry.count("+") not in (0, 2):
            raise ValueError("Invalid geometry: \"%s\"" % repr(geometry)[1:-1])
        dummy_geometry = ""
        if "+" in geometry:
            _, posx, posy = geometry.split("+")
            dummy_geometry = "+%i+%i" % (int(posx) + 75, int(posy) + 20)
        self.root.geometry(geometry)
        self.dummy_root.geometry(dummy_geometry)

    def focus_force(self) -> None:
        self.root.deiconify()
        self.root.focus_force()

    def destroy(self) -> None:
        self.settings.stoped_using()
        if self.window_destroyed:
            super().destroy()
        else:
            self.window_destroyed = True
            self.root.destroy()

    def iconbitmap(self, filename:str) -> None:
        if self.icon_label is not None:
            self.icon_label.destroy()
        self.dummy_root.iconbitmap(filename)
        self.root.lift()
        self.root.update_idletasks()
        size = self.title_frame.winfo_height()
        img = Image.open(filename).resize((size, size), Image.LANCZOS)
        self._tk_icon = ImageTk.PhotoImage(img, master=self.root)
        bg = self.title_label.cget("background")
        self.icon_label = tk.Label(self.title_frame, image=self._tk_icon, bg=bg)
        self.icon_label.grid(row=1, column=1, sticky="news")

    def resizable(self, width:int=None, height:int=None) -> None:
        if width is not None:
            self.resizable_window.resizable_horizontal = width
        if height is not None:
            self.resizable_window.resizable_vertical = height
        return None

    def attributes(self, *args, **kwargs):
        return self.root.attributes(*args, **kwargs)

    def withdraw(self) -> None:
        self.minimise_button.minimise_window()
        self.dummy_root.withdraw()

    def iconify(self) -> None:
        self.dummy_root.iconify()
        self.minimise_button.minimise_window()

    def deiconify(self) -> None:
        self.dummy_root.deiconify()
        self.dummy_root.focus_force()

    def maxsize(self, *args, **kwargs):
        return self.root.maxsize(*args, **kwargs)

    def minsize(self, *args, **kwargs):
        return self.root.minsize(*args, **kwargs)

    def state(self, *args, **kwargs):
        return self.root.state(*args, **kwargs)

    def report_callback_exception(self, *args, **kwargs):
        return self.root.report_callback_exception(*args, **kwargs)


class ResizableWindow:
    def __init__(self, frame, betterroot):
        # Makes the frame resizable like a window
        self.frame = frame
        self.geometry = betterroot.geometry
        self.betterroot = betterroot

        self.sensitivity = 10

        # Variables for resizing:
        self.started_resizing = False
        self.quadrant_resizing = None
        self.disable_north_west_resizing = False
        self.resizable_horizontal = True
        self.resizable_vertical = True

        self.frame.bind("<Enter>", self.change_cursor_resizing)
        self.frame.bind("<Motion>", self.change_cursor_resizing)

        self.frame.bind("<Button-1>", self.mouse_press)
        self.frame.bind("<B1-Motion>", self.mouse_motion)
        self.frame.bind("<ButtonRelease-1>", self.mouse_release)

        self.started_resizing = False

    def mouse_motion(self, event:tk.Event) -> None:
        if self.started_resizing:
            # Must be a list for `self.update_resizing_params` to change it
            new_params = [self.current_width, self.current_height,
                          self.currentx, self.currenty]

            if "e" in self.quadrant_resizing:
                self.update_resizing_params(new_params, self.resize_east())
            if "n" in self.quadrant_resizing:
                self.update_resizing_params(new_params, self.resize_north())
            if "s" in self.quadrant_resizing:
                self.update_resizing_params(new_params, self.resize_south())
            if "w" in self.quadrant_resizing:
                self.update_resizing_params(new_params, self.resize_west())

            self.geometry("%ix%i+%i+%i" % tuple(new_params))

    def mouse_release(self, event):
        self.started_resizing = False

    def mouse_press(self, event:tk.Event) -> None:
        if self.betterroot.is_full_screen:
            return None
        # Resizing the window:
        if event.widget == self.frame:
            self.current_width = self.betterroot.root.winfo_width()
            self.current_height = self.betterroot.root.winfo_height()
            self.currentx = self.betterroot.root.winfo_rootx()
            self.currenty = self.betterroot.root.winfo_rooty()

            quadrant_resizing = self.get_quadrant_resizing()

            if len(quadrant_resizing) > 0:
                self.started_resizing = True
                self.quadrant_resizing = quadrant_resizing

    # For resizing:
    def change_cursor_resizing(self, event) -> None:
        if self.betterroot.is_full_screen:
            self.frame.config(cursor="arrow")
            return None
        if self.started_resizing:
            return None
        quadrant_resizing = self.get_quadrant_resizing()

        if quadrant_resizing == "":
            # Reset the cursor back to "arrow"
            self.frame.config(cursor="arrow")
        elif (quadrant_resizing == "ne") or (quadrant_resizing == "sw"):
            if USING_WINDOWS:
                # Available on Windows
                self.frame.config(cursor="size_ne_sw")
            else:
                # Available on Linux
                if quadrant_resizing == "nw":
                    self.frame.config(cursor="bottom_left_corner")
                else:
                    self.frame.config(cursor="top_right_corner")
        elif (quadrant_resizing == "nw") or (quadrant_resizing == "se"):
            if USING_WINDOWS:
                # Available on Windows
                self.frame.config(cursor="size_nw_se")
            else:
                # Available on Linux
                if quadrant_resizing == "nw":
                    self.frame.config(cursor="top_left_corner")
                else:
                    self.frame.config(cursor="bottom_right_corner")
        elif (quadrant_resizing == "n") or (quadrant_resizing == "s"):
            # Available on Windows/Linux
            self.frame.config(cursor="sb_v_double_arrow")
        elif (quadrant_resizing == "e") or (quadrant_resizing == "w"):
            # Available on Windows/Linux
            self.frame.config(cursor="sb_h_double_arrow")

    def get_quadrant_resizing(self) -> str:
        x, y = self.betterroot.root.winfo_pointerx(), self.betterroot.root.winfo_pointery()
        width, height = self.betterroot.root.winfo_width(), self.betterroot.root.winfo_height()

        x -= self.betterroot.root.winfo_rootx()
        y -= self.betterroot.root.winfo_rooty()
        quadrant_resizing = ""
        if self.resizable_vertical:
            if y + self.sensitivity > height:
                quadrant_resizing += "s"
            if not self.disable_north_west_resizing:
                if y < self.sensitivity:
                    quadrant_resizing += "n"
        if self.resizable_horizontal:
            if x + self.sensitivity > width:
                quadrant_resizing += "e"
            if not self.disable_north_west_resizing:
                if x < self.sensitivity:
                    quadrant_resizing += "w"
        return quadrant_resizing

    def resize_east(self) -> (int, int, int, int):
        x = self.betterroot.root.winfo_pointerx()
        new_width = x - self.currentx
        if new_width < MIN_WIDTH:
            new_width = MIN_WIDTH
        return new_width, None, None, None

    def resize_west(self) -> (int, int, int, int):
        x = self.betterroot.root.winfo_pointerx()
        dx = self.currentx - x
        if dx < MIN_WIDTH - self.current_width:
            dx = MIN_WIDTH - self.current_width
        new_width = self.current_width + dx
        return new_width, None, self.currentx - dx, None

    def resize_south(self) -> (int, int, int, int):
        y = self.betterroot.root.winfo_pointery()
        new_height = y - self.currenty
        if new_height < MIN_HEIGHT:
            new_height = MIN_HEIGHT
        return None, new_height, None, None

    def resize_north(self) -> (int, int, int, int):
        y = self.betterroot.root.winfo_pointery()
        dy = self.currenty - y
        if dy < MIN_HEIGHT - self.current_height:
            dy = MIN_HEIGHT - self.current_height
        new_height = self.current_height + dy
        return None, new_height, None, self.currenty - dy

    def update_resizing_params(self, _list:list, _tuple:tuple):
        """
        Changes each element of `_list` to the corresponding on in `_tuple`
        if that element is not `None`. If it is, ignore it.
        """
        for i in range(len(_tuple)):
            element = _tuple[i]
            if element is not None:
                _list[i] = element


class DraggableWindow:
    def __init__(self, frame, betterroot):
        # Makes the frame draggable like a window
        self.frame = frame
        self.geometry = betterroot.geometry
        self.betterroot = betterroot

        self.dragging = False
        self._offsetx = 0
        self._offsety = 0
        self.frame.bind_all("<Button-1>", self.clickwin)
        self.frame.bind_all("<B1-Motion>", self.dragwin)
        self.frame.bind_all("<ButtonRelease-1>", self.stopdragwin)

    def stopdragwin(self, event):
        self.dragging = False

    def dragwin(self, event):
        if self.dragging:
            x = self.frame.winfo_pointerx() - self._offsetx
            y = self.frame.winfo_pointery() - self._offsety
            self.geometry("+%i+%i" % (x, y))

    def clickwin(self, event):
        if self.betterroot.is_full_screen:
            return None
        if not self.betterroot.check_parent_titlebar(event):
            return None
        self.dragging = True
        self._offsetx = event.widget.winfo_rootx() -\
                        self.betterroot.root.winfo_rootx() + event.x
        self._offsety = event.widget.winfo_rooty() -\
                        self.betterroot.root.winfo_rooty() + event.y


# Example 1:
if __name__ == "__main__":
    root = BetterTk()
    root.title("Example 1")
    root.geometry("400x400")
    # Adding a custom button:
    root.custom_buttons = {"name": "?",
                           "function": lambda: print("\"?\" was pressed"),
                           "column": 0}
    # Adding another custom button:
    root.custom_buttons = {"name": "\u2263",
                           "function": lambda: print("\"\u2263\" was pressed"),
                           "column": 2}
    # root.minimise_button.hide()
    # root.fullscreen_button.hide()
    # root.close_button.hide()
    root.mainloop()


# Example 2
if __name__ == "__main__":
    settings = BetterTkSettings(theme="light")
    settings.config(separator_colour="red", use_unicode=True,
                    active_titlebar_bg="#00ff00",
                    inactive_titlebar_bg="#009900",
                    active_titlebar_fg="white",
                    inactive_titlebar_fg="white",
                    hightlight_colour="cyan")
    root = BetterTk(settings=settings)
    root.geometry("400x400")
    root.title("Example 2")

    # Adding a custom button:
    root.custom_buttons = {"name": "?",
                           "function": lambda: print("\"?\" was pressed"),
                           "column": 0}
    button = root.buttons[-1]
    button.config(command=lambda: print("New command set"))

    label = tk.Label(root, text="This is just to show how to change the " \
                     "window's settings.\nI know it looks bad.", justify="left")
    label.pack(anchor="w")

    root.mainloop()
