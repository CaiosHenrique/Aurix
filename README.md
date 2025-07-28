# 🎮 Aurix Bot - League of Legends Discord Bot

Aurix é um bot Discord interativo desenvolvido em Python que permite aos usuários coletar, gerenciar e batalhar com campeões do League of Legends. O bot oferece um sistema completo de coleta de campeões, skins, batalhas e ranking.

## 📋 Funcionalidades

### 🏆 Sistema de Campeões
- **Coleta Aleatória**: Obtenha campeões aleatórios do League of Legends
- **Sistema de Salvamento**: Qualquer usuário pode salvar um campeão para si mesmo
- **Gerenciamento**: Visualize e delete seus campeões
- **Busca**: Encontre quem possui determinado campeão

### 🎨 Sistema de Skins
- **Coleta Aleatória**: Adquira skins aleatórias para seus campeões
- **Visualização**: Veja todas as skins que você possui
- **Troca de Skin**: Equipe diferentes skins nos seus campeões

### ⚔️ Sistema de Batalha
- **Batalhas PvP**: Desafie outros usuários para batalhas épicas
- **Sistema de HP**: Cada campeão possui 20 pontos de vida
- **Sistema de Aura**: Campeões podem ter diferentes níveis de aura que afetam o dano
- **Apostas**: O perdedor perde seus 5 primeiros campeões

### 📊 Sistema de Ranking
- **Ranking Global**: Veja quem tem mais vitórias
- **Sistema de Vitórias**: Campeões ganham vitórias após batalhas vencidas

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+**
- **discord.py** - Biblioteca para interação com Discord
- **Motor** - Driver assíncrono para MongoDB
- **MongoDB** - Banco de dados para armazenar dados dos campeões
- **Requests** - Para consumir a API do League of Legends
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 📦 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- MongoDB (local ou na nuvem)
- Conta Discord Developer com bot token
- Acesso à API do League of Legends (Riot Games)

### 1. Clone o repositório
```bash
git clone https://github.com/CaiosHenrique/Aurix.git
cd Aurix
```

### 2. Instale as dependências
```bash
pip install discord.py motor python-dotenv requests asyncio
```

### 3. Configure as variáveis de ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
DISCORD_TOKEN=seu_token_do_discord_bot
MONGO_URI=sua_string_de_conexao_mongodb
```

### 4. Execute o bot
```bash
python main.py
```

## 🎯 Comandos Disponíveis

### 📝 Comandos Básicos
- `!ping` - Verifica se o bot está online
- `!help` - Mostra todos os comandos disponíveis

### 🏆 Comandos de Campeões
- `!champ` - Gera um campeão aleatório com botão de salvamento
- `!mychamps` - Exibe seus campeões com navegação
- `!delete <nome>` - Remove um campeão específico
- `!search <nome>` - Busca quem possui determinado campeão

### 🎨 Comandos de Skins
- `!skin` - Adquire uma skin aleatória para um campeão aleatório
- `!skins <nome>` - Visualiza todas as skins de um campeão
- `!changeskin <nome>` - Permite escolher e equipar uma skin

### ⚔️ Comandos de Batalha
- `!battle <@usuário>` - Desafia outro usuário para batalha (requer 5+ campeões)
- `!rank` - Exibe o ranking de vitórias dos usuários

### 👑 Comandos de Admin
- `!setAura <nome> <nível>` - Define o nível de aura de um campeão (1-5)

## 🗃️ Estrutura do Banco de Dados

### Coleção: champions
```json
{
  "user_id": "ID_do_usuário_discord",
  "owner": "Nome_do_usuário",
  "name": "Nome_do_campeão",
  "image": "URL_da_imagem_do_campeão",
  "skin_image": "URL_da_skin_equipada (opcional)",
  "wins": "Número_de_vitórias",
  "aura_level": "Nível_de_aura (1-6)",
  "aura_label": "Label_da_aura",
  "owned_skins": [
    {
      "skin": "Nome_da_skin",
      "skin_image": "URL_da_skin"
    }
  ]
}
```

## 🎮 Como Jogar

### 1. Coletando Campeões
1. Use `!champ` para gerar um campeão aleatório
2. Clique no botão 💾 para salvar o campeão
3. Qualquer usuário pode salvar o campeão para si mesmo

### 2. Gerenciando Skins
1. Use `!skin` para obter skins aleatórias
2. Use `!skins <nome>` para ver suas skins
3. Use `!changeskin <nome>` para equipar uma skin diferente

### 3. Batalhas
1. Colete pelo menos 5 campeões
2. Desafie outro jogador com `!battle @usuário`
3. O desafiado deve aceitar a batalha clicando no botão
4. Assista à batalha automática por turnos
5. O vencedor mantém seus campeões, o perdedor perde os 5 primeiros

### 4. Sistema de Aura
- **Nível 1-5**: Afeta o dano nas batalhas
- **Nível 6**: "Aura Farming" para campeões com skins
- Maior aura = maior chance de causar mais dano

## 📁 Estrutura do Projeto

```
Aurix/
├── main.py              # Arquivo principal do bot
├── database.py          # Configuração do banco de dados
├── .env                 # Variáveis de ambiente (não versionado)
├── README.md           # Documentação do projeto
└── __pycache__/        # Cache do Python
```

## 🔧 Configuração Avançada

### Configuração do MongoDB
O bot utiliza MongoDB para armazenar dados dos campeões. Configure sua string de conexão no arquivo `.env`:
```env
MONGO_URI=mongodb://localhost:27017  # Para MongoDB local
# ou
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/  # Para MongoDB Atlas
```

### Configuração do Discord Bot
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma nova aplicação
3. Vá para "Bot" e crie um bot
4. Copie o token e adicione ao arquivo `.env`
5. Configure as permissões necessárias:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Attach Files
   - Read Message History

## 🐛 Solução de Problemas

### Erro de Conexão com MongoDB
- Verifique se o MongoDB está rodando
- Confirme se a string de conexão está correta
- Verifique permissões de rede/firewall

### Bot não responde
- Confirme se o token do Discord está correto
- Verifique se o bot tem permissões no servidor
- Confirme se as intents estão habilitadas

### Erro na API do League of Legends
- Verifique sua conexão com a internet
- A API do Riot Games pode estar temporariamente indisponível

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Desenvolvedores

- **CaiosHenrique** - Desenvolvedor Principal

## 🙏 Agradecimentos

- Riot Games pela API do League of Legends
- Comunidade Discord.py
- Contribuidores do projeto

---

**Nota**: Este projeto é independente e não é afiliado à Riot Games. League of Legends é uma marca registrada da Riot Games, Inc.
