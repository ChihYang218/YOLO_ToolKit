import os
import glob

# ================= configuration =================

# 1. 你的 Dataset 根目錄路徑
dataset_root = "my_yolo_dataset" 

# 2. 修改規則 (字典格式)
# 格式: { 舊 ID: 新 ID }
# 沒寫在這邊的 ID，程式會保持原樣
mapping_rules = {
    0: 2,    # 把 0 改成 2
    1: 5,    # 把 1 改成 5
    3: 0,    # 把 3 改成 0
    # 2 不改，所以不寫
    # ...以此類推
}

# 3. 安全開關 (True = 只顯示不修改, False = 真的修改檔案)
# 建議第一次先設為 True，確認 Log 沒問題後改成 False
DRY_RUN = True 

# =================================================

def process_file(file_path, mapping_rules):
    """讀取單一檔案並依規則修改"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    file_modified = False
    
    for line in lines:
        parts = line.strip().split()
        if len(parts) > 0:
            try:
                original_id = int(parts[0])
                # 檢查是否在規則中
                if original_id in mapping_rules:
                    new_id = mapping_rules[original_id]
                    # 修改該行的第一個數字
                    parts[0] = str(new_id)
                    file_modified = True
            except ValueError:
                pass # 如果第一項不是數字(例如 classes.txt)，跳過
        
        new_lines.append(" ".join(parts) + "\n")
    
    # 寫入檔案
    if file_modified:
        if DRY_RUN:
            print(f"  [模擬] 修改: {os.path.basename(file_path)} (內容變更但不存檔)")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"  [寫入] 修改: {os.path.basename(file_path)}")
            
    return file_modified

def find_label_folder(root, subset_name):
    """
    嘗試尋找標註檔的常見路徑結構
    常見結構 1: dataset/labels/train
    常見結構 2: dataset/train/labels
    常見結構 3: dataset/train (直接混在裡面)
    """
    # 定義可能的路徑組合
    potential_paths = [
        os.path.join(root, "labels", subset_name), # YOLOv5/v8 標準結構
        os.path.join(root, subset_name, "labels"), # 有些輸出格式是這樣
        os.path.join(root, subset_name)            # 最單純的結構
    ]
    
    for p in potential_paths:
        if os.path.exists(p) and os.path.isdir(p):
            # 檢查裡面是否有 txt 檔，避免選到空資料夾或只有圖片的資料夾
            if glob.glob(os.path.join(p, "*.txt")):
                return p
    return None

def main():
    # 要偵測的子集名稱 (包含 val 和 valid 兩種常見以此)
    subsets_to_check = ['train', 'valid', 'val', 'test']
    
    print(f"=== 開始處理 YOLO Dataset: {dataset_root} ===")
    if DRY_RUN:
        print("!!! 注意：目前是 DRY_RUN 模式，不會真的修改檔案 !!!\n")

    total_files_modified = 0

    for subset in subsets_to_check:
        target_dir = find_label_folder(dataset_root, subset)
        
        if target_dir:
            print(f"--> 偵測到 {subset} 集，路徑: {target_dir}")
            txt_files = glob.glob(os.path.join(target_dir, "*.txt"))
            
            subset_mod_count = 0
            for txt_file in txt_files:
                # 排除 classes.txt (如果有這個檔的話通常不用改)
                if os.path.basename(txt_file) == "classes.txt":
                    continue
                    
                if process_file(txt_file, mapping_rules):
                    subset_mod_count += 1
            
            print(f"    {subset} 處理完畢，共 {subset_mod_count} 個檔案需修改。\n")
            total_files_modified += subset_mod_count
        else:
            # 找不到該子集，靜默跳過或印出提示
            pass

    print("=========================================")
    print(f"全部完成！總計修改檔案數: {total_files_modified}")
    if DRY_RUN:
        print("請將 DRY_RUN = False 以執行實際寫入。")

if __name__ == "__main__":
    if os.path.exists(dataset_root):
        main()
    else:
        print(f"錯誤：找不到資料夾 '{dataset_root}'")