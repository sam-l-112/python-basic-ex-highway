import cv2  # OpenCV
import requests
import os
from datetime import datetime

# Nextcloud API 設定
NEXTCLOUD_URL = "http://nextcloud.kube.home/remote.php/webdav/"
#NEXTCLOUD_URL = "http://slaanesh.csie.npu.edu.tw:30080/remote.php/webdav/" 
USERNAME = "admin"
PASSWORD = "admin"

# 認證
session = requests.Session()
session.auth = (USERNAME, PASSWORD)

# 確保 Nextcloud 目錄存在
def create_directory_if_not_exists(remote_dir0):
    response0 = session.request(
        'MKCOL',
        f"{NEXTCLOUD_URL}{remote_dir0}"
    )
    if response0.status_code in [201, 405]:  # 201: Created, 405: Already exists
        print(f"目錄存在或已成功創建: {remote_dir0}")
    elif response0.status_code == 409:
        print(f"目錄創建失敗，可能父目錄不存在: {remote_dir0}")
        exit()
    else:
        print(f"目錄創建失敗: {remote_dir0}")
        exit()

# 驗證 Nextcloud 連線
response = session.get(
    f"{NEXTCLOUD_URL}",
    headers={"OCS-APIRequest": "true"}
)

if response.status_code == 200:
    print("Nextcloud 認證成功")
else:
    print("Nextcloud 認證失敗")
    exit()

# 設定目錄
remote_dir = "captured_videos/"
create_directory_if_not_exists(remote_dir)

# 設定攝影機串流來源
# url = 'https://cctv.bote.gov.taipei:8501/mjpeg/303' #萬華區-國稅局
# url = 'https://youtu.be/FI9n-Dt_k7g' #youtube is SpaceX
#url = 'https://tw.live/cam/?id=RIGDDp48PsU #澎湖機場
#url = 'https://trafficvideo2.tainan.gov.tw/0bc135e5' #台南市交通監視器
url = 'https://cctvc.freeway.gov.tw/abs2mjpg/bmjpg?camera=407' #國道1號407
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("無法打開相機")
    exit()

# 設定影片參數
FPS = 10  # 影片的幀率
FRAME_WIDTH = int(cap.get(3))  # 取得畫面寬度
FRAME_HEIGHT = int(cap.get(4))  # 取得畫面高度
VIDEO_DURATION = 60  # 每段影片的長度 (秒)
VIDEO_FRAMES = FPS * VIDEO_DURATION  # 計算一段影片需要的總幀數

# 本地存儲的臨時資料夾
TEMP_DIR = "temp_videos"
os.makedirs(TEMP_DIR, exist_ok=True)

print("按下 'q' 鍵退出")

# 設定影片寫入器
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#timestamp = 
local_video_path = os.path.join(TEMP_DIR, f"video_{timestamp}.mp4")
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 設定影片格式
out = cv2.VideoWriter(local_video_path, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

frame_count = 0  # 計算當前錄製幀數

while True:
    ret, frame = cap.read()

    if not ret:
        print("無法接收串流幀，嘗試重新連接...")
        cap = cv2.VideoCapture(url)
        continue

    cv2.imshow('studio', frame)
    # out.write(frame)  # 寫入影片檔案
    print(f"frame_count: {frame_count}") # 顯示當前錄製幀數
    frame_count += 1

    # 若影片錄製時間達到設定時間，則存檔並上傳
    if frame_count >= VIDEO_FRAMES:
        out.release()  # 儲存影片

        # 上傳影片到 Nextcloud
        remote_video_path = f"{remote_dir}video_{timestamp}.mp4"
        with open(local_video_path, 'rb') as f:
            response = session.put(
                f"{NEXTCLOUD_URL}{remote_video_path}",
                data=f
            )

        if response.status_code == 201:
            print(f"影片成功上傳至 Nextcloud: {remote_video_path}")
        else:
            print(f"影片上傳失敗: {remote_video_path}")
            print("狀態碼:", response.status_code)

        # 刪除本地影片，避免佔用過多空間
        os.remove(local_video_path)

        # 重新開始新的錄製
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        local_video_path = os.path.join(TEMP_DIR, f"video_{timestamp}.mp4")
        out = cv2.VideoWriter(local_video_path, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))
        frame_count = 0

    # 按 'q' 退出
    if cv2.waitKey(10) == ord('q'):
        break

# 釋放資源
cap.release()
out.release()
cv2.destroyAllWindows()

# 清理臨時資料夾
os.rmdir(TEMP_DIR)
