from ldap3 import Server, Connection, ALL
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)

# LDAP Sunucu Bilgileri
ldap_server = "192.168.134.128"
ldap_username = "Administrator"
ldap_password = "Antalya9!"
ldap_domain = "serkan.com"

# Kullanıcı bilgileri
new_user_dn = "CN=John Doe,OU=Users,DC=serkan,DC=com"  # Kullanıcı DN
new_user_attrs = {
    'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
    'sAMAccountName': 'jdoe',
    'userPrincipalName': 'jdoe@serkan.com',
    'givenName': 'John',
    'sn': 'Doe',
    'displayName': 'John Doe',
    'mail': 'jdoe@serkan.com',
    'userAccountControl': 512  # Hesabı etkinleştir
}

try:
    # LDAP bağlantısı
    server = Server(ldap_server, get_info=ALL,use_ssl=True)
    conn = Connection(server, user=f'{ldap_username}@{ldap_domain}', password=ldap_password)

    # Bağlantı başarılı mı?
    if conn.bind():
        logging.info("LDAP bağlantısı başarılı!")

        # OU=Users,DC=serkan,DC=com mevcut mu kontrol et
        if not conn.search(search_base="DC=serkan,DC=com", search_filter="(ou=Users)", attributes=["ou"]):
            # Eğer OU=Users mevcut değilse, oluşturulmaya çalışılıyor
            conn.add("OU=Users,DC=serkan,DC=com", attributes={'objectClass': ['top', 'organizationalUnit']})
            if conn.result['result'] == 0:
                logging.info("OU=Users başarıyla oluşturuldu.")
            else:
                logging.error(f"OU oluşturulamadı: {conn.result}")
                raise Exception("OU oluşturulamadı.")

        # Kullanıcıyı ekleme işlemi
        conn.add(new_user_dn, attributes=new_user_attrs)
        if conn.result['result'] == 0:
            logging.info(f"Kullanıcı başarıyla oluşturuldu: {new_user_dn}")
        else:
            logging.error(f"Kullanıcı oluşturulamadı: {conn.result}")

    else:
        logging.error("LDAP bağlantısı sağlanamadı!")

except Exception as e:
    logging.error(f"Hata oluştu: {str(e)}")

finally:
    # Bağlantıyı kapat
    if 'conn' in locals() and conn.bound:
        conn.unbind()
