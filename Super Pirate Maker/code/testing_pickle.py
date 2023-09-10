import pickle

def save(lista, nome_arquivo):
    with open(nome_arquivo, 'wb') as arquivo:
        pickle.dump(lista, arquivo)
    print(f"A lista foi salva no arquivo {nome_arquivo}.")


def load(nome_arquivo):
    with open(nome_arquivo, 'rb') as arquivo:
        lista = pickle.load(arquivo)
    return lista

# Exemplo de uso
minha_lista = [1, 2, 3, 4, 5]
nome_do_arquivo = "lista.pkl"

save(minha_lista, nome_do_arquivo)

# Exemplo de uso
nome_do_arquivo = "lista.pkl"

minha_lista_recuperada = load(nome_do_arquivo)
print(minha_lista_recuperada)

