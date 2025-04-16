import tkinter as tk
import tkintermapview

def search_loc():
    location = search_in.get()
    if location:
        map.set_address(location, marker=True)

cordi_map = tk.Tk()
cordi_map.geometry("1500x800")
cordi_map.title("CordiMap")

main = tk.Frame(cordi_map)
main.pack(fill="both", expand=True)

map = tkintermapview.TkinterMapView(main, width=1500, height=760)
map.set_position(16.9083, 122.3941)  
map.set_zoom(8)
map.pack(fill="both", expand=True)

center_marker = tk.Canvas(map.canvas, width=10, height=10, bg="blue", highlightthickness=0)
center_marker.place(relx=0.5, rely=0.5, anchor="center")
center_marker.create_line(0, 5, 10, 5, fill="red", width=2)  
center_marker.create_line(5, 0, 5, 10, fill="red", width=2)  


search_tf = tk.Frame(main, bg="white", width=500, height=50)
search_tf.place(relx=0.65, rely=0.05, anchor="w")  

search_in = tk.Entry(search_tf, font=("Times New Roman", 12), width=50, borderwidth=0, highlightthickness=0, relief="flat")
search_in.pack(side="left", padx=15, pady=5)
search_in.focus_set()

search_btn = tk.Button(
    search_tf, text="Search",
    font=("Times New Roman", 12, "bold italic"),
    command=search_loc, bg="white", activebackground="LightBlue3",
    bd=0,  relief="flat", cursor="hand2"
)
search_btn.pack(side="left", padx=(0, 15), pady=5)

map.canvas.unbind("<MouseWheel>")

# Check coordinates
last_pos = map.get_position()
def check_pos():
    global last_pos
    current = map.get_position()
    if current != last_pos:
        print(f"Map moved to: {current[0]:.4f}, {current[1]:.4f}")
        last_pos = current
    cordi_map.after(300, check_pos)

check_pos()

cordi_map.mainloop()
