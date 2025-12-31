# YOLO ToolKit 🚀

**YOLO ToolKit** 是一個專為 YOLO 系列模型 (YOLOv5, v8, v10, v11 等) 訓練流程打造的實用工具箱。
這個專案旨在解決在資料集處理、標註轉換及訓練過程中常見的繁瑣問題，讓開發者能更專注於模型優化本身。

## 📂 專案結構

```text
YOLO_ToolKit/
├── README.md           # 專案說明文件
├── remap_classes.py    # 工具 1：類別 ID 重映射工具
└── (更多工具開發中...)
```

---

## 🛠️ 目前收錄工具

### 1. `remap_classes.py` - 標註類別 ID 重映射器

**功能描述：**
當你需要合併不同的資料集，或者發現標註時 ID 順序錯誤時，這個腳本可以幫你批次修改所有 `.txt` 標註檔中的 class ID。

**核心特色：**
* **安全優先 (Dry Run)**：預設開啟「模擬模式」，只顯示會修改哪些內容，不直接更動檔案，確保安全。
* **智慧路徑偵測**：自動識別常見的 YOLO 資料夾結構（如 `labels/train` 或 `train/labels`），無需手動指定每一層。
* **支援多子集**：一次處理 `train`, `val`, `test` 等資料夾。

#### 📖 使用方法

1.  **開啟腳本設定參數**
    使用編輯器打開 `remap_classes.py`，修改上方的 `configuration` 區塊：

    ```python
    # 1. 設定你的 Dataset 根目錄
    dataset_root = "path/to/your/dataset" 

    # 2. 設定修改規則 { 舊ID: 新ID }
    mapping_rules = {
        0: 2,    # 將原本的 class 0 改為 class 2
        1: 5,    # 將原本的 class 1 改為 class 5
        # 未列出的 ID 將保持原樣
    }

    # 3. 安全開關
    DRY_RUN = True  # True = 僅模擬; False = 實際寫入
    ```

2.  **執行腳本**
    在終端機執行：
    ```bash
    python remap_classes.py
    ```

3.  **確認與寫入**
    * 先檢查 Console 印出的 `[模擬]` 訊息是否符合預期。
    * 確認無誤後，將 `DRY_RUN` 改為 `False` 再執行一次即可完成修改。

---

## 📋 系統需求 (Prerequisites)

* Python 3.6+
* 標準函式庫 (無需安裝額外 pip 套件)：
    * `os`
    * `glob`