# VisualGenius

VisualGenius is a Python-based project that integrates computer vision with hardware control. By leveraging gaze tracking and interfacing with FPGA and GPIO controllers, the project aims to create interactive applications that respond to user visual input. Although still in early stages, VisualGenius sets the groundwork for experiments and applications where computer vision meets real-time hardware interaction.

## Motivation

Recent research has highlighted that individuals on the autism spectrum can experience challenges with ocular coordination. Studies and articles on this subject suggest that subtle differences in eye movement patterns may affect communication and sensory integration. VisualGenius was inspired by these findings, aiming to explore how precise gaze tracking and adaptive hardware interfaces can assist in understanding and potentially supporting the development of ocular coordination in autistics. By providing a platform for integrating gaze tracking with hardware control, this project seeks to contribute to research and innovative applications that may benefit the autistic community.

## Features

- **Gaze Tracking:**  
  A dedicated module for tracking eye movements, which can be used to trigger hardware events or adapt on-screen content.
  
- **Hardware Interface:**  
  - **FPGA Control:** Uses `FPGAController.py` to communicate with FPGA devices.  
  - **GPIO Interface:** Provides methods in `IGPIOController.py` to manage general-purpose input/output for various hardware components.
  
- **Configurable Constants:**  
  Hardware-related constants and parameters are centralized in `dwfconstants.py` for easier configuration and tuning.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/jpbelga/VisualGenius.git
   cd VisualGenius
   python VisualGenius.py

--- 

# VisualGenius

VisualGenius é um projeto baseado em Python que integra visão computacional com controle de hardware. Utilizando rastreamento do olhar e interfaces com controladores FPGA e GPIO, o projeto tem como objetivo criar aplicações interativas que respondam ao input visual do usuário. Embora ainda esteja em estágio inicial, o VisualGenius estabelece as bases para experimentos e aplicações onde a visão computacional se alia à interação em tempo real com hardware.

## Motivação

Pesquisas recentes destacam que indivíduos no espectro autista podem apresentar desafios na coordenação ocular. Estudos e artigos sobre o tema sugerem que as sutis diferenças nos padrões de movimento dos olhos podem impactar a comunicação e a integração sensorial. O VisualGenius foi inspirado nesses achados, buscando explorar como o rastreamento preciso do olhar e interfaces de hardware adaptativas podem auxiliar na compreensão e, possivelmente, no desenvolvimento da coordenação ocular em autistas. Ao oferecer uma plataforma para integrar rastreamento ocular com controle de hardware, este projeto pretende contribuir para pesquisas e aplicações inovadoras que possam beneficiar a comunidade autista.

## Funcionalidades

- **Rastreamento do Olhar:**  
  Um módulo dedicado para rastreamento dos movimentos dos olhos, que pode ser utilizado para acionar eventos de hardware ou adaptar conteúdos exibidos.
  
- **Interface com Hardware:**  
  - **Controle FPGA:** Utiliza `FPGAController.py` para comunicação com dispositivos FPGA.  
  - **Interface GPIO:** Fornece métodos em `IGPIOController.py` para gerenciar entrada/saída de hardware.
  
- **Constantes Configuráveis:**  
  Parâmetros e constantes relacionados ao hardware são centralizados em `dwfconstants.py` para facilitar a configuração e o ajuste.

## Instalação

1. **Clone o Repositório:**

   ```bash
   git clone https://github.com/jpbelga/VisualGenius.git
   cd VisualGenius
   python VisualGenius.py
