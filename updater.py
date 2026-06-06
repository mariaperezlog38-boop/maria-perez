import os
import tempfile
import subprocess
import requests
import hashlib

def _version_tuple(v: str):
    return tuple(int(x) for x in v.split('.') if x.isdigit())

def _sha256_of_file(path: str):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def download_file(url: str, dest_path: str):
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

def run_installer(installer_path: str, silent: bool = True):
    args = [installer_path]
    if silent:
        args += ['/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART', '/SILENTUPDATE']
    # Run installer and wait for it to finish
    try:
        subprocess.run(args, check=False)
    except Exception:
        # Best-effort: if subprocess.run fails, attempt os.startfile
        try:
            os.startfile(installer_path)
        except Exception:
            pass

def check_for_updates(current_version: str, info_url: str) -> tuple[bool, str]:
    """
    Check update metadata at `info_url` (expects JSON with keys: version, url, sha256 optional).
    If newer version found, downloads and runs installer. Returns (updated, message).
    """
    try:
        resp = requests.get(info_url, timeout=20)
        resp.raise_for_status()
        info = resp.json()
    except Exception as e:
        return False, f"Error al consultar actualizaciones: {e}"

    remote_version = info.get('version')
    download_url = info.get('url')
    remote_sha = info.get('sha256')

    if not remote_version or not download_url:
        return False, "Información de actualización incompleta en el servidor."

    try:
        if _version_tuple(remote_version) <= _version_tuple(current_version):
            return False, "Ya tienes la versión más reciente."
    except Exception:
        # fallback string comparison
        if remote_version <= current_version:
            return False, "Ya tienes la versión más reciente."

    # download installer to temp
    fd, tmp_path = tempfile.mkstemp(suffix='.exe')
    os.close(fd)
    try:
        download_file(download_url, tmp_path)
    except Exception as e:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return False, f"Error al descargar instalador: {e}"

    # verify sha256 if provided
    if remote_sha:
        try:
            local_sha = _sha256_of_file(tmp_path)
            if local_sha.lower() != remote_sha.lower():
                os.remove(tmp_path)
                return False, "Checksum no coincide, descarga corrupta."
        except Exception as e:
            return False, f"Error verificando checksum: {e}"

    # run installer
    try:
        run_installer(tmp_path, silent=True)
    except Exception as e:
        return False, f"Error ejecutando instalador: {e}"

    return True, f"Actualización a la versión {remote_version} iniciada."
