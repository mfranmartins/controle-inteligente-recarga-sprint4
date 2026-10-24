# GoodWe Smart Charging Station

Projeto desenvolvido para a **Sprint 4 — Solução Final Integrada: GoodWe Smart Charging Station**, utilizando **Raspberry Pi Pico**, **MicroPython** e **Wokwi**.

O protótipo simula uma estação inteligente de recarga para veículos elétricos capaz de gerenciar a distribuição de energia disponível entre múltiplos veículos, considerando o nível de bateria, a potência solicitada e a disponibilidade energética do sistema.

## Objetivo

Desenvolver um protótipo funcional que demonstre:

* Leitura de dados por meio de entradas;
* Simulação de múltiplos veículos elétricos;
* Gerenciamento e distribuição inteligente de energia;
* Priorização de veículos com menor nível de bateria;
* Controle dos estados de recarga;
* Indicação visual por meio de LEDs RGB;
* Representação da energia disponível nos sistemas decimal, binário e hexadecimal;
* Aplicação de conceitos de **Arquitetura de Computadores**;
* Relação entre o protótipo e o gerenciamento inteligente de energia da GoodWe.

## Funcionamento

O sistema simula três veículos elétricos, cada um com seu próprio nível de bateria, demanda de potência e indicador luminoso.

Os potenciômetros são utilizados para simular o nível de bateria de cada veículo, com valores de 0% a 100%.

As demandas de potência e a energia disponível são configuradas pelo terminal serial.

Cada veículo possui as seguintes informações:

* **ID:** identificação do veículo;
* **Bateria:** nível de carga atual, em porcentagem;
* **Demanda:** potência solicitada para recarga, em watts;
* **Potência alocada:** potência efetivamente disponibilizada pelo sistema;
* **Estado:** situação atual da recarga.

O sistema considera a energia disponível e prioriza os veículos com menor nível de bateria. Em caso de empate, o veículo com menor demanda de potência tem prioridade.

Quando a bateria de um veículo atinge 100%, sua demanda é zerada e seu LED é desligado.

## Gerenciamento de energia

A distribuição de potência considera dois limites principais:

* **Energia disponível inferior a 2000 W:** somente o veículo prioritário pode receber energia;
* **Energia disponível igual ou superior a 2000 W:** a energia é distribuída entre os veículos por ordem de prioridade, respeitando a demanda de cada um e o limite total disponível.

O sistema utiliza uma potência mínima de alocação de 500 W. Caso não seja possível disponibilizar essa potência para um veículo, ele permanece em espera.

A distribuição respeita a seguinte condição:

```text
Soma das potências alocadas <= Energia disponível
```

Os limites foram definidos para fins de simulação do protótipo.

## Estados da recarga

| Condição | Estado | LED |
| --- | --- | --- |
| Potência alocada igual à demanda | Recarga total | Verde |
| Potência alocada entre 500 W e a demanda solicitada | Recarga reduzida | Amarelo |
| Veículo com demanda, mas sem potência suficiente | Em espera | Vermelho |
| Veículo sem demanda ou com bateria em 100% | Sem demanda | Desligado |

## Componentes

* Raspberry Pi Pico;
* 3 potenciômetros;
* 3 LEDs RGB;
* Protoboard;
* Jumpers para conexão dos componentes.

Os resistores limitadores de corrente devem ser utilizados em circuitos físicos para proteger os LEDs.

## Pinagem

| Componente | Pino do Raspberry Pi Pico |
| --- | --- |
| Potenciômetro — Bateria EV1 | GP26 / ADC0 |
| Potenciômetro — Bateria EV2 | GP27 / ADC1 |
| Potenciômetro — Bateria EV3 | GP28 / ADC2 |
| LED RGB EV1 — Vermelho | GP0 |
| LED RGB EV1 — Verde | GP1 |
| LED RGB EV1 — Azul | GP2 |
| LED RGB EV2 — Vermelho | GP3 |
| LED RGB EV2 — Verde | GP4 |
| LED RGB EV2 — Azul | GP5 |
| LED RGB EV3 — Vermelho | GP6 |
| LED RGB EV3 — Verde | GP7 |
| LED RGB EV3 — Azul | GP8 |

Os LEDs RGB utilizados na simulação possuem cátodo comum conectado ao GND. O canal azul está disponível na montagem, mas não é utilizado pelos estados atuais do sistema.

## Comandos seriais

O terminal serial permite configurar a demanda de cada veículo e a energia disponível para a estação.

| Comando | Função | Exemplo |
| --- | --- | --- |
| `1EV` + potência | Define a demanda do EV1 | `1EV2000` |
| `2EV` + potência | Define a demanda do EV2 | `2EV4000` |
| `3EV` + potência | Define a demanda do EV3 | `3EV1000` |
| `ENERGIA` + potência | Define a energia disponível | `ENERGIA5000` |

