# Transfer Learning Toolkit 環境建制

### 環境要求
![](https://i.imgur.com/avKmaGY.png)


### 製作 Ubuntu 18.04 開機隨身碟

Ubuntu 版本必須為 18.04，經測試後證實所有的 GTC 2021 開源新軟體都只在 Ubuntu 18.04 有教好的支援，並且 Python 運行環境也以 18.04 版本的原始版本 Python 3.6.9 作為標準。安裝 18.04 可以少走許多彎路。


1.連結到Ubuntu的[官方網站](https://www.ubuntu-tw.org/modules/tinyd0/)，依自己的需要選擇適合的版本，如下圖所示，發行版選擇「Ubuntu桌面版本」，版本選擇「18.04」版，電腦架構選擇「64 位元版本」，點選「開始下載」。

![](https://i.imgur.com/UXEMgk6.png)


2.選擇「儲存檔案」，點選「確定」。

![](https://i.imgur.com/Cfa9PNt.png)


3.連結到Rufus的官方網站。(Rufus 是唯一測試的 USB 製作軟體)

![](https://i.imgur.com/b1Iktla.png)

4.向下移動頁面，點選「Rufus 3.10」。

![](https://i.imgur.com/Hho9aG5.png)

5.下載完成以後，開啟檔案總管，對著下載的檔案連續按兩下按滑鼠左鍵，執行Rufus

![](https://i.imgur.com/zMOdiYJ.png)

6.選擇要製作的 USB 隨身碟

![](https://i.imgur.com/1uWR2ox.png)

7.選擇

![](https://i.imgur.com/8n0kt7g.png)


### 安裝開發環境必須套件
在安裝任何東西之前，首先先打開 terminal 輸入以下指令，更新所有已安裝的套件到最新版本。

> sudo apt-get update
> sudo apt-get upgrade

接著安裝個人常用的基本的套件，以下請自行添增或減少要安裝的套件。(請注意 build-essential 是絕對不可缺少的，因為往後的軟體安裝都需要 gcc 套件)

> sudo apt-get install -y build-essential cmake gfortran git pkg-config
> sudo apt-get install -y python-dev software-properties-common wget vim
> sudo apt-get autoremove

一般來說，build-essential 套件安裝後就會有 gcc，但筆者有過即使安裝後卻不見 gcc 的情形，因此在後面的 Nvidia driver 安裝時失敗。因此必須先輸入以下的指令檢查 gcc 是否正確安裝完畢。

> gcc --version

如果發現 gcc 沒有正確的安裝，可以透過以下指令來安裝(以下是安裝 gcc 10 的指令親測可用，但gcc 版本可以自行調整)


## 安裝 Nvidia 驅動程式 graphic driver / Cuda 11.2 / Cudnn
### ***Cuda 11.2 & graphic driver***
目前大多數深度學習框架支援的 cuda 最新版本為11.2，而 TLT 目前支援的版本是 cuda 11.1。但由於 TLT 是運行在 docker 容器，因此本機的深度學習環境可以與 TLT 抽離互不影響。在此於本機安裝 cuda 11.2 為例，[點此](https://developer.nvidia.com/cuda-11.2.2-download-archive?target_os=Linux&target_arch=x86_64&target_distro=Ubuntu&target_version=1804&target_type=deblocal)至下載連結。

![](https://i.imgur.com/h66SqAT.png)

> wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
> sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
> wget https://developer.download.nvidia.com/compute/cuda/11.2.2/local_installers/cuda-repo-ubuntu1804-11-2-local_11.2.2-460.32.03-1_amd64.deb
> sudo dpkg -i cuda-repo-ubuntu1804-11-2-local_11.2.2-460.32.03-1_amd64.deb
> sudo apt-key add /var/cuda-repo-ubuntu1804-11-2-local/7fa2af80.pub
> sudo apt-get updatesudo apt-get -y install cuda

安裝完畢後在 terminal 輸入指令確定安裝是否正確：
> nvidia-smi

如果正確則應該結果如下圖
![](https://i.imgur.com/foH5v5m.png)

### ***Cudnn 8.1***
請參考此 [Archive](https://developer.nvidia.com/rdp/cudnn-archive) 連結到下載 Cudnn 8.1。

![](https://i.imgur.com/seJdLyB.png)

下載完畢後，請打開 terminal 並且 cd 到下載的資料夾，輸入以下指令：

> tar -xzvf cudnn-11.2-linux-x64-v8.1.1.33.tgz
> sudo cp -P cuda/lib64/* /usr/local/cuda/lib64/
> sudo cp cuda/include/* /usr/local/cuda/include/

最後則將 cuda 相關的路徑加到環境變數當中：

    echo 'export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64"' >> ~/.bashrc
    echo 'export CUDA_HOME=/usr/local/cuda' >> ~/.bashrc
    echo 'export PATH="/usr/local/cuda/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc

### 安裝 virtualenv 與 virtualenbwarpper

    sudo pip3 install virtualenv virtualenvwrapper
    echo "# Virtual Environment Wrapper" >> ~/.bashrc
    echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" >> ~/.bashrc
    echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
    source ~/.bashrc

### ***建立 TLT 虛擬環境***
由於 TLT 官方示範的版本為 3.6.9，正好是 Ubuntu 18.04 的標準 Python3 版本。因此建立的虛擬環境使用的 Python 以系統標準的 Python3 為主，在此建立一個名為 launcher 的虛擬環境。

> mkvirtualenv launcher -p python3

安裝完畢後即可透過 workon 指令來啟用虛擬環境：

![](https://i.imgur.com/hn29RAw.png)

### 安裝 Docker
使用 docker 官方的安裝指示[連結](https://docs.docker.com/engine/install/ubuntu/)，完成安裝。

#### Uninstall old versions
> sudo apt-get remove docker docker-engine docker.io containerd runc
#### Set up the repository
> sudo apt-get update
> 
> sudo apt-get install \
>     apt-transport-https \
>     ca-certificates \
>     curl \
>     gnupg \
>     lsb-release

#### Add Docker’s official GPG key
> curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

> echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

#### Install Docker Engine
> sudo apt-get update
> sudo apt-get install docker-ce docker-ce-cli containerd.io

#### Verify that Docker Engine is installed correctly
> sudo docker run hello-world

完成以後輸入以下指令，確認 docker 的版本資訊
> docker version

![](https://i.imgur.com/R8QJxsI.png)

注意在上圖的最下方的訊息是因為權限問題所產生，若遇到這樣的情形一定要先行解決，否則 TLT 無法順利訓練。依序輸入以下的指令，此[連結](https://forums.developer.nvidia.com/t/error-runnning-the-facenet-notebook/176234/4)為官方論壇之相關議題：

    sudo groupadd docker
    sudo usermod -aG docker ${USER}
    sudo chmod 666 /var/run/docker.sock
    sudo systemctl restart docker
    sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
    sudo chmod g+rwx "/home/$USER/.docker" -R

成功安裝後再度運行 docker version，因為權限問題出現的訊息應該已經消失。
![](https://i.imgur.com/LQvYocQ.png)

### 安裝 Nvidia Docker 2
參考此[連結](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)安裝 Nvidia Docker 2


### 設置 NGC token 與 API key
請以 Nvidia Developer 的身分登入 [NGC]([https://](https://ngc.nvidia.com/)) ，進行 API key 生成與安裝 NGC CLI，這些設置是在使用 TLT 訓練模型之前必要的步驟。
### 下載 Computer Vision notebooks
按照此[連結](https://ngc.nvidia.com/catalog/resources/nvidia:tlt_cv_samples)，下載 TLT 當中的 CV 筆記本。

### 標籤轉換 Yolo -> Kitti
請使用此[程式碼](https://www.programmersought.com/article/37777249196/)


### 常見之 TLT 問題集
https://forums.developer.nvidia.com/t/tlt-model-issues/173135




