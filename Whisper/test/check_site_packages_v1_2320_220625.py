import sys
import site

print(f"Python executable: {sys.executable}")
print(f"User site-packages: {site.getusersitepackages()}")
print(f"System site-packages: {site.getsitepackages()}")
