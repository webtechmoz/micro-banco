from manage_sql import SQLITE
import os
from tabulate import tabulate

# 1 - Registar Usuarios
class Registar:
    def __init__(
        self,
        nome: str,
        username: str,
        senha: str
    ):
        self.nome = nome
        self.senha = senha
        self.username = username
        self.__db = SQLITE(
            database='usuarios',
            path='usuarios'
        )

        self.__db.create_table(
            tablename='usuarios',
            columns=[
                self.__db.Column(
                    name='nome',
                    column_type=self.__db.Column_types.text,
                ),
                self.__db.Column(
                    name='username',
                    column_type=self.__db.Column_types.text,
                ),
                self.__db.Column(
                    name='senha',
                    column_type=self.__db.Column_types.text,
                ),
                self.__db.Column(
                    name='status',
                    column_type=self.__db.Column_types.text,
                )
            ]
        )
    
    def criar_usuario(self) -> bool:
        usuarios = self.__db.select_data(
            tablename='usuarios',
            condition=self.__db.filter_by(
                column='username'
            ).EQUAL(
                value=self.username
            )
        )

        if len(usuarios) > 0:
            return False

        else:
            self.__db.insert_data(
                tablename='usuarios',
                insert_query=[
                    self.__db.ColumnData(
                        column='nome',
                        value=self.nome
                    ),
                    self.__db.ColumnData(
                        column='username',
                        value=self.username
                    ),
                    self.__db.ColumnData(
                        column='senha',
                        value=self.__db.encrypt_value(self.senha)
                    ),
                    self.__db.ColumnData(
                        column='status',
                        value=1
                    )
                ]
            )

            return True

# 2 - Login
class Login:
    def __init__(
        self,
        username: str,
        senha: str
    ):
        self.username = username
        self.senha = senha
        self.__db = SQLITE(
            database='usuarios',
            path='usuarios'
        )
    
    def logar(self):
        try:
            usuario = self.__db.select_data(
                tablename='usuarios',
                columns=['nome', 'username',],
                condition=self.__db.filter_by(
                    column='username'
                ).EQUAL(
                    value=self.username
                ).AND.filterby(
                    column='senha'
                ).EQUAL(
                    value=self.__db.encrypt_value(
                        value=self.senha
                    )
                )
            )

            return usuario
        
        except Exception as e:
            return e

# 3 - Menu principal (Depositar, Transferir, Levantar, Ver Saldo, Movimentos)
class ContaPrincipal:
    def __init__(
        self,
        username: str
    ):
        self.username = username
        self.__db = SQLITE(
            database='contas',
            path='contas'
        )
        self.__db.create_table(
            tablename='saldos',
            columns=[
                self.__db.Column(
                    name='username',
                    column_type=self.__db.Column_types.text
                ),
                self.__db.Column(
                    name='saldo',
                    column_type=self.__db.Column_types.real
                )
            ]
        )
        self.__db.create_table(
            tablename='movimentos',
            columns=[
                self.__db.Column(
                    name='username',
                    column_type=self.__db.Column_types.text
                ),
                self.__db.Column(
                    name='descricao',
                    column_type=self.__db.Column_types.text
                ),
                self.__db.Column(
                    name='saldo_inicial',
                    column_type=self.__db.Column_types.real
                ),
                self.__db.Column(
                    name='valor',
                    column_type=self.__db.Column_types.real
                ),
                self.__db.Column(
                    name='saldo_final',
                    column_type=self.__db.Column_types.real
                )
            ]
        )
    
    def ver_saldo(self):
        def consultar():
            saldo = self.__db.select_data(
                tablename='saldos',
                columns=['username','saldo'],
                condition=self.__db.filter_by(
                    column='username'
                ).EQUAL(
                    value=self.username
                )
            )

            return saldo

        if len(consultar()) == 0:
            self.__db.insert_data(
                tablename= 'saldos',
                insert_query=[
                    self.__db.ColumnData(
                        column='username',
                        value=self.username
                    ),

                    self.__db.ColumnData(
                        column='saldo',
                        value=0
                    ),
                ]
            )

        return consultar()
    
    def ver_movimentos(self):
        movimentos = self.__db.select_data(
            tablename='movimentos',
            columns=['username', 'descricao', 'saldo_inicial', 'valor', 'saldo_final'],
            condition=self.__db.filter_by(
                column='username'
            ).EQUAL(
                value=self.username
            )
        )

        return movimentos
    
    def depositar(self, montante: float):
        self.__movimentar(montante=montante, descricao='deposito de valores')
    
    def levantar(self, montante: float):
        self.__movimentar(montante=-montante, descricao='levantamento de valores')
    
    def transferir(self, montante: float, destinatario: str):
        self.__movimentar(montante=-montante, descricao=f'transferiu para {destinatario}')
    
    def receber(self, montante: float, rementente: str):
        self.__movimentar(montante=montante, descricao=f'recebeu de {rementente}')

    def __movimentar(self, montante: float, descricao: str):
        saldo_inicial = self.ver_saldo()[0][1]

        if montante < 0 and saldo_inicial + montante < 0:
            print('Não possui saldo disponível para efectuar este movimento')
            exit()
        
        else:
            self.__db.insert_data(
                tablename='movimentos',
                insert_query=[
                    self.__db.ColumnData(
                        column='username',
                        value=self.username
                    ),
                    self.__db.ColumnData(
                        column='descricao',
                        value=descricao
                    ),
                    self.__db.ColumnData(
                        column='saldo_inicial',
                        value=saldo_inicial
                    ),
                    self.__db.ColumnData(
                        column='valor',
                        value=montante
                    ),
                    self.__db.ColumnData(
                        column='saldo_final',
                        value=saldo_inicial + montante
                    )
                ]
            )

            self.__db.update_data(
                tablename='saldos',
                edit_query=[
                    self.__db.ColumnData(
                        column='saldo',
                        value=saldo_inicial + montante
                    )
                ],
                condition=self.__db.filter_by(
                    column='username'
                ).EQUAL(
                    value=self.username
                )
            )

