# e2_configure_favoritos

Script para gerar canais ordenados para o pixel com e2


## Instalação

Entrar no terminal do e2 e fazer o download do script:
```
wget https://raw.githubusercontent.com/josemoraes99/enigma2_custom_bouquet/master/e2_configure_favoritos.py
```

## Para executar: (o script é em python 2)

```
python e2_configure_favoritos.py
```

## Argumentos

Remover canais SD quando houver em HD
```
--desativar-canais-sd
```

Remover canais adultos
```
--desativar-canais-adultos
```

Remover canais internos
```
--desativar-canais-internos
```

## Exemplo com argumentos
```
python e2_configure_favoritos.py --desativar-canais-sd --desativar-canais-adultos --desativar-canais-internos
```
