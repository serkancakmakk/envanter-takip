import logging
from django.shortcuts import get_object_or_404
from ldap3 import Server, Connection, NTLM, ALL # Modellerinizi doğru şekilde ekleyin

logging.basicConfig(level=logging.DEBUG)

import logging
from ldap3 import Server, Connection, ALL, NTLM
from .models import LdapConfig, Company

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)

import logging
from ldap3 import Server, Connection, ALL, NTLM
from .models import Company

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)

from ldap3 import Server, Connection, ALL, NTLM
from django.shortcuts import get_object_or_404
from .models import LdapGroup
import logging

def get_all_ldap_users_and_groups(company):
    from inventory_track.models import LdapUser
    try:
        ldap_config = get_object_or_404(LdapConfig, company=company)
        print('Şirket Bilgileri Alınıyor')  # Şirketin LDAP yapılandırma bilgilerini alıyoruz
        ldap_server = ldap_config.ldap_server
        ldap_username = ldap_config.bind_username
        ldap_password = ldap_config.get_decrypted_password()
        ldap_domain = ldap_config.bind_dn

        # LDAP sunucusuna bağlan
        server = Server(ldap_server, get_info=ALL)
        connection = Connection(
            server,
            user=f"{ldap_domain}\\{ldap_username}",
            password=ldap_password,
            authentication=NTLM,
            auto_bind=True
        )

        if not connection.bound:
            print('LDAP Bağlantısı Sağlanamadı')
            logging.error(f"LDAP bağlantısı başarısız: {connection.last_error}")
            return [], []

        logging.info("LDAP bağlantısı başarılı!")

        # Kullanıcıları çek
        connection.search(
            search_base=f'dc={ldap_domain},dc=com',  # Şirketin LDAP yapısına göre düzenleyin
            search_filter='(objectClass=user)',  # Kullanıcılar için filtre
            attributes=[
                'sAMAccountName', 'givenName', 'sn', 'mail',
                'distinguishedName', 'title', 'userAccountControl'
            ]
        )

        users = []
        for entry in connection.entries:
            # userAccountControl'dan aktiflik durumunu belirle
            user_account_control = entry.userAccountControl.value
            is_active = not (int(user_account_control) & 2)  # 2 -> ACCOUNTDISABLE bayrağı

            user_info = {
                'username': entry.sAMAccountName.value,
                'first_name': entry.givenName.value if entry.givenName else '',
                'last_name': entry.sn.value if entry.sn else 'No Last Name',
                'email': entry.mail.value if 'mail' in entry else None,
                'ldap_dn': entry.distinguishedName.value if 'distinguishedName' in entry else None,
                'is_active': is_active  # Kullanıcı durumu
            }
            users.append(user_info)

        # Kullanıcıları kaydet veya güncelle
        for user in users:
            try:
                ldap_user, created = LdapUser.objects.get_or_create(
                    ldap_dn=user['ldap_dn'],  # LDAP DN benzersiz kontrol
                    defaults={
                        'username': user['username'],
                        'first_name': user.get('first_name', ''),
                        'last_name': user.get('last_name', ''),
                        'email': user.get('email', ''),
                        'company_code': company.code,
                        'company': company,
                        'is_active': user['is_active']
                    }
                )
                if not created:
                    # Eğer kullanıcı zaten varsa ve bilgileri farklıysa güncelle
                    updated = False
                    if ldap_user.first_name != user['first_name']:
                        ldap_user.first_name = user['first_name']
                        updated = True
                    if ldap_user.last_name != user['last_name']:
                        ldap_user.last_name = user['last_name']
                        updated = True
                    if ldap_user.email != user['email']:
                        ldap_user.email = user['email']
                        updated = True
                    if ldap_user.is_active != user['is_active']:
                        ldap_user.is_active = user['is_active']
                        updated = True
                    if updated:
                        ldap_user.save()
                        logging.info(f"Kullanıcı güncellendi: {user['username']}")
                else:
                    logging.info(f"Yeni kullanıcı oluşturuldu: {user['username']}")
            except Exception as e:
                logging.error(f"Kullanıcı kaydedilirken hata oluştu: {str(e)}")

        # Grupları çek
        connection.search(
            search_base=f'dc={ldap_domain},dc=com',
            search_filter='(objectClass=group)',
            attributes=['cn', 'member']
        )

        groups = []
        for entry in connection.entries:
            group_info = {
                'name': entry.cn.value,
                'members': entry.member.values if 'member' in entry else []
            }
            groups.append(group_info)

        # Grupları kaydet
        for group in groups:
            try:
                ldap_group, _ = LdapGroup.objects.get_or_create(
                    name=group['name'],
                    defaults={'company': company}
                )
                for member_dn in group['members']:
                    try:
                        user = LdapUser.objects.get(ldap_dn=member_dn)
                        ldap_group.users.add(user)
                    except LdapUser.DoesNotExist:
                        logging.warning(f"Kullanıcı bulunamadı: {member_dn}")
                logging.info(f"Grup senkronize edildi: {group['name']}")
            except Exception as e:
                logging.error(f"Grup kaydedilirken hata oluştu: {str(e)}")

        logging.info(f"Toplam {len(users)} kullanıcı ve {len(groups)} grup bulundu.")
        return users, groups

    except Exception as e:
        logging.error(f"LDAP kullanıcıları ve grupları alınamadı: {str(e)}")
        return [], []
