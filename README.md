LibraryAPI é uma API RESTful desenvolvida para o gerenciamento de uma biblioteca de livros como parte de um projeto backend com uso de frameworks Django.

## Funcionalidades

- Gerenciamento de Livros (CRUD)
- Gestão de Empréstimos (CRUD)
- Cadastro e Autênciação de Usuários

## Tecnologias Utilizadas

- Django
- Djangorestframework
- Corsheaders
- Pillow
- Simple-JWT
- Pytest-Django

## Instruções de Uso

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

Você também pode criar um superusuário para manipular diretamente os dados sem passar pela autênticação
```bash
$ python manage.py createsuperuser
```

Para rodar os testes unitários basta rodar o seguinte comando
```bash
$ pytest
```

## Autor

- GitHub: [@DaviRafaelDev](https://github.com/DaviRafaelDev)
- LinkedIn: [Davi Nascimento](https://www.linkedin.com/in/davinascimentodev/)
