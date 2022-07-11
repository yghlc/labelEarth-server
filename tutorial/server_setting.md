# Server setting on Ubuntu 20.04

## Vagrant virtual machine (or use a real server)
We can set up a virtual machine for our project in [Vagrant](https://www.vagrantup.com/).
```
cp ~/programs/vagrant-machine/vm-labelEarth/Vagrantfile .
vagrant up
vagrant ssh # login to the VM
# after login, modify the default password for user: vagrant. 
passwd  # enter the current password, then enter the new password twice.
# create a new admin account
sudo su - # enter the root user
adduser user # change the username to your own, then enter the password twice.
usermod -aG sudo user # add the user to the sudo group.
```

## Set firewall of the server
Set up firewall: ref: [Initial Server Setup with Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04)
```angular2html
sudo ufw allow 'OpenSSH'   # allow SSH first, so we can log back in next time. 
sudo ufw enable
sudo ufw app list  # list all applications
sudo ufw status     # show the status of the firewall
```

## Apache2 
Install Apache2. ref: [How To Install the Apache Web Server on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-20-04)
``` 
sudo apt update
sudo apt install apache2
sudo ufw allow 'Apache'
sudo systemctl status apache2   # check the status of the Apache2
```
Available applications: Apache, Apache Full, Apache Secure, OpenSSH. 
Apache: This profile opens only port 80 (normal, unencrypted web traffic).
Apache Full: This profile opens both port 80 (normal, unencrypted web traffic) and port 443 (TLS/SSL encrypted traffic).
Apache Secure: This profile opens only port 443 (TLS/SSL encrypted traffic).

We can get the ip address of the server by one of the following ways:
```
ifconfig  # show the ip address of the server
hostname -I     # recommended, You will get back a few addresses separated by spaces. You can try each in your web browser to determine if they work. then you can use the address to open the default Apache landing page, making sure Apache2 is running
curl -4 icanhazip.com #Icanhazip tool, which should give you your public IP address as read from another location on the internet
```
should be able to open Apache web page: http://your_server_ip

Managing the Apache Process:
```
sudo systemctl stop apache2
sudo systemctl start apache2
sudo systemctl restart apache2
sudo systemctl reload apache2   # reload configuration without dropping connections.
sudo systemctl disable apache2  # disable starting automatically
sudo systemctl enable apache2
```
Some directories for Apache [link](https://www.digitalocean.com/community/tutorials/how-to-install-the-apache-web-server-on-ubuntu-20-04):
```
content: /var/www/html
the main configuration file: /etc/apache2/apache2.conf

Server logs:
/var/log/apache2/access.log: By default, every request to your web server is recorded in this log file unless Apache is configured to do otherwise.
/var/log/apache2/error.log: By default, all errors are recorded in this file. The LogLevel directive in the Apache configuration specifies how much detail the error logs will contain.
```

## Django
Create a python environment for Django. After set up Apache, 
we need to install mod_wsgi for Django. mod_wsgi is an Apache module which can host any Python [WSGI](https://wsgi.readthedocs.io/en/latest/) application, including Django. 
Django will work with any version of Apache which supports mod_wsgi.

Use the python3 in Ubuntu 20.04. Don't use  miniconda3 or anaconda3, 
some problems with webservice: https://github.com/GrahamDumpleton/mod_wsgi/issues/338
```angular2html
sudo apt install -y python3-pip
sudo ln /usr/bin/python3 /usr/bin/python # "which python" to check
sudo apt update && sudo apt install build-essential
sudo apt-get install apache2-dev
```
install mod_wsgi, ref to https://modwsgi.readthedocs.io/en/develop/user-guides/quick-installation-guide.html 

Source code of mod_wsgi: https://github.com/GrahamDumpleton/mod_wsgi/releases
```
wget https://github.com/GrahamDumpleton/mod_wsgi/archive/refs/tags/4.9.2.tar.gz
tar xvfz 4.9.2.tar.gz
cd mod_wsgi-4.9.2
./configure
make
sudo make install
# setting in (Apache/2.4.41)
cd /etc/apache2/mods-available 
sudo echo "LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi.so" > mod_wsgi.load
sudo a2enmod mod_wsgi.load
sudo systemctl restart apache2
```

Create a virtual env for Django:
```
cd # change to home folder
sudo apt install python3.8-venv
python3 -m venv djangoEnv
source djangoEnv/bin/activate
python3 -m pip install django==4.0.3
python3 -m pip install geopandas==0.10.2
python3 -m pip install django-debug-toolbar==3.2.4
python3 -m pip install django-cors-headers==3.11.0
python3 -m pip install django-crispy-forms==1.14.0
python3 -m pip install openpyxl==3.0.10
```

## PostgreSQL
Install PostgreSQL as the database server, ref: [How To Use PostgreSQL with your Django Application on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-20-04).
```
sudo apt update
sudo apt install libpq-dev postgresql postgresql-contrib
```
Create a database. Please change the "username" and "password" to your own.
```
sudo -u postgres psql           # login to postgresql
CREATE DATABASE thawslump_db;   # create a database, ";" is needed.
CREATE USER username WITH PASSWORD 'password'; # create a user with password.
# modify the parameters for the user just created:
ALTER ROLE username SET client_encoding TO 'utf8'; 
ALTER ROLE username SET default_transaction_isolation TO 'read committed';
ALTER ROLE username SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE thawslump_db TO username;
```
Install packages and setting for Django.
```
source djangoEnv/bin/activate   # activate Django environment
pip install psycopg2            # could be a error, but eventually success.
```
Setting is in the ./labelEarth/settings.py (no need to change). These parameters are read from the file: "setting.ini", 
avoiding uploading username and password to a public repository. 
```
DATABASES = {
    'default': {
        'ENGINE': database_engine,
        'NAME': database_name,
        'USER': database_user,
        'PASSWORD': database_password,
        'HOST': database_host,
        'PORT': database_port,
    }
}
```
Some useful commands for PostgreSQL:
```
python manage.py migrate --run-syncdb      # load database schema
python manage.py loaddata labelEarthServer_db.json # load data from json file
sudo -u postgres psql                         # login to postgresql
# after login to postgresql:
\c thawslump_db                             # connect to the database
\dt                                        # show tables
SELECT * FROM public.auth_user;             # show all rows in the table "auth_user"
\q                                          # quit
```


## Enable HTTPS
enable https in Apache2, refer to [link](https://techexpert.tips/apache/enable-https-apache/).
```
sudo apt-get update
sudo apt-get install openssl
sudo a2enmod ssl
sudo a2enmod rewrite
sudo ufw allow "Apache Full"  # allow port 443 and 80
sudo systemctl restart apache2

# in /etc/apache2/apache2.conf, adding the following lines at the end of the file:
<Directory /var/www/html>
AllowOverride All
</Directory>
```
Create a private key and the website certificate using the OpenSSL command. 
```
sudo mkdir /etc/apache2/certificate
cd /etc/apache2/certificate
# On the option named COMMON_NAME, you need to enter the IP address or hostname
sudo openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out apache-certificate.crt -keyout apache.key

# save the following setting into: /etc/apache2/sites-enabled/000-default.conf
<VirtualHost *:80>
        RewriteEngine On
        RewriteCond %{HTTPS} !=on
        RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R=301,L]
</virtualhost>
<VirtualHost *:443>
        ServerAdmin webmaster@localhost
        DocumentRoot /var/www/html
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
        SSLEngine on
        SSLCertificateFile /etc/apache2/certificate/apache-certificate.crt
        SSLCertificateKeyFile /etc/apache2/certificate/apache.key
</VirtualHost>

# check apache2 configuration by running: 
sudo apache2ctl -t
```
*When you navigate to your website via HTTPS, 
you’ll be warned that it’s not a trusted certificate. 
That’s okay. We know this since we signed it ourselves! 
Just proceed and you will see your actual website. 
This will not happen if you use a paid SSL certificate or 
an SSL certificate provided by Letsencrypt.* copied from [link](https://www.rosehosting.com/blog/how-to-enable-https-protocol-with-apache-2-on-ubuntu-20-04/).

SSL certificate is necessary for https, and we may purchase a SSL certificate or
apply for a [free one](https://geekflare.com/free-ssl-tls-certificate/) or 
request one from our university [IT department](https://oit.colorado.edu/services/web-content-applications/ssl-certificates).

## Deploy the website
read this [checklist](https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/) before deploying.
More information about Django setting is at [link](https://docs.djangoproject.com/en/4.0/ref/settings/)
```angular2html
# check the potential problems by running:
python manage.py check --deploy
```










