import cv2  # OpenCV影像存取
import requests #負責與NEXTCLOUD的進行HTTP請求
import os #處裡本地文件操作
from datetime import datetime #負責獲取當前時間

# Nextcloud API 資訊
NEXTCLOUD_URL = "http://nextcloud.kube.home//remote.php/webdav/"
USERNAME = "admin"
PASSWORD = "admin"

# 認證
session = requests.Session()
session.auth = (USERNAME, PASSWORD)

# 檢查（或創建）Nextcloud中的目錄
def create_directory_if_not_exists(remote_dir0):
    response0 = session.request(
        'MKCOL',  # MKCOL 是 WebDAV 用於建立目錄的 HTTP 方法
        f"{NEXTCLOUD_URL}{remote_dir0}"
    )
    if response0.status_code in [201, 405]:  # 201: Created, 405: Already exists
        print(f"目錄存在或已成功創建: {remote_dir0}")
    elif response0.status_code == 409:  #如果狀態碼是 409（衝突，例如父目錄不存在），則報錯並退出程式。
        print(f"目錄創建失敗，可能父目錄不存在: {remote_dir0}")
        print("狀態碼:", response0.status_code)
        exit()
    else:
        print(f"目錄創建失敗: {remote_dir0}")
        print("狀態碼:", response0.status_code)
        exit()

# 檢查認證是否成功，驗證 Nextcloud 連線
response = session.get(
    f"{NEXTCLOUD_URL}",
    headers={"OCS-APIRequest": "true"}
)

if response.status_code == 200: #如果回應狀態碼是 200（成功），則認證成功。
    print("Nextcloud 認證成功")
else:
    print("Nextcloud 認證失敗")
    print("狀態碼:", response.status_code)
    exit()

# 設定目錄，設定要存放影像的 Nextcloud 目錄
remote_dir = "captured_frames/"
create_directory_if_not_exists(remote_dir)

# 串流來源網址
url = 'https://cctvc.freeway.gov.tw/abs2mjpg/bmjpg?camera=407'
cap = cv2.VideoCapture(url)  # 打開視訊串流來源

if not cap.isOpened():
    print("無法打開相機")
    exit()

# 定義本地保存的臨時路徑，創建本地臨時文件夾
TEMP_DIR = "temp_frames"
os.makedirs(TEMP_DIR, exist_ok=True)

#主迴圈：讀取並顯示影像
print("按下 'q' 鍵退出")
commit_timer = 0
while True:
    # 讀取串流幀
    ret, frame = cap.read()

    if not ret:
        print("無法接收串流幀，嘗試重新連接...")
        cap = cv2.VideoCapture(url)
        continue

    # 顯示串流畫面，定期截圖並上傳
    cv2.imshow('studio', frame)
    if commit_timer >= 100: #每 100 幀（大約 3 秒）保存一張圖片，並上傳到 Nextcloud。
        # 保存圖片並上傳到 Nextcloud

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        local_filename = os.path.join(TEMP_DIR, f"frame_{timestamp}.jpg")
        cv2.imwrite(local_filename, frame)  # 保存幀為圖片

        # 構建目錄和文件的遠程名稱，圖片名稱基於時間戳，以防覆蓋舊文件
        remote_filename = f"{remote_dir}frame_{timestamp}.jpg"
        with open(local_filename, 'rb') as f:
            response = session.put(
                f"{NEXTCLOUD_URL}{remote_filename}",
                data=f
            )

        # 確認上傳是否成功
        if response.status_code == 201:
            print(f"圖片成功上傳至Nextcloud: {remote_filename}")
        else:
            print(f"圖片上傳失敗: {remote_filename}")
            print("狀態碼:", response.status_code)
        commit_timer = 0

    # 每秒處理與繪圖刷新
    if cv2.waitKey(10) == ord('q'):
        break
    commit_timer = commit_timer + 1

# 釋放資源
cap.release()
cv2.destroyAllWindows()

# 清理臨時檔案
for file in os.listdir(TEMP_DIR):
    os.remove(os.path.join(TEMP_DIR, file))
os.rmdir(TEMP_DIR)