def clean_system():
    os.system('cls')

def registar():
    """Registar no sistema"""

    while True:
        nome = input('Digite o seu nome: ')

        if nome:
            break

        clean_system()
    
    while True:
        username = input('Digite o seu username: ')

        if username:
            break

        clean_system()
    
    while True:
        senha = input('Digite a sua senha: ')

        if senha:
            break

        clean_system()

    Registar(nome=nome, username=username, senha=senha).criar_usuario()

    return main()

def logar():
    """Logar no sistema"""

    username = input('Digite o username: ')
    senha = input('Digite a senha: ')

    response = Login(username=username, senha=senha).logar()

    if type(response) == Exception:
        print(f'Erro: {response}')
    
    elif len(response) == 0:
        clean_system()

        print('Usuário ou senha incorrectos\n')

        return logar()

    else:
        return conta_principal(username=response[0][1], nome=response[0][0])

def conta_principal(username: str, nome: str):
    """Gestão da conta bancária"""
    clean_system()

    text = f"Conta do cliente {nome}\n\n1. Depositar\n2. Levantar\n3. Transferir\n4. Saldo\n5. Movimentos\n0. Sair: "

    while True:
        opcao = input(text)

        if opcao in ['0', '1', '2', '3', '4', '5']:
            clean_system()

            if opcao == '0':
                exit()
            
            elif opcao == '1':
                depositar(username, nome)
            
            elif opcao == '2':
                levantar(username, nome)
            
            elif opcao == '3':
                transferir(username, nome)
            
            elif opcao == '4':
                clean_system()
                ver_saldo(username, nome)
            
            elif opcao == '5':
                clean_system()
                ver_movimentos(username, nome)
        
        else:
            clean_system()

            print('Opção incorrecta. Tente de novamente')

def depositar(username: str, nome: str):
    """Depositar valores"""

    while True:
        try:
            montante = input('Digite o montante (0. Voltar): ')

            if montante == '0':
                break

            ContaPrincipal(username=username).depositar(float(montante))

            break

        except Exception as e:
            print(f'Erro: {e}\n')

    return conta_principal(username=username, nome=nome)

def levantar(username: str, nome: str):
    """Levantar valores"""

    while True:
        try:
            montante = input('Digite o montante a levantar (0. Voltar): ')

            if montante == '0':
                break

            ContaPrincipal(username=username).levantar(float(montante))

            break
        
        except Exception as e:
            clean_system()
            print(f'Erro: {e}\n')

    return conta_principal(username=username, nome=nome)

def transferir(username: str, nome: str):
    """Transferir valores"""

    while True:
        try:
            montante = input('Digite o montante a transferir (0. Voltar): ')

            if montante == '0':
                return conta_principal(username, nome)

            montante = float(montante)

            break
        
        except Exception as e:
            clean_system()
            print(f'Erro: {e}\n')

    while True:

        destino = input('Digite a conta destino (0. Voltar): ')

        if destino == '0':
            break

        db = SQLITE(
            database='usuarios',
            path='usuarios'
        )

        confirmar_user = db.select_data(
            tablename='usuarios',
            condition=db.filter_by(
                column='username'
            ).EQUAL(
                value=destino
            )
        )

        if len(confirmar_user) > 0:
            break

        else:
            clean_system()
            print('Usuário incorrecto. Tente novamente!\n')
            
    if destino != '0':
        ContaPrincipal(username=username).transferir(montante=float(montante), destinatario=destino)
        ContaPrincipal(username=destino).receber(montante=float(montante), rementente=username)
    
    return conta_principal(username, nome)

def ver_saldo(username: str, nome: str):
    """Ver saldo"""

    saldo = ContaPrincipal(username=username).ver_saldo()
    header = ['Username', 'Saldo (MT)']

    while True:
        clean_system()

        print(f'{tabulate(saldo, header, tablefmt='grid')}\n')
        opcao = input('0. Voltar: ')

        if opcao == '0':
            return conta_principal(username, nome)

        else:
            break
    
    clean_system()
    exit()

def ver_movimentos(username: str, nome: str):
    """Ver movimentos"""

    movimentos = ContaPrincipal(username=username).ver_movimentos()
    header = ['Username', 'Descrição', 'Saldo Inicial', 'Montante', 'Saldo Final']

    while True:
        print(f'{tabulate(movimentos, header, tablefmt='grid')}\n')
        opcao = input('0. Voltar: ')

        if opcao == '0':
            return conta_principal(username, nome)

        else:
            break

    clean_system()
    exit()

def main():
    """Inicindo a aplicação"""
    clean_system()

    texto = "Bem vindo ao Meu-Banco\n\n1. Registar\n2. Entrar\n0. Sair: "

    while True:
        opcao = input(texto)

        if opcao in ['0','1','2']:
            clean_system()
            if opcao == '1':
                registar()
            
            elif opcao == '2':
                logar()
            
            elif opcao == '0':
                exit()
        
        else:
            clean_system()
            print('Opção incorrecta. Tente de novo\n')

if __name__ == '__main__':
    main()