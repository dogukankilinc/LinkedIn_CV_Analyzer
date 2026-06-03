import hashlib

def patch_md5():
    # Sadece bir kere yama yap
    if getattr(hashlib, '_md5_patched', False):
        return

    original_md5 = hashlib.md5

    def patched_md5(*args, **kwargs):
        # usedforsecurity parametresini sil
        kwargs.pop("usedforsecurity", None)
        return original_md5(*args, **kwargs)

    hashlib.md5 = patched_md5
    hashlib._md5_patched = True

# Dosya import edildiği an çalışsın
patch_md5()
