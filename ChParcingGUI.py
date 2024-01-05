# import sys
# from PyQt5.QtWidgets import *
#
# class DlgMain(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Chords Parcing")
#         self.resize(500, 500)
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     dlgMain = DlgMain()
#     dlgMain.show()
#     sys.exit(app.exec_())

# from tkinter import tix
# 
# def get_sel(*event):
# 	print(tree.hlist.info_selection())
# 	tree.hlist.selection_clear()
# 	tree.hlist.delete_entry('1.1')
# 
# def bcom(*l, **d):
# 	print('bcom', l, d)
# 
# def com(*l, **d):
# 	print('com', l, d)
# 
# Tk = tix.Tk()
# tree = tix.Tree(Tk, browsecmd=bcom, command=com)
# tree.pack()
# tree.hlist.add('1', text='USB', itemtype=tix.TEXT)
# tree.hlist.add('1.1', text='E14-440', itemtype=tix.TEXT)
# tree.hlist.add('1.2', text='E14-140', itemtype=tix.TEXT)
# tree.hlist.add('2', text='LTC', itemtype=tix.TEXT)
# tree.hlist.add('2.1', text='LC-227', itemtype=tix.TEXT)
# tree.hlist.add('2.1.1', text='LC-227K', itemtype=tix.TEXT)
# tree.hlist.add('2.1.2', text='LC-227C', itemtype=tix.TEXT)
# tree.hlist.add('2.2', text='LC-111', itemtype=tix.TEXT)
# tree.autosetmode()
# #tree.close('1')
# #tree.close('2')
# #tree.close('2.1')
# Tk.bind('<d>', get_sel)
# tree.hlist.selection_set('2.1', '2.1.2')
# Tk.mainloop()


from tkinter import tix

class View(object):
    def __init__(self, root):
        self.root = root
        self.makeCheckList()

    def makeCheckList(self):
        self.cl = tix.CheckList(self.root, browsecmd=self.selectItem)
        self.cl.pack()
        self.cl.hlist.add("CL1", text="checklist1")
        self.cl.hlist.add("CL1.Item1", text="subitem1")
        self.cl.hlist.add("CL2", text="checklist2")
        self.cl.hlist.add("CL2.Item1", text="subitem1")
        self.cl.setstatus("CL2", "on")
        self.cl.setstatus("CL2.Item1", "on")
        self.cl.setstatus("CL1", "off")
        self.cl.setstatus("CL1.Item1", "off")
        self.cl.autosetmode()

    def selectItem(self, item):
        print(item, self.cl.getstatus(item))

def main():
    root = tix.Tk()
    view = View(root)
    root.update()
    root.mainloop()

if __name__ == '__main__':
    main()