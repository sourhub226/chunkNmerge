import math
import subprocess
from customtkinter import *
from tkinter import filedialog
import os
from pathlib import Path

set_appearance_mode("System")
set_default_color_theme("blue")

input_filesize = 0
no_of_parts = 0
input_file = None
read_buffer_size = 1024  # try changing this later
chunk_size = 1
root = CTk()
root.title("chunkNmerge")
# root.geometry(f"{1100}x{580}")


def get_multiplier(size):
    multiple = {
        "Bytes (B)": 1,
        "Kilobytes (KB)": 1024,
        "Megabytes (MB)": 1024*1024,
        "Gigabytes (GB)": 1024*1024*1024
    }
    return multiple.get(size)


def calc_parts():
    global input_filesize, no_of_parts, chunk_size
    print(input_filesize)
    parts_entry.focus()
    print(size_unit.get())
    multiplier = get_multiplier(size_unit.get())
    chunk_size = int(parts_entry.get())*multiplier
    if parts_entry.get():
        no_of_parts = math.ceil(
            input_filesize/chunk_size)
    else:
        no_of_parts = 0
    print(no_of_parts)
    no_of_parts_string.set(f"{no_of_parts} chunks of")


def open_file():
    global input_filesize, input_file
    input_entry.delete(0, "end")
    input_file = (
        filedialog.askopenfile(
            parent=root,
            mode="rb",
            title="Choose a file",
            filetype=[("All files", "*.*")],
        )
    ).name
    input_entry.insert(0, input_file)
    print(f'Input File: {input_file}')
    input_filesize = os.path.getsize(input_file)
    calc_parts()


def split():
    global input_file, read_buffer_size, input_filesize, chunk_size, no_of_parts
    destination = Path(input_file).parent
    file_name = Path(input_file).name
    with open(input_file, 'rb') as file:
        current_chunk_size = 0
        current_chunk_no = 1
        done_reading = False
        while not done_reading:
            status_var.set(f"{current_chunk_no}/{no_of_parts} Splitting...")
            progress_var.set(current_chunk_no/no_of_parts)
            root.update_idletasks()
            with open(f'{destination}\{file_name}.{current_chunk_no}of{no_of_parts}.chk', 'ab') as chunk:
                while True:
                    bfr = file.read(read_buffer_size)
                    if not bfr:
                        done_reading = True
                        break

                    chunk.write(bfr)
                    current_chunk_size += len(bfr)
                    if current_chunk_size + read_buffer_size > chunk_size:
                        current_chunk_no += 1
                        current_chunk_size = 0
                        break
    status_var.set("Spliting complete!")
    progress_var.set(0)


def join():
    global input_file
    destination = Path(input_file).parent

    chunks = list(destination.rglob('*.chk'))
    chunks.sort()
    file_name = os.path.splitext(os.path.splitext(Path(input_file).name)[0])[0]
    print(file_name)
    with open(f'{destination}\merged_{file_name}', 'ab') as file:
        for index, chunk in enumerate(chunks):
            with open(chunk, 'rb') as piece:
                status_var.set(f"{index}/{len(chunks)} Joining...")
                progress_var.set(index/len(chunks))
                root.update_idletasks()
                while True:
                    bfr = piece.read(read_buffer_size)
                    if not bfr:
                        break
                    file.write(bfr)

    status_var.set("Joining complete!")
    progress_var.set(0)


tabview = CTkTabview(root)
tabview.add("Split")
tabview.add("Join")
tabview.pack(expand=1, fill=BOTH)
split_tab = tabview.tab("Split")
join_tab = tabview.tab("Join")


input_frame = CTkFrame(split_tab, fg_color="transparent")
input_frame.pack(expand=1)

input_label = CTkLabel(input_frame, text="Input file")
input_label.pack(side=LEFT, padx=10)
input_entry = CTkEntry(input_frame, width=470)
input_entry.pack(side=LEFT)
input_entry.focus()
input_browse_btn = CTkButton(
    input_frame, text="Browse", width=70, command=open_file)
input_browse_btn.pack(side=LEFT, padx=10)


parts_frame = CTkFrame(split_tab, fg_color="transparent")
parts_frame.pack(expand=1, anchor=N)
no_of_parts_string = StringVar(parts_frame, value="0 chunks of")

CTkLabel(parts_frame, textvariable=no_of_parts_string).pack(side=LEFT, padx=10)
parts_entry = CTkEntry(parts_frame, width=90, justify=CENTER)
parts_entry.insert(0, 100)
parts_entry.pack(side=LEFT)
size_unit = StringVar(value="Megabytes (MB)")
CTkComboBox(parts_frame, values=["Bytes (B)", "Kilobytes (KB)", "Megabytes (MB)", "Gigabytes (GB)"],
            command=lambda _: calc_parts(),
            variable=size_unit).pack(side=LEFT)
CTkLabel(parts_frame, text="each").pack(side=LEFT, padx=10)

split_btn = CTkButton(split_tab, text="Split!", command=split)
split_btn.pack(expand=1, anchor=S)


progress_var = DoubleVar()
progressbar = CTkProgressBar(
    split_tab, variable=progress_var)
progressbar.pack(fill=X, expand=1, anchor=S, padx=10)

status_var = StringVar(value="Ready")
status_label = CTkLabel(split_tab, textvariable=status_var)
status_label.pack(anchor=SW, padx=10)


def callback(P):
    if str.isdigit(P) or P == "":
        return True
    else:
        return False


vcmd = (parts_entry.register(callback))
parts_entry.configure(validate='all', validatecommand=(vcmd, '%P'))
parts_entry.bind("<KeyRelease>", lambda _: calc_parts())

root.mainloop()
