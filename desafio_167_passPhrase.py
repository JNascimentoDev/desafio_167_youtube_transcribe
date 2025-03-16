from youtube_transcript_api import YouTubeTranscriptApi
import unicodedata
import re
from urllib.parse import urlparse, parse_qs
import hashlib
import requests

# Definir o hash alvo e regex para validação do SHA256
target_hash = '71718102e9b760d2f04b2df8315241af1672d8253d51aa62f3cb55257375c046'
sha256_regex = re.compile(r"^[a-fA-F0-9]{64}$")

# Função para exibir a descrição do script
def imprimir_descricao():
    descricao = """
    📝 ** CAÇADOR DE MENSAGEM SECRETA - by. DomDoko **

    🔍 **Descrição:**  
    Este script busca uma frase secreta nos ** 30 últimos vídeos ** do canal ** Mestre Cacatal ** no YouTube, 
    utilizando transcrições automáticas. Ele analisa combinações de palavras nas transcrições e compara os 
    hashes SHA-256 com um valor alvo fornecido pelo usuário, exibindo a senha encontrada ao identificar uma 
    correspondência. 🎯

    📺 **Canal:** Mestre Cacatal  
    📊 **Objetivo:** Encontrar a passphrase secreta nos vídeos e validar o hash SHA-256.
    """
    print(descricao)

# Função para limpar a string (remove acentos, caracteres especiais e números)
def clean_string(text):
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.replace('ç', 'c').replace('Ç', 'C')
    text = re.sub(r'[.,\n\d]', '', text)
    return text.lower()

# Função para extrair o ID do vídeo a partir da URL
def get_video_id(url):
    parsed_url = urlparse(url)
    if "youtube" in parsed_url.netloc:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif "youtu.be" in parsed_url.netloc:
        return parsed_url.path.lstrip("/")
    return None

# Função para obter a transcrição do vídeo
def get_transcription(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt'])
        return ' '.join(entry['text'] for entry in transcript)
    except Exception as e:
        return f"Erro ao obter transcrição: {e}"

# Função para verificar combinações de palavras nas transcrições
def check_string(lista_palavras, number_words, len_string):
    resultado = []
    tamanho_lista = len(lista_palavras)

    for i in range(tamanho_lista - (number_words-1)):
        grupo = lista_palavras[i:i+number_words]
        if sum(len(p) for p in grupo) == len_string:
            iniciais = {p[0] for p in grupo if p}  # Ignora palavras vazias
            if len(iniciais) == 5:
                resultado.append("".join(grupo))

    return resultado

# Bloco principal de execução
if __name__ == "__main__":
    imprimir_descricao()  # Exibe a descrição do script
    
    # Interação com o usuário para obter número de palavras e tamanho da string
    while True:
        try:
            num_words = int(input("Nº de palavras: "))
            len_string = int(input("Tamanho da String: "))
            break  # Sai do loop se ambas as entradas forem inteiras
        except ValueError:
            pass
    
    # Solicita o SHA256 alvo e valida o formato
    while True:
        print(f'Pressione ENTER para o SHA256: {target_hash}')
        sha256_alvo = input("SHA256 Alvo: ").strip() or target_hash
        print(f'🔍 Buscando SHA256: {sha256_alvo}')
        
        if sha256_regex.fullmatch(sha256_alvo):
            break

    continue_code = True
    url = "https://www.youtube.com/@mestrecacatal/videos"
    
    # Coleta os IDs dos vídeos mais recentes
    index_key = '"richItemRenderer":{"content":{"videoRenderer":{"videoId":'
    response = requests.get(url).text
    index_videos = [match.start() + len(index_key) + 1 for match in re.finditer(index_key, response)]
    ids_list = list()
    
    for id_item in index_videos:
        ids_list.append(response[id_item:id_item+11])
    
    # Processa cada vídeo e busca pela passphrase
    for id in ids_list:
        if continue_code:
            url = "https://www.youtube.com/watch?v=" + id
            response = requests.get(url).text
            title_key_init = response.find('<meta name="title" content=') + 28
            title_key_finish = response.find('"><meta name=')
            title_video = response[title_key_init: title_key_finish]
            print('-'*101)
            print(f'Pesquisanto passPhrase no vídeo[{ids_list.index(id)}]: 📺 {title_video}')
            
            # Obtém e limpa a transcrição do vídeo
            transcription = get_transcription(id)
            transcription_clean = clean_string(transcription)
            list_transcription_clean = transcription_clean.split()  # Remove espaços extras
            possible_passphrases = check_string(list_transcription_clean, num_words, len_string)

            # Exibe as possíveis frases secretas
            print("\nPossíveis frases secretas encontradas:\n")
            for possible_passphrase in possible_passphrases:
                sha256_hash = hashlib.sha256(possible_passphrase.encode()).hexdigest()
                if possible_passphrase == 'transcricao:couldnotretrievea':
                    print(f'🚫 Video não está público e/ou Vídeo Inválido.')
                    break
                print(f' 🔍 {possible_passphrase} -> {sha256_hash}')
                if sha256_hash == target_hash:
                    print('*'*50)
                    print(f'\n🔑 Senha Encontrada: {possible_passphrase} 🎉')
                    print()
                    print('*'*50)
                    continue_code = False
                    break
        else:
            break

