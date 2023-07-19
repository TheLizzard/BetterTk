from __future__ import annotations
from subprocess import Popen, PIPE
from threading import Thread
from time import sleep
import sys
import os

try:
    from bettertk.get_os import IS_WINDOWS, IS_UNIX
    from piper import TmpPipePair
except ImportError:
    from ..bettertk.get_os import IS_WINDOW, IS_UNIX
    from .piper import TmpPipePair


SLAVE_PATH:str = os.path.join(os.path.dirname(__file__), "slave.py")
PING_SIGNAL:bytes = b"="
PONG_SIGNAL:bytes = b"#"
DEBUG_XTERM:bool = False


if IS_WINDOWS:
    raise NotImplementedError("Convert the command bellow to Windows")
elif IS_UNIX:
    KEY_BINDINGS:tuple[str] = (
                                "Ctrl Shift <Key>C: copy-selection(CLIPBOARD)",
                                "Ctrl <Key>V: insert-selection(CLIPBOARD)",
                                "Ctrl <Key>W: quit()",
                                "Ctrl <Key>X: copy-selection(CLIPBOARD)",
                                "Shift <Key>Left: keymap(None)",
                                "Shift <Key>Right: keymap(None)",
                                "Shift <Key>Up: keymap(None)",
                                "Shift <Key>Down: keymap(None)",
                                "Ctrl <Key>KP_Add: larger-vt-font()",
                                "Ctrl <Key>KP_Subtract: smaller-vt-font()",
                                "Ctrl <Key>+: larger-vt-font()",
                                "Ctrl <Key>-: smaller-vt-font()",
                              )
    KEY_BINDINGS:str = r" \n ".join(KEY_BINDINGS)
    XRMS:str = (
                  f"VT100.Translations: #override {KEY_BINDINGS}",
                  # Do NOT delete the next line!
                  #r"VT100.Translations: #override Ctrl Shift <Key>C: copy-selection(CLIPBOARD) \n Ctrl <Key>V: insert-selection(CLIPBOARD) \n Ctrl <Key>W: quit() \n Ctrl <Key>X: copy-selection(CLIPBOARD)",
                  "curses: true",
                  "cutNewline: true",
                  "scrollTtyOutput: false",
                  "autoScrollLock: true",
                  "jumpScroll: false",
                  "scrollKey: true",
                  "omitTranslation: popup-menu",
                  "allowWindowOps: true",
                  # "ScrollBar: on",
                  # "xterm*sixelScrolling: on",
                  # f"xterm*scrollbar.thumb: {THUMB_SPRITE}",
               )
    ARGS:str = "-b 0 -bw 0 -bc +ai -bg black -fg white -fa Monospace " \
               "-fs 12 -cu -sb -rightbar -sl 100000 "
    for XRM in XRMS:
        ARGS += f"-xrm 'xterm*{XRM}' "
    ARGS += f'-e {sys.executable} "{SLAVE_PATH}" "{{}}" "{{}}"'
else:
    raise NotImplementedError("Don't know what this OS is")


class BaseTerminal:
    __slots__ = "proc", "pipe", "running"

    def __init__(self, *, into:int=None) -> None:
        self.running:bool = False
        self.pipe:TmpPipePair = TmpPipePair.from_tmp()
        self.start(*self.pipe.reverse(), into=into)
        assert self.running, "You must call \"self.run(command, env=env)\" " \
                             'inside "self.start"'

    def run(self, command:str, *, env:dict[str,str]) -> None:
        self.proc:Popen = Popen(command, env=env, shell=True, stdout=PIPE,
                                stderr=PIPE)
        self.pipe.start()
        self.running:bool = True

    def wait_ended(self) -> None:
        while self.proc.poll() is None:
            sleep(0.2)

    def close(self, signal:bytes=b"KILL") -> None:
        if signal is not None:
            self.send_signal(signal)
        self.pipe.close()
        self.wait_ended()

    def send_signal(self, signal:bytes) -> None:
        self.pipe.write(signal)

    def ended(self) -> bool:
        return self.proc.poll() is not None

    def start(self, slave2master:str, master2slave:str, *, into:int=None):
        raise NotImplementedError("Override this method, making sure you " \
                                  "call `self.run(command, env=env)` at " \
                                  "the end")

    def resize(self, *, width:int, height:int) -> None:
        raise NotImplementedError('Override this method. Some terminals ' \
                                  'support the "\x1b[4;{height};{width}t" ' \
                                  'ANSI escape code.')


class XTermTerminal(BaseTerminal):
    __slots__ = ()

    def start(self, slave2master:str, master2slave:str, *, into:int=None):
        args:str = ARGS.format(slave2master, master2slave)
        if into is None:
            command:str = f"xterm {args}"
        else:
            command:str = f"xterm -into {into} {args}"
        self.run(command, env=os.environ|dict(force_color_prompt="yes"))
        if DEBUG_XTERM: Thread(target=self.debug_proc_end, daemon=True).start()

    def resize(self, *, width:int, height:int) -> None:
        assert isinstance(width, int), "TypeError"
        assert isinstance(height, int), "TypeError"
        self.pipe.write(encode_print(f"\x1b[4;{height};{width}t"))

    def debug_proc_end(self) -> None:
        self.wait_ended()
        stdout:bytes = self.proc.stdout.read()
        stderr:bytes = self.proc.stderr.read()
        if len(stdout+stderr) > 0:
            print(" stdout ".center(80, "#"))
            print(stdout)
            print(" stderr ".center(80, "#"))
            print(stderr)


if IS_UNIX:
    Terminal:type = XTermTerminal
else:
    raise NotImplementedError

assert issubclass(Terminal, BaseTerminal), "You must subclass BaseTerminal."


def allisinstance(iterable:Iterable, T:type) -> bool:
    return all(map(lambda elem: isinstance(elem, T), iterable))

def _assert_no_null(string:str) -> None:
    assert isinstance(string, str), "TypeError"
    assert "\x00" not in string, "Invalid char in string"

def _encode_args(args:tuple[str]|list[str]) -> bytes:
    assert isinstance(args, tuple|list), "TypeError"
    assert allisinstance(args, str), "TypeError"
    for arg in args: _assert_no_null(arg)
    return "\x00".join(args).encode("utf-8")+b"\x00"

def encode_run(cmd_id:int, args:tuple[str], string_to_print) -> bytes:
    return b"RUN" + cmd_id.to_bytes(2,"big") + len(args).to_bytes(2,"big") + \
           _encode_args(args) + string_to_print.encode("utf-8") + b"\n\x00"

def encode_check_stdout(cmd_id:int, args:tuple[str]) -> bytes:
    return b"CHECK_STDOUT" + cmd_id.to_bytes(2,"big") + \
           len(args).to_bytes(2,"big") + _encode_args(args)

def encode_print(text:str) -> bytes:
    _assert_no_null(text)
    return b"PRINTSTR"+text.encode("utf-8")+b"\x00"


if __name__ == "__main__":
    DEBUG_XTERM:bool = True
    term:Terminal = Terminal()
    term.pipe.write(encode_run(0, ["bash"], " Bash Started ".center(80, "=")))
    term.pipe.write(encode_run(1, ["python3", "/home/thelizzard/.updater.py"], " Updater Started ".center(80, "=")))
    while not term.ended():
        data:bytes = term.pipe.read(100)
        print(data)
    term.pipe.close()
