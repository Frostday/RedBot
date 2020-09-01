import tkinter as tk
import tkinter.font as tkfont
import model

predict = model.run()

root = tk.Tk()

root.title('RedBot')
root.geometry('400x450')

txt = tk.StringVar()

# Chat Window with scroll bar
wrapper1 = tk.LabelFrame(root)
wrapper2 = tk.LabelFrame(root)
canvas = tk.Canvas(wrapper1, bg='white', height=320)
canvas.pack(side="left", expand="yes", fill="both")
scrollbar = tk.Scrollbar(wrapper1, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
chatWindow = tk.Label(canvas, bd=1, textvariable=txt, wraplength=350, justify="left", bg="white")
canvas.create_window((0, 0), window=chatWindow, anchor="nw")
wrapper1.pack(fill="both", expand="yes")
wrapper2.pack(fill="both", expand="yes")

# Message Window
messageWindow = tk.Entry(root)
messageWindow.place(x=128, y=395, height=50, width=250)


def proccess(e):
    inp = e.get()
    e.delete(0, 'end')
    # LOGIC HERE
    result = predict(inp)
    inp = txt.get() + '\n' + 'You:  ' + inp + '\n' + 'RedBot:  ' + result + '\n'
    txt.set(inp)
    canvas.config(scrollregion=canvas.bbox("all"))


# Button to send messages
button = tk.Button(root, text='Send', bg='red', activebackground='yellow', width=12,
                   height=5, font=('Arial', 12), command=(lambda e=messageWindow: proccess(e)))
button.place(x=6, y=395, height=50, width=120)


root.mainloop()