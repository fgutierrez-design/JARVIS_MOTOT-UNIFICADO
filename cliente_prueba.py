#!/usr/bin/env python3
import requests, sys
b=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:11435').rstrip('/')
print('Estado', requests.get(b+'/api/estado',timeout=10).json())
print('Enjambre', requests.post(b+'/api/enjambre/ciclo',timeout=30).json().get('ciclos'))
print(requests.post(b+'/api/pensar',json={'texto':'Hola motor unificado, que hora es?'},timeout=90).json())
