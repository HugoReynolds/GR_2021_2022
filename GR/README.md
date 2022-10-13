# Guião 5 : Rui Freitas, a84121

## Opções tomadas

Relativamente ao guião desta semana foram criados 2 ficheiros para a implementação do servidor [server.py](https://github.com/uminho-leti-crypto/2122-G02/blob/main/Guioes/G05/server.py) e do cliente [client.py](https://github.com/uminho-leti-crypto/2122-G02/blob/main/Guioes/G05/client.py).
Para a implementação do protocolo de acordo de chaves Diffie-Hellman, como este é realizado com a troca de chaves publicas entre o cliente e servidor estes mandam mensagens encriptadas um para o outro com as informações necessárias. Após isso são trocadas mensagens do cliente para o servidor encriptadas com o AESGCM e HMAC. Um aspeto a notar na realização deste guião foi o facto de termos tido um problema ao fechar o socket em que ao invés de utilizar '\n' para enviar esta informação ao servidor tivemos de alterar para 'quit'.

## Principais dificuldades

Na realização deste guião não nos deparámos com notáveis dificuldades apenas o assunto falado anteriormente do facto de não estarmos a conseguir fechar a socket com '\n' mas achamos ser um problema menor.# GR_2021_2022
# GR_2021_2022
