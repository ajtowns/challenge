#!/usr/bin/env python

import wx, re

re_fmt = re.compile("\s*%([(]([a-z]+)[)])?([-=+])?(\d+)?(,(\d+))?([ebt])")
re_txt = re.compile("\s*(([^%\t]|%%)+)")

def parsefmt(layout):
    layout = layout.rstrip(" ")
    idx = 0
    res = []
    while idx < len(layout):
        m = re_fmt.match(layout, idx)
        if m is not None:
            name = m.group(2)
            offset = m.group(3)
            width = m.group(4)
            height = m.group(6)
            widget = m.group(7)
        else:
            m = re_txt.match(layout, idx)
            if m is None:
                raise Exception("Format error: %s\n" % (layout[idx:]))
            widget = ":"
            name = m.group(1)
            offset = width = height = None
        res.append( (widget, name, offset, width, height) )
        idx = m.end()
    return res

def horizlayout(parent, layout, *args, **kwargs):
    fmt = parsefmt(layout)
    args = list(args)

    h_sizer = None
    res = None

    names = kwargs.get("names", {})

    for widget, name, offset, width, height in fmt:

        if width is None:
            width = -1
        if height is None:
            height = -1
        sz = wx.Size(int(width), int(height))

        if widget == "e":
            el = wx.TextCtrl(parent, size=sz, value=args.pop(0))
        elif widget == "b":
            el = wx.Button(parent, label=args.pop(0))
        elif widget == "t":
            el = wx.StaticText(parent, label=args.pop(0))
        elif widget == ":":
            el = wx.StaticText(parent, label=name)
            name = None
        else:
            raise Exception("Unhandled widget type")

        if name is not None:
            names[name] = el

        if res is None:
            res = el
        else:
            if h_sizer is None:
                h_sizer = wx.BoxSizer(wx.HORIZONTAL)
                h_sizer.Add(res)
                res = h_sizer
            h_sizer.AddSpacer((5,0))
            h_sizer.Add(el, 1)

    return res, args

class GUIf(wx.Frame):
    def __init__(self, layout, *args):
        wx.Frame.__init__(self, None)
        self.names = {}
        self.layout = layout
        self.args = args

        hlayouts = self.layout.split("\n")
        args = self.args
 
        if len(hlayouts) > 1:
            v_sizer = wx.BoxSizer(wx.VERTICAL)
            for l in hlayouts:
                h, args = horizlayout(self, l, *args, names=self.names)
                v_sizer.Add(h, 0, wx.EXPAND)
            self.SetSizer(v_sizer)
            v_sizer.Fit(self)
            self.SetMinSize(v_sizer.GetMinSize())
        else:
            h, args = horizlayout(self, hlayouts[0], *args, names=self.names)
            self.SetSizer(h)
            h.Fit(self)
            self.SetMinSize(h.GetMinSize())

        if len(args) > 0:
            raise Exception("Leftover arguments (%d)" % len(args))
    
        for name in self.names:
            if hasattr(self, name):
                raise Exception("Invalid widget name %s" % name)
            setattr(self, name, self.names[name])

implicit_app = None

def dispguif(layout, *args, **kwargs):
    global implicit_app

    exiton = (None, wx.EVT_CLOSE)
    if "ExitOn" in kwargs:
        exiton = kwargs.pop("ExitOn")

    if implicit_app is None:
        implicit_app = wx.App()

    frame = GUIf(layout, *args, **kwargs)

    frame.Bind(wx.EVT_CLOSE, lambda e: True)
    if exiton is not None:
        el, evt = exiton
        if el is None:
            el = frame
        else:
            el = frame.names[el]
        el.Bind(evt, lambda e: implicit_app.ExitMainLoop())

    frame.Show()
    implicit_app.SetTopWindow(frame)

    if exiton is not None:
        implicit_app.MainLoop()
        frame.Hide()

    return frame
