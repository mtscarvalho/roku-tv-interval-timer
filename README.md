# Intervalo TV — timer para Roku

Canal Roku SceneGraph para treinos intervalados. O usuário define o tempo ativo, o intervalo e a quantidade de repetições usando apenas o controle remoto.

## Funcionalidades

- tempo ativo de 15 segundos a 60 minutos, ajustado em passos de 15 segundos;
- intervalo de 0 a 30 minutos, ajustado em passos de 15 segundos;
- 1 a 99 repetições;
- contagem sonora de 3 segundos antes de cada rodada;
- contagem regressiva em tamanho extra grande para visualização à distância;
- cronômetro ampliado e centralizado para leitura em TVs distantes;
- sinal sonoro ascendente e mais alto quando a rodada começa;
- alertas sonoros nos 3 segundos finais de cada fase;
- som distinto ao encerrar uma rodada;
- pausa com **OK** e cancelamento com **Voltar**;
- tela de conclusão com resumo do treino.
- identidade visual em grafite, preto, vermelho e branco;
- tipografia Poppins incorporada ao pacote sob a Open Font License.
- transição suave de cor e fundos com cantos arredondados nos controles.

## Gerar o pacote

Com Python 3, execute:

```bash
python3 tools/package.py
```

O arquivo para instalar na Roku será criado em `dist/intervalo-tv.zip`.

## Instalar em uma Roku para desenvolvimento

1. Ative o modo de desenvolvedor na Roku com a sequência: **Home ×3, Cima ×2, Direita, Esquerda, Direita, Esquerda, Direita**.
2. Anote o IP mostrado pela TV, aceite os termos e defina uma senha.
3. No computador, abra `http://IP-DA-ROKU` no navegador.
4. Envie `dist/intervalo-tv.zip` pela tela **Development Application Installer**.

## Controles

- **Cima/Baixo:** navegar entre opções;
- **Esquerda/Direita:** diminuir/aumentar valores;
- **OK:** iniciar ou pausar/continuar;
- **Voltar:** cancelar o treino e retornar à configuração.

Os ícones, imagens de abertura e o beep da contagem são gerados por `tools/generate_assets.py`, sem dependências externas. Os sons de início e conclusão são os arquivos `audio/start.wav` e `audio/complete.wav` incluídos no projeto.
