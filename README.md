# Dentman
Dentman is a dentist office management system build using Django with Nginx and Docker. Application will allow to manage whole office: your clients, employees, stuff and bills. Customers will be able to appoint the visit, check their vists history and much more.

## How to run
First, you have to clone the repo using
```bash
git clone git@github.com:Blizek/dentist-office-management.git
```

Next you need to install (if you don't have):
 - Python 3.12 or newer
 - Django 5.2.2 or newer
 - Poetry
 - Nginx
 - Docker

After that type in terminal
```bash
make build
make etc/nginx.conf
```

To run application type
```bash
make up
```