import tkinter as tk
import tkinter.font as tkfont

def arrange(root,fontStyle):
    root.title(u"Title")
    root.geometry("400x300")

    titleLabel = tk.Label(text=u'新',font=fontStyle)
    titleLabel.place()
    titleLabel.pack(side='left')

    to_first_btn = tk.Button(root,text=u"最初",height=50,width=5)
    to_first_btn.pack(side='left')
    to_back_btn = tk.Button(root,text=u"<=",height=50,width=10)
    to_forward_btn = tk.Button(root,text=u"=>",height=50,width=10)
    name_btn = tk.Button(root,text=u'name',height=50)
    to_back_btn.pack(side='left')
    to_forward_btn.pack(side='right')
    name_btn.pack()
    
class tk_gui():
    def __init__(self):
        self.root = tk.Tk()
        self.fontStyle = tkfont.Font(size=30)
        
        arrange(self.root,self.fontStyle)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = tk_gui()
    gui.run()