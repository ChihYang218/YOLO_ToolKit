import os
import shutil
import random
import glob
from pathlib import Path

# ================= Configuration =================

# 1. 來源資料集列表 (可以放多個路徑)
SOURCE_DATASETS = [
    "./dataset_A", 
    "./dataset_B",
    # "/Users/gelo/Downloads/coco128", 
]

# 2. 輸出的新資料集路徑 (程式會自動建立)
OUTPUT_DATASET = "./My_Merged_YOLO_Dataset"

# 3. 資料分配比例 (總和建議為 1.0，若為 0 則不建立該資料夾)
# 注意：這裡統一使用 train, valid, test 這三個標準名稱
SPLIT_RATIOS = {
    "train": 0.8,   # 80% 訓練集
    "valid": 0.2,   # 20% 驗證集 (YOLO 訓練通常用 valid)
    "test":  0.0    # 0%  測試集 (設為 0 就不會產生資料夾)
}

# 4. 支援的圖片格式
IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}

# =================================================

def collect_image_label_pairs(source_dirs):
    """
    遍歷所有來源資料夾，收集 (圖片路徑, 標籤路徑) 的配對。
    會搜尋 train, val, valid, test 等常見子資料夾。
    """
    pairs = []
    # 常見的來源子資料夾名稱
    subsets_to_scan = ['train', 'val', 'valid', 'test']

    print(f"🔍 開始掃描 {len(source_dirs)} 個來源資料集...")

    for src_idx, root_path in enumerate(source_dirs):
        if not os.path.exists(root_path):
            print(f"⚠️  警告：找不到路徑 '{root_path}'，已跳過。")
            continue

        # 掃描該 root 下可能的子資料夾
        found_in_root = False
        
        # 策略 1: 檢查標準結構 root/train/images 或 root/images/train
        # 為了簡化，我們直接遞迴搜尋所有圖片，只要路徑包含 subsets 關鍵字即可
        
        # 使用 os.walk 遍歷整個目錄樹
        for current_dir, _, files in os.walk(root_path):
            # 判斷當前資料夾是否屬於我們感興趣的子集 (train/val/etc)
            # 或者資料夾結構很淺，直接就在 root 裡
            
            for file in files:
                file_path = Path(current_dir) / file
                if file_path.suffix.lower() in IMG_EXTENSIONS:
                    # 找到圖片，嘗試尋找對應的標籤
                    # 假設標籤在同目錄，或在對應的 labels 目錄
                    # 這裡採用最寬鬆的判定：同檔名(副檔名換成txt)
                    
                    # 尋找 txt 邏輯：
                    # 1. 同目錄下的 .txt
                    # 2. 如果父目錄是 images，則去父目錄/labels 找
                    
                    label_path = None
                    potential_txt = file_path.with_suffix('.txt')
                    
                    # 情況 1: 標籤在同一資料夾
                    if potential_txt.exists():
                        label_path = potential_txt
                    else:
                        # 情況 2: 標準 YOLO 結構 (images/xxx.jpg <-> labels/xxx.txt)
                        # 嘗試將路徑中的 'images' 替換為 'labels'
                        parts = list(file_path.parts)
                        if 'images' in parts:
                            # 替換最後一次出現的 images
                            idx = len(parts) - 1 - parts[::-1].index('images')
                            parts[idx] = 'labels'
                            potential_label_dir = Path(*parts).with_suffix('.txt')
                            if potential_label_dir.exists():
                                label_path = potential_label_dir
                    
                    # 加入列表 (圖片, 標籤, 來源ID)
                    # 來源ID 用來在複製時避免檔名衝突
                    pairs.append({
                        "img": file_path,
                        "lbl": label_path, # 可能為 None
                        "src_id": src_idx
                    })
    
    # 隨機打亂順序
    random.shuffle(pairs)
    return pairs

def create_dirs(base_path, subsets):
    """建立輸出資料夾結構"""
    if os.path.exists(base_path):
        response = input(f"⚠️  輸出資料夾 '{base_path}' 已存在。是否刪除並重建？(y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(base_path)
        else:
            print("程式終止，請更換輸出路徑或手動處理。")
            exit()
            
    os.makedirs(base_path)
    
    active_subsets = []
    for subset_name, ratio in subsets.items():
        if ratio > 0:
            # 建立 train/images, train/labels
            os.makedirs(os.path.join(base_path, subset_name, "images"), exist_ok=True)
            os.makedirs(os.path.join(base_path, subset_name, "labels"), exist_ok=True)
            active_subsets.append(subset_name)
            
    return active_subsets

def copy_files(pairs, output_root, ratios):
    """根據比例分配並複製檔案"""
    total_files = len(pairs)
    if total_files == 0:
        print("❌ 未找到任何圖片檔案。")
        return

    current_idx = 0
    stats = {k: 0 for k in ratios.keys()}
    
    print(f"🚀 開始處理 {total_files} 筆資料...")

    # 計算分割點
    # 例如 100張, 0.7/0.2/0.1 -> split at 70, 90
    thresholds = []
    cumulative = 0
    active_keys = []
    
    for key, ratio in ratios.items():
        if ratio > 0:
            cumulative += ratio
            thresholds.append((cumulative, key))
            active_keys.append(key)
            
    # 開始複製
    for i, item in enumerate(pairs):
        # 決定要分配到哪個集 (train/valid/test)
        progress = (i + 1) / total_files # 0.0 ~ 1.0
        
        target_subset = active_keys[-1] # 預設最後一個
        for threshold, key in thresholds:
            if progress <= threshold:
                target_subset = key
                break
        
        # 建構新檔名 (加入 src_id 以防重複)
        # 例如: src0_filename.jpg
        original_name = item['img'].name
        new_filename = f"ds{item['src_id']}_{original_name}"
        new_txtname = Path(new_filename).with_suffix('.txt').name
        
        # 來源路徑
        src_img = item['img']
        src_lbl = item['lbl']
        
        # 目的路徑
        dst_img = os.path.join(output_root, target_subset, "images", new_filename)
        dst_lbl = os.path.join(output_root, target_subset, "labels", new_txtname)
        
        # 複製圖片
        shutil.copy2(src_img, dst_img)
        
        # 複製標籤 (如果有)
        if src_lbl:
            shutil.copy2(src_lbl, dst_lbl)
        
        stats[target_subset] += 1
        
        if (i + 1) % 100 == 0:
            print(f"   已處理 {i + 1}/{total_files} 檔案...", end='\r')

    print(f"\n✅ 處理完成！")
    print("=" * 30)
    print(f"總計檔案數: {total_files}")
    for k, v in stats.items():
        if SPLIT_RATIOS[k] > 0:
            print(f"  - {k}: {v} 張 ({v/total_files*100:.1f}%)")
    print("=" * 30)
    print(f"📁 新資料集位置: {output_root}")

def main():
    # 檢查比例總和
    total_ratio = sum(SPLIT_RATIOS.values())
    if not (0.99 <= total_ratio <= 1.01):
        print(f"⚠️  警告：比例總和不為 1.0 (目前為 {total_ratio})，請檢查設定。")
    
    # 1. 收集
    pairs = collect_image_label_pairs(SOURCE_DATASETS)
    
    # 2. 建立資料夾
    create_dirs(OUTPUT_DATASET, SPLIT_RATIOS)
    
    # 3. 分配與複製
    copy_files(pairs, OUTPUT_DATASET, SPLIT_RATIOS)

if __name__ == "__main__":
    main()