As potências devem estar entre 0 e 10000 W e ser múltiplos de 250 W.

Após o recebimento de um comando, o sistema recalcula a distribuição e atualiza o painel automaticamente.

## Cenários de teste

### Cenário 1 — Energia abundante

Com 10000 W disponíveis, o sistema consegue atender integralmente às demandas dos três veículos, desde que a soma das solicitações não ultrapasse esse limite.

### Cenário 2 — Energia limitada

Com 5000 W disponíveis e demanda total de 7000 W, o sistema prioriza o veículo com menor bateria e distribui a potência restante aos próximos veículos, conforme a ordem de prioridade.

### Cenário 3 — Baixa disponibilidade de energia

Com 1500 W disponíveis, somente o veículo prioritário pode receber energia. Os demais permanecem em espera até que exista disponibilidade suficiente.

Esses cenários demonstram como o sistema adapta a distribuição de potência às condições energéticas disponíveis.

## Sistemas numéricos

O sistema apresenta a energia disponível nos sistemas decimal, binário e hexadecimal.

Exemplo:

```text
Energia disponível: 5000 W
Decimal: 5000
Binário: 1001110001000
Hexadecimal: 1388
```

Essa representação demonstra como os valores utilizados pelo sistema podem ser representados em diferentes sistemas numéricos empregados na computação.

## Arquitetura de Computadores

O projeto relaciona as etapas de funcionamento do protótipo aos conceitos de Arquitetura de Computadores.

### Entrada

Os potenciômetros fornecem valores analógicos correspondentes aos níveis de bateria dos veículos. O ADC do Raspberry Pi Pico converte esses sinais em valores digitais. O terminal serial permite informar as demandas de potência e a energia disponível.

### Processamento

O processador executa:

1. Leitura dos níveis de bateria;
2. Recebimento e interpretação dos comandos seriais;
3. Ordenação dos veículos por prioridade;
4. Cálculo da potência que pode ser alocada a cada veículo;
5. Definição dos estados da recarga;
6. Atualização dos indicadores luminosos e do painel serial.

### Memória

Durante a execução, variáveis armazenam os níveis de bateria, as demandas, a energia disponível, as potências alocadas, os estados dos veículos e os dados utilizados no processamento dos comandos.

### Saída

Os resultados são apresentados por meio de:

* LEDs RGB, que indicam os estados de recarga;
* Terminal serial, que apresenta a energia disponível, os níveis de bateria, as demandas, as potências alocadas e os estados dos veículos.

### Fluxo do sistema

```text
Potenciômetros e Terminal Serial
              |
              v
       Leitura dos Dados
              |
              v
            Memória
              |
              v
     Processamento no Pico
              |
              v
   Priorização dos Veículos
              |
              v
    Distribuição de Energia
              |
              v
      Definição dos Estados
              |
        +-----+-----+
        |           |
        v           v
    LEDs RGB   Terminal Serial
```

## Relação com a GoodWe

O protótipo demonstra conceitos relacionados ao gerenciamento inteligente de energia e à distribuição controlada de potência em uma estação de recarga para veículos elétricos.

A solução simula um sistema capaz de avaliar a disponibilidade energética, considerar as necessidades dos veículos e ajustar a potência disponibilizada para evitar que a soma das potências alocadas ultrapasse o limite configurado.

Essa abordagem se relaciona conceitualmente ao **GoodWe Smart Energy Controller**, ao demonstrar a importância do monitoramento, da tomada de decisão automatizada e do uso eficiente dos recursos energéticos.

O projeto possui finalidade acadêmica e didática. A simulação não representa uma integração real com equipamentos ou plataformas GoodWe.

## Como executar

O projeto pode ser executado diretamente no Wokwi.

1. Abra o projeto no Wokwi: [Projeto da Sprint 4](https://wokwi.com/projects/478717315600952321).
2. Clique em "Start the simulation".
3. Ajuste os potenciômetros para modificar os níveis de bateria.
4. Utilize o terminal serial para configurar as demandas dos veículos.
5. Configure a energia disponível utilizando o comando `ENERGIA`.
6. Observe a distribuição de potência, os estados apresentados no terminal e as alterações dos LEDs RGB.

## Demonstração

Vídeo demonstrando o funcionamento do protótipo: [Vídeo no YouTube](https://youtu.be/t2TUaN0KwoI).

## Integrantes

* Ana Berbel - RM: 574176
* Gustavo Piccoli - RM: 569984
* Julian Moncoski - RM: 572603
* Marcelo Martins - RM: 573905
* Maria Medeiros - RM: 574094
* Pietro Lorande - RM: 569125

## Instituição e curso

**FIAP — Faculdade de Informática e Administração Paulista**

**Ciência da Computação**

Projeto desenvolvido para a **Sprint 4 — Solução Final Integrada: GoodWe Smart Charging Station**.
