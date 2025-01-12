import tkinter
import tkinter.font
from tkinter import ttk

tree_columns = ("country", "capital", "currency")
tree_data = [
    ("Argentina",      "Buenos Aires",     "ARS"),
    ]

class MultiColumnListBox(object):
    def __init__(self):
        self.tree = None
        self._setup_widgets()
        self._build_tree()

    def _setup_widgets(self):
        container = ttk.Frame()
        container.pack(fill='both', expand=True)

        # XXX Sounds like a good support class would be one for constructing
        #     a treeview with scrollbars.
        self.tree = ttk.Treeview(columns=tree_columns, show="headings")
        verticalScrollBar = ttk.Scrollbar(orient="vertical", command=self.tree.yview)
        horizontalScrollBar = ttk.Scrollbar(orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=verticalScrollBar.set, xscrollcommand=horizontalScrollBar.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        verticalScrollBar.grid(column=1, row=0, sticky='ns', in_=container)
        horizontalScrollBar.grid(column=0, row=1, sticky='ew', in_=container)

        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def _build_tree(self):
        for col in tree_columns:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: MultiColumnListBox.sortby(self.tree, c, 0))
            # XXX tkFont.Font().measure expected args are incorrect according
            #     to the Tk docs
            self.tree.column(col, width=tkinter.font.Font().measure(col.title()))

        for item in tree_data:
            self.tree.insert('', 'end', values=item)

            # adjust columns lenghts if necessary
            for indx, val in enumerate(item):
                ilen = tkinter.font.Font().measure(val)
                if self.tree.column(tree_columns[indx], width=None) < ilen:
                    self.tree.column(tree_columns[indx], width=ilen)
    
    @staticmethod
    def sortby(tree, col, descending):
        """Sort tree contents when a column is clicked on."""
        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        # reorder data
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        # switch the heading so that it will sort in the opposite direction
        tree.heading(col,
            command=lambda col=col: MultiColumnListBox.sortby(tree, col, int(not descending)))

def main():
    root = tkinter.Tk()
    root.wm_title("Multi-Column List")
    root.wm_iconname("mclist")

    app = MultiColumnListBox()
    root.mainloop()

if __name__ == "__main__":
    main()