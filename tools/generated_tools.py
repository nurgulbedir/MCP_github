

# Bu kod ToolCreatorEngine tarafından otomatik olarak üretilmiştir.
# DİKKAT: Bu dosya 'tools' klasöründedir.

# Doğru yerden, yani 'services' klasöründen import yapılıyor
# ve fonksiyona 'service_function' diye bir TAKMA AD veriliyor.
from services.generated_services import get_zen as service_function

def get_zen() -> dict:
    """
    Get the Zen of GitHub
    """
    # 'service_function' takma adını kullanarak doğru fonksiyonu çağırıyoruz
    # ve kendi kendini çağırma hatasını (sonsuz döngüyü) engelliyoruz.
    return service_function()


# Bu kod ToolCreatorEngine tarafından otomatik olarak üretilmiştir.
# DİKKAT: Bu dosya 'tools' klasöründedir.

# Doğru yerden, yani 'services' klasöründen import yapılıyor
# ve fonksiyona 'service_function' diye bir TAKMA AD veriliyor.
from services.generated_services import get_users_username_following_target_user as service_function

def get_users_username_following_target_user(target_user: str) -> dict:
    """
    Check if a user follows another user
    """
    # 'service_function' takma adını kullanarak doğru fonksiyonu çağırıyoruz
    # ve kendi kendini çağırma hatasını (sonsuz döngüyü) engelliyoruz.
    return service_function(target_user=target_user)
