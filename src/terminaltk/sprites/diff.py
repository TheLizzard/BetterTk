from __future__ import annotations
from PIL import Image, ImageTk
from time import perf_counter
import tkinter as tk

from creator import init as old_init
from new_creator import init

ALL_SPRITE_NAMES = ("play", "pause", "stop", "close", "error",
                    "kill", "settings", "warning", "info", "restart")


DIFF_BG = (0,0,0,0) # black
DIFF_BG = (38,43,226,255) # purple
DIFF_BG = (75,0,130,255) # indigo

def compute_diff(old:Image, new:Image) -> Image|None:
    size:int = old.size[0]
    assert old.size == new.size, "SizeError"
    assert size == old.size[1], "SizeError"
    out = Image.new("RGBA", (size,size), DIFF_BG)
    old_pix = old.load()
    new_pix = new.load()
    out_pix = out.load()
    for x in range(size):
        for y in range(size):
            if old_pix[x,y] != new_pix[x,y]:
                out_pix[x,y] = new_pix[x,y]
    return out

def flip_img(img:Image) -> tuple[Image,Image]:
    assert img.size[0] == img.size[1], "SizeError"
    size:int = img.size[0]

    outx = Image.new("RGBA", (size,size))
    outy = Image.new("RGBA", (size,size))
    outx_pix = outx.load()
    outy_pix = outy.load()
    img_pix = img.load()
    for x in range(size):
        for y in range(size):
            outx_pix[size-x-1,y] = img_pix[x,y]
            outy_pix[x,size-y-1] = img_pix[x,y]
    return outx, outy


def img_label(img:Image) -> tk.Label:
    tk_img = ImageTk.PhotoImage(img)
    label = tk.Label(image=tk_img, bg="black")
    label.tk_img = tk_img
    label.bind("<Button-3>", lambda e: img.show())
    return label

def text_label(text:str) -> tk.Label:
    return tk.Label(text=text, bg="black", fg="white")


size:int = 256>>1
start:float = perf_counter()
old = old_init(size=size, compute_size=size<<4)
print(f"[TIME]: Old create took {perf_counter()-start:.4f} sec")
start:float = perf_counter()
new = init(size=size, compute_size=size<<4)
print(f"[TIME]: New create took {perf_counter()-start:.4f} sec")

start:float = perf_counter()
diffs = {}
for name in ALL_SPRITE_NAMES:
    diff = compute_diff(old[name], new[name])
    if diff is not None:
        diffs[name] = diff
print(f"[TIME]: Diff took {perf_counter()-start:.3f} sec")

start:float = perf_counter()
syms = {}
for name in set(new)|set(old):
    symx, symy = flip_img(new[name])
    syms[name] = compute_diff(new[name], symx), compute_diff(new[name], symy)
print(f"[TIME]: Sym diff took {perf_counter()-start:.3f} sec")

if diffs:
    root = tk.Tk()
    root.geometry("+0+0")
    root.resizable(False, False)
    col:int = 0
    for name, diff in diffs.items():
        text_label(name).grid(row=1, column=col, sticky="news")
        img_label(diff).grid(row=2, column=col, sticky="news")
        img_label(new[name]).grid(row=3, column=col, sticky="news")
        img_label(old[name]).grid(row=4, column=col, sticky="news")
        img_label(syms[name][0]).grid(row=5, column=col, sticky="news")
        img_label(syms[name][1]).grid(row=6, column=col, sticky="news")
        col += 1
else:
    print("No diffs")