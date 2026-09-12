# `ui`

Reusable Tkinter and ttk buttons, widgets, containers, and styles for small
desktop interfaces.

```python
import tkinter as tk
from ui import create_button

root = tk.Tk()
create_button(root, "Close", command=root.destroy).pack(padx=20, pady=20)
root.mainloop()
```

UI factories expect a Tkinter parent. They require a graphical display and
should be created on Tkinter's main thread.