def auto_get_all_ldap_users_and_groups():
    from inventory_track.models import LdapUser, LdapConfig, LdapGroup
    from django.shortcuts import get_object_or_404
    from ldap3 import Server, Connection, ALL, NTLM
    import logging

    logging.info('Tüm LDAP kullanıcıları ve grupları senkronize ediliyor...')

    try:
        # Tüm LDAP konfigürasyonlarını al
        ldap_configs = LdapConfig.objects.all()

        for ldap_config in ldap_configs:
            try:
                company = ldap_config.company
                ldap_server = ldap_config.ldap_server
                ldap_username = ldap_config.bind_username
                ldap_password = ldap_config.bind_password
                ldap_domain = ldap_config.bind_dn

                logging.info(f"{company.name} için LDAP bağlantısı kuruluyor...")

                # LDAP sunucusuna bağlan
                server = Server(ldap_server, get_info=ALL)
                connection = Connection(
                    server,
                    user=f"{ldap_domain}\\{ldap_username}",
                    password=ldap_password,
                    authentication=NTLM,
                    auto_bind=True
                )

                if not connection.bound:
                    logging.error(f"{company.name} için LDAP bağlantısı başarısız: {connection.last_error}")
                    continue

                logging.info(f"{company.name} için LDAP bağlantısı başarılı!")

                # Kullanıcıları çek
                connection.search(
                    search_base=f'dc={ldap_domain},dc=com',
                    search_filter='(objectClass=user)',
                    attributes=[
                        'sAMAccountName', 'givenName', 'sn', 'mail',
                        'distinguishedName', 'title', 'userAccountControl'
                    ]
                )

                users = []
                for entry in connection.entries:
                    user_account_control = entry.userAccountControl.value
                    is_active = not (int(user_account_control) & 2)

                    user_info = {
                        'username': entry.sAMAccountName.value,
                        'first_name': entry.givenName.value if entry.givenName else '',
                        'last_name': entry.sn.value if entry.sn else 'No Last Name',
                        'email': entry.mail.value if 'mail' in entry else None,
                        'ldap_dn': entry.distinguishedName.value if 'distinguishedName' in entry else None,
                        'is_active': is_active
                    }
                    users.append(user_info)

                # Kullanıcıları kaydet veya güncelle
                for user in users:
                    try:
                        ldap_user, created = LdapUser.objects.get_or_create(
                            ldap_dn=user['ldap_dn'],
                            defaults={
                                'username': user['username'],
                                'first_name': user.get('first_name', ''),
                                'last_name': user.get('last_name', ''),
                                'email': user.get('email', ''),
                                'company_code': company.code,
                                'company': company,
                                'is_active': user['is_active']
                            }
                        )
                        if not created:
                            updated = False
                            if ldap_user.first_name != user['first_name']:
                                ldap_user.first_name = user['first_name']
                                updated = True
                            if ldap_user.last_name != user['last_name']:
                                ldap_user.last_name = user['last_name']
                                updated = True
                            if ldap_user.email != user['email']:
                                ldap_user.email = user['email']
                                updated = True
                            if ldap_user.is_active != user['is_active']:
                                ldap_user.is_active = user['is_active']
                                updated = True
                            if updated:
                                ldap_user.save()
                                logging.info(f"{company.name} için kullanıcı güncellendi: {user['username']}")
                        else:
                            logging.info(f"{company.name} için yeni kullanıcı oluşturuldu: {user['username']}")
                    except Exception as e:
                        logging.error(f"{company.name} için kullanıcı kaydedilirken hata oluştu: {str(e)}")

                # Grupları çek
                connection.search(
                    search_base=f'dc={ldap_domain},dc=com',
                    search_filter='(objectClass=group)',
                    attributes=['cn', 'member']
                )

                groups = []
                for entry in connection.entries:
                    group_info = {
                        'name': entry.cn.value,
                        'members': entry.member.values if 'member' in entry else []
                    }
                    groups.append(group_info)

                # Grupları kaydet
                for group in groups:
                    try:
                        ldap_group, _ = LdapGroup.objects.get_or_create(
                            name=group['name'],
                            defaults={'company': company}
                        )
                        for member_dn in group['members']:
                            try:
                                user = LdapUser.objects.get(ldap_dn=member_dn)
                                ldap_group.users.add(user)
                            except LdapUser.DoesNotExist:
                                logging.warning(f"{company.name} için kullanıcı bulunamadı: {member_dn}")
                        logging.info(f"{company.name} için grup senkronize edildi: {group['name']}")
                    except Exception as e:
                        logging.error(f"{company.name} için grup kaydedilirken hata oluştu: {str(e)}")

                logging.info(f"{company.name} için toplam {len(users)} kullanıcı ve {len(groups)} grup bulundu.")

            except Exception as e:
                logging.error(f"{company.name} için senkronizasyon sırasında hata oluştu: {str(e)}")

        logging.info("Tüm LDAP şirket senkronizasyonları tamamlandı.")
    except Exception as e:
        logging.error(f"LDAP kullanıcıları ve grupları alınamadı: {str(e)}")
