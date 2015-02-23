# install

```install
pip install pyotp
```

# Usage

```Usage
sshd as example, add the following line to the end of /etc/pam.d/sshd and restart sshd, make sure auth.py is executable for root
auth required pam_python.so /your/path/to/auth.py
```
