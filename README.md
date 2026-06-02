# HandTrackduino

> Controle de uma mão robótica em tempo real através de Visão Computacional utilizando Python, MediaPipe, OpenCV e Arduino.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Arduino](https://img.shields.io/badge/Arduino-UNO-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange)
![Flask](https://img.shields.io/badge/Flask-Web%20Server-lightgrey)

## Sobre o Projeto

O HandTrackduino é um projeto de interação humano-robô que utiliza Visão Computacional para capturar os movimentos da mão de um usuário através de uma câmera e reproduzi-los em uma mão robótica acionada por servomotores controlados por Arduino.

O sistema combina processamento de imagens em tempo real, rastreamento de mãos, controle embarcado e uma interface web para configuração e monitoramento da solução.

Além do modo de espelhamento dos movimentos da mão humana, o sistema também possui um modo automático capaz de executar gestos pré-programados para demonstrações e testes.

## Objetivo

Desenvolver uma plataforma educacional e experimental de baixo custo para demonstrar conceitos de:

Visão Computacional
Inteligência Artificial aplicada à robótica
Interação Humano-Máquina (HMI)
Controle de atuadores
Sistemas embarcados
Integração Python + Arduino
Processamento de vídeo em tempo real

O projeto foi concebido para fins educacionais, prototipação e demonstrações tecnológicas.

## Arquitetura

Câmera → OpenCV → MediaPipe → Detecção de Dedos → Regras de Negócio → PyFirmata → Arduino → Servomotores → Mão Robótica


## Lógica de Funcionamento

O sistema utiliza o MediaPipe para identificar 21 pontos de referência (landmarks) da mão humana.

Com base na posição desses pontos, são calculadas distâncias e relações geométricas que permitem determinar quais dedos estão:

- Abertos
- Fechados

Após a interpretação do gesto:

1. O estado dos dedos é atualizado.
1. Apenas mudanças são enviadas ao Arduino.
1. O Arduino movimenta os servomotores correspondentes.
1. A mão robótica replica o gesto detectado.

Caso nenhuma mão seja detectada por um período definido, o sistema posiciona automaticamente a mão robótica em estado seguro (aberta).

## Tecnologias Utilizadas

### Backend
- Python
- Flask
- OpenCV
- MediaPipe
- CVZone
- PyFirmata

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap

### Hardware
- Arduino UNO R3
- 5 Servomotores
- Webcam USB
- Fonte de alimentação adequada para os servos
- Estrutura física da mão robótica
### Software
#### Python
Versão recomendada: Python 3.10

#### Arduino IDE
Versão recomendada: Arduino IDE 2.x

#### Firmware Arduino
- Utilizar OLD bootloader 
- Utilizar protocolo Firmata.

Instalar no Arduino:

Arquivo > Exemplos > Firmata > StandardFirmata

Enviar o sketch para a placa antes da primeira execução.

## Instalação

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU-USUARIO/HandTrackduino.git
cd HandTrackduino
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**Linux:**

```bash
source venv/bin/activate
```
### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

## Execução

```bash
python app.py
```

Acesse:

```text
http://localhost:5000
```

## Passo a Passo
1. Conectar Hardware
    - Conecte o Arduino ao computador
    - Conecte os servomotores
    - Conecte a webcam

2. Gravar o StandardFirmata

    Abra a Arduino IDE:

    Arquivo
        → Exemplos
        → Firmata
            → StandardFirmata

        Faça o upload para o Arduino.

3. Iniciar o Sistema
python app.py
4. Selecionar a Câmera

    Na interface web:

    Configurações → Selecionar Câmera

    Escolha a câmera desejada.

5. Selecionar Porta Arduino

    Na interface web:

    Configurações → Porta Arduino

    Selecione a porta serial correta.

6. Iniciar o Rastreamento

    Acesse:

    Modo Robótico

    Posicione a mão diante da câmera.

    A mão robótica começará a reproduzir os movimentos detectados.

## Principais Funcionalidades
###  Rastreamento de Mãos em Tempo Real
- Detecção da mão através da câmera
- Identificação dos dedos abertos e fechados
- Reconhecimento de gestos
### Controle da Mão Robótica
- Acionamento individual dos servomotores
- Espelhamento dos movimentos da mão do usuário
- Controle em tempo real
### Configuração Dinâmica
- Seleção de câmera via interface web
- Seleção automática da porta serial Arduino
- Gerenciamento centralizado de dispositivos
### Modo Automático

Execução automática de gestos pré-programados:

- Paz ✌️
- Rock 🤘
- Hang 🤙
- Aberta 🖐️
- Fechada ✊
- Apontar 👉
- Tchau 👋
### Lousa Virtual
- Desenho utilizando gestos
- Limpeza da tela através de gestos específicos

## Estrutura do Projeto

```text
HandTrackduino
│
├── app.py
│
├── routes/
│
├── services/
│   ├── cameras/
│   └── arduino/
│
├── src/
│   ├── robo/
│   └── desenho/
│
├── templates/
│
├── static/
│
└── requirements.txt
```

## Possíveis Evoluções
- Controle proporcional dos dedos
- Reconhecimento avançado de gestos via IA
- Suporte a múltiplas mãos
- Comunicação via ESP32
- Controle remoto pela internet
- Integração com ROS
- Treinamento de modelos personalizados

## Aplicações
- Ensino de robótica
- Ensino de visão computacional
- Prototipação rápida
- Pesquisa acadêmica
- Demonstrações tecnológicas
- Interação humano-robô

## Licença

Este projeto é disponibilizado para fins educacionais e de pesquisa.

Sinta-se à vontade para estudar, modificar e expandir a solução conforme sua necessidade.

⭐ Se este projeto foi útil para você, considere deixar uma estrela no repositório.
