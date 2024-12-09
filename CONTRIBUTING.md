## Como Contribuir

- Faça um Fork no repositório principal
- Clone o Fork no seu computador

```bash
$ git clone https://github.com/seu-usuario/seu-fork.git
```

## Configure o Ambiente

Primeiro abra o terminal e clone o repositório.

```bash
$ git clone https://github.com/DaviRafaelDev/LibraryAPI
```

Navegue até a pasta raiz do projeto.

```bash
$ cd LibraryAPI
```

Crie e Inicie um ambiente virtual(venv)

```bash
$ python -m venv .venv
```

Para Windows

```bash
$ .venv/Scripts/activate
```

Para Linux/GNU

```bash
$ Source .venv/bin/activate
```

Instale as dependências. Verifique se já têm o [`Python`](https://www.python.org/downloads/) instalado no seu sistema.

```bash
$ pip install -r requirements.txt
```

Inicie o App.

```bash
$ python manage.py runserver
```

## Faça Suas Alterações

Crie uma nova branch para seu trabalho:

```bash
$ git checkout -b minha-feature
```

Faça commits claros e descritivos:

```bash
$ git commit -m "Adicionar funcionalidade"
```

## Submeta Seu Trabalho

Envie suas alterações para o seu fork:

```bash
$ git push origin minha-feature
```

Crie um Pull Request (PR) no repositório principal.

Certifique-se de que seu PR:

- Inclui uma descrição clara do que foi feito.
- Se relaciona a uma issue (se aplicável).

## Feedback e Revisão

- Aguarde revisão do seu PR.
- Faça as alterações solicitadas, se necessário.
- Quando aprovado, seu código será mesclado ao repositório principal!

Obrigado por contribuir!
