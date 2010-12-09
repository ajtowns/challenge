#!/usr/bin/env python

import wx, re

re_fmt = re.compile("\s*%([(]([a-z]+)[)])?([-=+])?(\d+)?(,(\d+))?([ebt])")

def parsefmt(layout):
    layout = layout.rstrip(" ")
    idx = 0
    res = []
    while idx < len(layout):
        m = re_fmt.match(layout, idx)
        if m is None:
            raise Exception("Format error: %s\n" % (layout[idx:]))
        name = m.group(2)
        offset = m.group(3)
        width = m.group(4)
        height = m.group(6)
        widget = m.group(7)
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
        arg = args.pop(0)

        if width is None:
            width = -1
        if height is None:
            height = -1
        sz = wx.Size(int(width), int(height))

        if widget == "e":
            el = wx.TextCtrl(parent, size=sz, value=arg)
        elif widget == "b":
            el = wx.Button(parent, label=arg)
        elif widget == "t":
            el = wx.StaticText(parent, label=arg)
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

def guif(layout, *args):
    frame = wx.Frame(None)
    names = {}

    """Called when the controls on Window are to be created"""
    hlayouts = layout.split("\n")
 
    if len(hlayouts) > 1:
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        for l in hlayouts:
            h, args = horizlayout(frame, l, *args, names=names)
            v_sizer.Add(h, 0, wx.EXPAND)
        frame.SetSizer(v_sizer)
        v_sizer.Fit(frame)
        frame.SetMinSize(v_sizer.GetMinSize())
    else:
        h, args = horizlayout(frame, hlayouts[0], *args, names=names)
        frame.SetSizer(h)

    return frame, names

