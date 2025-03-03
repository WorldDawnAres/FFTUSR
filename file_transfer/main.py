import tkinter as tk
from PIL import ImageTk
import os
from file_transfer import config,ui,file_utils

def main():
    root = tk.Tk()
    root.title("文件传输选项")
    root.geometry("650x670")
    try:
        image = config.image
        photo = ImageTk.PhotoImage(image)
        root.iconphoto(True, photo)
    except Exception as e:
        file_utils.update_display(f"Error setting icon: {e}")
    
    root.protocol("WM_DELETE_WINDOW", lambda: ui.on_closing(root))

    ui.create_tkinter_window(root)
    #file_utils.update_display(f"SHARED_FOLDER: {SHARED_FOLDER}")
    #file_utils.update_display(f"TARGET_FOLDER: {TARGET_FOLDER}")
    root.mainloop()

def get_target_subfolders(target_folder_path):
    subfolders = []
    if os.path.isdir(target_folder_path):
        for filename in os.listdir(target_folder_path):
            item_full_path = os.path.join(target_folder_path, filename)
            if os.path.isdir(item_full_path):
                subfolders.append(filename)
    return subfolders

def get_items(folder_path):
    items = []
    if os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            item_full_path = os.path.join(folder_path, filename)
            is_dir = os.path.isdir(item_full_path)
            relative_path = os.path.relpath(item_full_path, config.SHARED_FOLDER)  # 生成相对路径
            items.append({'name': filename, 'path': relative_path, 'is_dir': is_dir})
            #file_utils.update_display(f"Item added: {relative_path}")
    return items

if __name__ == '__main__':
    main()