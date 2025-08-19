# 'get_user_profile' fonksiyonunu import ettiğinizden emin olun
from services.github_service import get_user_public_repos, get_user_profile


def list_github_repos(username: str) -> dict:
    """
    Belirtilen bir GitHub kullanıcısının herkese açık repolarını ve ana profil URL'sini listeler.

    Args:
        username (str): Bilgileri alınacak GitHub kullanıcısının adı.
    """
    print(f"TOOL ÇAĞRILDI: list_github_repos, kullanıcı adı: {username}")
    return get_user_public_repos(username=username)



def get_github_user_info(username: str) -> dict:
    """
    Belirtilen GitHub kullanıcısının profil bilgilerini (bio, takipçi sayısı vb.) getirir.

    Args:
        username (str): Bilgileri alınacak GitHub kullanıcısının adı.
    """
    print(f"TOOL ÇAĞRILDI: get_github_user_info, kullanıcı adı: {username}")
    # Hatanın kaynaklandığı yer burası. Yukarıdaki import doğruysa,
    # 'get_user_profile' artık bulunabilir olacaktır.
    return get_user_profile(username=username)