import os
import shutil
import zipfile
import logging
import requests
from tqdm import tqdm

MOD_GITHUB_REPOSITORY_ROOT = "https://github.com/IrisuM/ManosabaMod/"
MIRROR_SITE_BASE_URL = ""

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download(url: str, destination: str):
    progress_bar = tqdm(unit='B', unit_scale=True, desc=destination)

    download_request = requests.get(url, stream=True)
    with open(destination, 'wb') as file:
        for chunk in download_request.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                progress_bar.update(1024)
    progress_bar.close()



def download_mod_release(repo_root: str):
    # Arg - repo_root:
    # Saved for later, allowing for an cli arg or config file, to download from github mirrors.
    # Example addr: https://github.com/IrisuM/ManosabaMod/releases/download/v2.0.1/ManosabaMod.zip
    # https://github.com/IrisuM/ManosabaMod/releases/latest/download/ManosabaMod.zip
    logger.info("正在从仓库Releases地址下载最新版mod压缩包.")
    try:
        download(
            url = repo_root + "releases/latest/download/ManosabaMod.zip",
            destination = "ManosabaMod.zip"
        )
    except Exception as exc:
        logger.error("Exception during download: %s", exc)


def check_release_existence(release_zip_path: str):
    # First of all, check if there is actually that zip file.
    if not os.path.exists(release_zip_path):
        # "Mod release didn't exist!"
        return False
    else:
        return True
        

def unzip_mod_release_and_copy(release_zip_path: str):
    try:
        # 2. Then, let's try and unzip the zip file.
        # 2.1 Is is really a working zip file or not
        if not zipfile.is_zipfile(release_zip_path):
            logger.warning("当前位置的ManosabaMod.zip不是有效的压缩包。")
            logger.warning("提示：是不是文件损坏了？请试试看删掉压缩包后重新运行。")
            raise zipfile.BadZipFile("Zipfile check shows that the file's not a zipfile.")

        # 2.2 Opening the zip file.
        with zipfile.ZipFile(release_zip_path) as zipfile_instance:
            # Examining the zipfile, check if files in the archive are corrupt.
            if zipfile_instance.testzip() is not None:
                logger.warning("程序检测到ManosabaMod.zip中有文件损坏了。")
                logger.warning("提示：请试试看删掉压缩包后重新运行一下脚本。")
                raise zipfile.BadZipFile("Archived content has a least one corrupt file.")

            # Extract all, at there.
            zipfile_instance.extractall(path="workdir/", members=zipfile_instance.namelist())

            # And copy'em
            shutil.copytree("workdir/ManosabaMod/", "test_target_dir/", dirs_exist_ok=True)

            logger.info("复制完成。请查看原模组文档确认是否安装起效。")

    except Exception as exc:
        logger.error("Exception during unzipping: %s", exc)
        raise exc



def main():
    try:
        logger.info("manosaba-sherry-mod-installer started.")
        logger.info("检查：ManosabaMod.zip是否已存在")
        release_existence = check_release_existence("ManosabaMod.zip")
        if release_existence:
            logger.debug("存在，不再下载。")
        else:
            logger.debug("不存在，从源仓库下载。")
            logger.debug("默认采用镜像站的设计不够安全，目前暂时加入。")
            download_mod_release(MIRROR_SITE_BASE_URL + MOD_GITHUB_REPOSITORY_ROOT)

        unzip_mod_release_and_copy("ManosabaMod.zip")
        input("安装脚本正常执行完毕，按回车结束脚本。")

    except Exception:
        logger.error("脚本执行遇到问题! 脚本退出。")
        input("按回车结束脚本。")

if __name__ == "__main__":
    main()
