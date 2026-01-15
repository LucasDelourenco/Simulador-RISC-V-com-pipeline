Bem vindo(a)!
Esse programa se trata de um simulador para execução de programas RISC-V implementando os conceitos de pipeline

Preparando:
-Certifique-se de que você possui o Python e o pip do terminal instalados
-Baixe a biblioteca PyQt5:
 >Abra o seu terminal
 >Insira a seguinte linha: pip install PyQt5

Como usar o programa?
-Ao abrir o main.py com o Python, será aberta a interface
-Clique no botão "Selecionar Arquivo" no canto superior esquerdo da tela
-Selecione o arquivo de formato .bin ou .asm que deseja executar
-Clique em Iniciar e escolha o modo de inicialização (com ou sem forwarding)

Agora, ao clicar o botão "Próximo" um ciclo será avançado e as mudanças das instruções destacadas em verdes serão computadas, ou, caso queira ver o final da execução direto, simplesmente clique no botão "Finalizar".
Caso queira conferir o código do arquivo lido, alterne a aba atual clicando no marcador "Código do Arquivo" e, para voltar ao diagrama de execução, clique em "Simulação".

O projeto também conta com arquivos exemplos para visualizar o funcionamento do simulador (Pasta "Arquivos Teste"), além de uma apresentação sobre este funcionamento e ideias usadas para a criação desse programa.

OBS: Esse simulador não suporta função "la" nem "ecall"

Se divirta executando e analisando seus programas RISC-V em diagrama pipeline!


