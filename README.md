# projeto_samba4

SAMBA AD

O Samba Active Directory (Samba AD) é uma implementação do serviço de diretório do Active Directory (AD) da Microsoft, criada pela comunidade de código aberto do Samba. O Active Directory é um serviço de diretório utilizado principalmente em ambientes corporativos que executam o sistema operacional Windows Server. Ele fornece uma variedade de serviços de diretório, incluindo autenticação de usuários, gerenciamento de políticas de segurança, organização de recursos de rede e muito mais.

O Samba AD permite que sistemas Linux e UNIX funcionem como controladores de domínio compatíveis com o Active Directory, oferecendo muitos dos mesmos recursos e funcionalidades encontrados em um ambiente Windows Server. Isso inclui:

1 - Autenticação de usuário: O Samba AD permite que os usuários autentiquem suas credenciais de login em sistemas Linux e UNIX usando suas contas do Active Directory.

2 - Gestão de políticas de grupo: O Samba AD permite que os administradores definam e apliquem políticas de grupo para usuários e computadores em uma rede, semelhantes às funcionalidades oferecidas pelo Active Directory.

3 - Gestão de recursos de rede: Os controladores de domínio do Samba AD podem ser usados para gerenciar e controlar o acesso a recursos de rede, como compartilhamentos de arquivos e impressoras.

4 - Integração com serviços de autenticação: O Samba AD pode ser integrado com outros serviços de autenticação, como Kerberos e LDAP, para oferecer uma experiência de autenticação mais segura e robusta.

5 - Compatibilidade com clientes Windows: Os controladores de domínio do Samba AD são compatíveis com clientes Windows, permitindo que computadores Windows sejam integrados a um domínio Samba AD e utilizem seus serviços de forma transparente.

O Samba AD é uma opção atraente para organizações que desejam implantar um ambiente de diretório centralizado e autenticação única em uma infraestrutura heterogênea, combinando sistemas Windows e Linux/UNIX. Ele oferece uma alternativa de código aberto ao Active Directory da Microsoft, proporcionando muitos dos mesmos recursos e funcionalidades a um custo mais baixo.

1 - Definições

Hostname: fedora.mydomain.lan
Dominio: mydomain.lan
IP: 172.16.10.10/16

2 - Instalando o Samba

Instalando os pacotes necessários para o funcionamento do Samba-ad

dnf install samba samba-dc samba-client krb5-workstation

3 - Hostname

Organizando o hostname do servidor:

hostnamectl hostname fedora.mydomain.lan

4 - Firewall

Adicionando as regras necessários de firewall:

Adicionando o serviço:

firewall-cmd --permanent --add-service=samba-dc --zone=FedoraServer

5 - Segundo método

Alternativa para adionar as portas manualmente:

firewall-cmd --permanent --add-port={53/udp,53/tcp,88/udp,88/tcp,123/udp,135/tcp,137/udp,138/udp,139/tcp,389/udp,389/tcp,445/tcp,464/udp,464/tcp,636/tcp,3268/tcp,3269/tcp,49152-65535/tcp}

Releia o firewalld:

firewall-cmd --reload

6 - SELinux

Para rodar o Samba-ad é necessário adicionar as boolenas ao SELINUX.

setsebool -P samba_create_home_dirs=on 
samba_domain_controller=on samba_enable_home_dirs=on 
samba_portmapper=on use_samba_home_dirs=on

sudo restorecon -Rv /

7 - Samba e resolv

Remover o /etc/samba/smb.conf arquivo existente:

rm /etc/samba/smb.conf

Temos que acertar o arquivo resolve para divulgar DNS para a rede.

Criar o diretório /etc/systemd/resolved.conf.d/ se ele não existirt:

mkdir /etc/systemd/resolved.conf.d/

Criar o arquivo /etc/systemd/resolved.conf.d/custom.conf contendo o seguinte conteúdo:

[Resolve]
DNSStubListener=no
Domains=mydomain.lan
DNS=192.168.10.10

Reiniciar o serviço systemd-resolved:

systemctl restart systemd-resolved

Finalizando, provisionando as onfigurações do Samba.

Use o samba-tool para a diulgação do servidor:

samba-tool domain provision --server-role=dc --use-rfc2307 --dns-backend=SAMBA_INTERNAL --realm=MYDOMAIN.LAN --domain=MYDOMAIN --adminpass=minhasenha@2024

O argumento ?use-rfc2307 fornece atributos POSIX ao Active Directory, que armazena informações do usuário e do grupo Unix sobre LDAP.

Certifique-se de que você tem o endereço de encaminhador dns correto definido em /etc/samba/smb.conf. Em relação a este tutorial, ele deve ser diferente do endereço IP do próprio servidor 172.16.10.10, no meu caso, eu defino para 8.8.8.8, altere os valores dentro do arquivo /etc/samba/smb.conf
8 - Kerberos

Depois de configurado o Samba devemos configurar o kerberos o arquivo krb5.conf usando:

 cp /usr/share/samba/setup/krb5.conf /etc/krb5.conf.d/samba-dc

Edite arquivo /etc/krb5.conf.d/samba-dc adicione as informações da sua organização:

[libdefaults]
  default_realm = MYDOMAIN.LAN
  dns_lookup_realm = false
  dns_lookup_kdc = true
[realms]
MYDOMAIN.LAN = {
  default_domain = MYDOMAIN
}
[domain_realm]
  fedora.mydomain.lan = MYDOMAIN.LAN

9 - Iniciando e ativando o serviço samba na inicialização

Fazendo da seguinte forma:

 systemctl enable samba
 systemctl start samba

10 - Testando conectividade

$ smbclient -L localhost -N

As a result of smbclient command, shows that connection was successful.

Anonymous login successful
        Sharename       Type      Comment
        ---------       ----      -------
        sysvol          Disk
        netlogon        Disk
        IPC$            IPC       IPC Service (Samba 4.15.6)
SMB1 disabled -- no workgroup available

smbclient connection test

Agora vamos fazer login como administrador:

$ smbclient //localhost/netlogon -UAdministrator -c 'ls'
Password for [ONDA\Administrator]:
  .                              D        0  Sat Mar 26 05:45:13 2022
  ..                             D        0  Sat Mar 26 05:45:18 2022
                8154588 blocks of size 1024. 7307736 blocks available

smbclient Administrator connection test
11 - Testando DNS

Execute os seguintes comandos para testes de DNS:

$ host -t SRV _ldap._tcp.mydomain.lan.
_ldap._tcp.onda.org has SRV record 0 100 389 fedora.meudominio.local.
$ host -t SRV _kerberos._udp.mydomain.lan.
_kerberos._udp.onda.org has SRV record 0 100 88 fedora.meudominio.local.
$ host -t A fedora.mydomain.lan.
dc1.onda.org has address 172.16.10.10

se seus comandos resutlar erros como:

-bash: host: command not found 

Instale o pacote bind-utils:

dnf install bind-utils

12 - Testanto o Kerberos

$ kinit administrator
$ klist

13 - Adding a user to the Domain

Use o comando abaixo para ver mais especificações para adicionar o usuário ao domínio:

$ samba-tool user add --help

Adicionando o usuário marcio.rcolombo ao dominio:

 samba-tool user add marcio.rcolombo MinhaSenha --unix-home=/home/marcio.rcolombo --login-shell=/bin/bash --gecos 'Márcio Colombo.' --given-name=Marcio --surname='Colombo' --mail-address='marcio.colombo@mydomain.lan'

Liste os usuários do dominio:

 samba-tool user list
