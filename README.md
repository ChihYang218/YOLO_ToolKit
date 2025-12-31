# YOLO ToolKit 🚀

**YOLO ToolKit** 是一個專為 YOLO 系列模型 (YOLOv5, v8, v10, v11 等) 訓練流程打造的實用工具箱。
這個專案旨在解決在資料集處理、標註轉換及訓練過程中常見的繁瑣問題，讓開發者能更專注於模型優化本身。

## 📂 專案結構

```text
YOLO_ToolKit/
├── README.md           # 專案說明文件
├── remap_classes.py    # 工具 1：類別 ID 重映射工具
├── merge_datasets.py   # 工具 2：資料集多合一與自動分配器
└── (更多工具開發中...)
```

---

## 🛠️ 目前收錄工具

### 1. `remap_classes.py` - 標註類別 ID 重映射器

**功能描述：**
當你需要合併不同的資料集，或者發現標註時 ID 順序錯誤時，這個腳本可以幫你批次修改所有 `.txt` 標註檔中的 class ID。

**核心特色：**
* **安全優先 (Dry Run)**：預設開啟「模擬模式」，只顯示會修改哪些內容，不直接更動檔案。
* **智慧路徑偵測**：自動識別常見的 YOLO 資料夾結構（如 `labels/train`）。
* **支援多子集**：一次處理 `train`, `val`, `test` 等資料夾。

#### 📖 使用方法

1.  **設定參數**：打開 `remap_classes.py` 修改 `mapping_rules`。
2.  **執行腳本**：
    ```bash
    python remap_classes.py
    ```

---

### 2. `merge_datasets.py` - 資料集多合一與自動分配器

**功能描述：**
負責將多個散落在不同路徑的 YOLO 資料集（Source）合併成一個標準化的新資料集（Target）。程式會自動收集所有圖片與標籤，並依照你指定的比例重新分配給 `train`, `valid`, `test`。

**核心特色：**
* **自動防撞名**：不同資料集有相同檔名（如 `001.jpg`）時，自動加上前綴（如 `ds0_001.jpg`）避免覆蓋。
* **彈性比例分配**：可自訂訓練/驗證/測試集比例（例如：80% Train, 20% Valid, 0% Test）。
* **標準化輸出**：自動建立符合 YOLO 訓練標準的 `images` 與 `labels` 資料夾結構。
* **智慧搜尋**：自動遞迴搜尋來源資料夾內的圖片與對應標籤。

#### 📖 使用方法

1.  **開啟腳本設定參數**
    打開 `merge_datasets.py` 修改上方的 Configuration 區塊：

    ```python
    # 1. 來源資料集列表 (支援多個)
    SOURCE_DATASETS = [
        "./dataset_A", 
        "./dataset_B",
    ]

    # 2. 輸出的新資料集路徑
    OUTPUT_DATASET = "./My_Merged_YOLO_Dataset"

    # 3. 資料分配比例 (總和需為 1.0)
    SPLIT_RATIOS = {
        "train": 0.8,   # 80% 訓練
        "valid": 0.2,   # 20% 驗證
        "test":  0.0    # 不產生測試集
    }
    ```

2.  **執行腳本**
    ```bash
    python merge_datasets.py
    ```

3.  **結果**
    程式會在當前目錄產生 `My_Merged_YOLO_Dataset`，你可以直接將此路徑填入 YOLO 的 `.yaml` 設定檔中開始訓練。

---

## 📋 系統需求 (Prerequisites)

* Python 3.6+
* 標準函式庫 (無需安裝額外 pip 套件)：
    * `os`, `glob`, `shutil`, `random`, `pathlib`

## 📝 License

This project is licensed under the MIT License.