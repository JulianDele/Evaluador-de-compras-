#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from app.auth.security import create_access_token

token = create_access_token(10)
print(token)
